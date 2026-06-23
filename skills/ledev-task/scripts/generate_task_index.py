#!/usr/bin/env python3
"""Generate .ai/tasks/index.md from T### task files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TASK_FILE_RE = re.compile(r"^(T[0-9]{3})-.+\.md$")
FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]*):\s*(.*)$")
KNOWN_STATUSES = ("todo", "in_progress", "blocked", "done", "obsolete")
STATUS_ICONS = {
    "todo": "⬜",
    "in_progress": "🔄",
    "blocked": "⛔",
    "done": "✅",
    "obsolete": "🗑️",
}


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    task_type: str
    status: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate .ai/tasks/index.md from .ai/tasks/T###-*.md files."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Target project root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated index without writing .ai/tasks/index.md.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if .ai/tasks/index.md is missing or stale.",
    )
    parser.add_argument(
        "--unfinished-report",
        action="store_true",
        help="Print task stats and unfinished tasks without writing files.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def field_value(lines: list[str], name: str, default: str) -> str:
    wanted = name.lower()
    for line in lines:
        match = FIELD_RE.match(line.strip())
        if match and match.group(1).lower() == wanted:
            value = match.group(2).strip()
            return value or default
    return default


def heading_title(lines: list[str], task_id: str, fallback: str) -> str:
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            if title.startswith(task_id):
                title = title[len(task_id) :].strip(" -:")
            return title or fallback
    return fallback


def fallback_title(path: Path, task_id: str) -> str:
    stem = path.stem
    prefix = f"{task_id}-"
    if stem.startswith(prefix):
        return stem[len(prefix) :].replace("-", " ")
    return stem


def parse_task(path: Path) -> Task | None:
    match = TASK_FILE_RE.match(path.name)
    if not match:
        return None

    task_id = match.group(1)
    lines = read_text(path).splitlines()
    return Task(
        task_id=task_id,
        title=heading_title(lines, task_id, fallback_title(path, task_id)),
        task_type=field_value(lines, "Type", "chore"),
        status=field_value(lines, "Status", "todo"),
        path=path,
    )


def link_target(path: Path) -> str:
    name = path.name.replace(" ", "%20")
    name = name.replace("(", "%28").replace(")", "%29")
    return f"./{name}"


def escape_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", r"\|")


def task_link(task: Task, text: str) -> str:
    return f"[{escape_cell(text)}]({link_target(task.path)})"


def status_icon(status: str) -> str:
    return STATUS_ICONS.get(status, "❔")


def status_counts(tasks: list[Task]) -> dict[str, int]:
    counts = {status: 0 for status in KNOWN_STATUSES}
    for task in tasks:
        counts.setdefault(task.status, 0)
        counts[task.status] += 1
    return counts


def render_index(tasks: list[Task]) -> str:
    counts = status_counts(tasks)
    sorted_tasks = sorted(tasks, key=lambda task: task.task_id)
    status_parts = [
        f"{status_icon(status)} `{status}` {counts.get(status, 0)}"
        for status in KNOWN_STATUSES
    ]
    status_parts.extend(
        f"{status_icon(status)} `{status}` {counts[status]}"
        for status in sorted(set(counts) - set(KNOWN_STATUSES))
    )

    lines: list[str] = [
        "# LEDev Tasks",
        "",
        f"- Total: {len(tasks)}",
        f"- Status: {' · '.join(status_parts)}",
    ]

    lines.extend(
        [
            "",
            "## Tasks",
            "",
            "| Task | Type | Title | Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for task in sorted_tasks:
        lines.append(
            "| "
            + " | ".join(
                [
                    task_link(task, task.task_id),
                    escape_cell(task.task_type),
                    task_link(task, task.title),
                    escape_cell(status_icon(task.status)),
                ]
            )
            + " |"
        )

    return "\n".join(lines) + "\n"


def render_unfinished_report(tasks: list[Task]) -> str:
    counts = status_counts(tasks)
    unfinished = [
        task for task in sorted(tasks, key=lambda item: item.task_id)
        if task.status not in {"done", "obsolete"}
    ]
    status_parts = [
        f"{status_icon(status)} `{status}` {counts.get(status, 0)}"
        for status in KNOWN_STATUSES
    ]
    status_parts.extend(
        f"{status_icon(status)} `{status}` {counts[status]}"
        for status in sorted(set(counts) - set(KNOWN_STATUSES))
    )

    lines = [
        f"- Total: {len(tasks)}",
        f"- Status: {' · '.join(status_parts)}",
        "",
        "## Unfinished",
        "",
    ]
    if not unfinished:
        lines.append("- None.")
    else:
        lines.extend(
            [
                "| Task | Type | Title | Status |",
                "| --- | --- | --- | --- |",
            ]
        )
        for task in unfinished:
            lines.append(
                "| "
                + " | ".join(
                    [
                        task_link(task, task.task_id),
                        escape_cell(task.task_type),
                        task_link(task, task.title),
                        escape_cell(status_icon(task.status)),
                    ]
                )
                + " |"
            )
    return "\n".join(lines) + "\n"


def load_tasks(tasks_dir: Path) -> list[Task]:
    if not tasks_dir.exists():
        return []
    tasks: list[Task] = []
    for path in sorted(tasks_dir.glob("T[0-9][0-9][0-9]-*.md")):
        task = parse_task(path)
        if task:
            tasks.append(task)
    return tasks


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    tasks_dir = project_root / ".ai" / "tasks"
    index_path = tasks_dir / "index.md"
    tasks = load_tasks(tasks_dir)

    if args.unfinished_report:
        sys.stdout.write(render_unfinished_report(tasks))
        return 0

    rendered = render_index(tasks)

    if args.dry_run:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not index_path.exists():
            print(f"missing: {index_path}", file=sys.stderr)
            return 1
        current = read_text(index_path)
        if current != rendered:
            print(f"stale: {index_path}", file=sys.stderr)
            return 1
        return 0

    tasks_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(rendered, encoding="utf-8")
    print(f"generated {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
