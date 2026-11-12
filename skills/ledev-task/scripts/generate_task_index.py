#!/usr/bin/env python3
"""Generate .ai/ledev/tasks/index.md from T### task files."""

from __future__ import annotations

import argparse
import os
from urllib.parse import quote
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


TASK_FILE_RE = re.compile(r"^(T[0-9]{3,})-.+\.md$")
TASK_ID_RE = re.compile(r"\bT([0-9]{3,})\b")
FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]*):\s*(.*)$")
KNOWN_STATUSES = (
    "todo",
    "in_progress",
    "awaiting_acceptance",
    "blocked",
    "done",
    "obsolete",
)
STATUS_ICONS = {
    "todo": "⬜",
    "in_progress": "🔄",
    "awaiting_acceptance": "🔵",
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
    completed: str = ""
    archived: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate .ai/ledev/tasks/index.md from .ai/ledev/tasks/T###-*.md files."
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
        help="Print generated index without writing .ai/ledev/tasks/index.md.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if .ai/ledev/tasks/index.md is missing or stale.",
    )
    parser.add_argument(
        "--unfinished-report",
        action="store_true",
        help="Print task stats and unfinished tasks without writing files.",
    )
    parser.add_argument(
        "--next-id",
        action="store_true",
        help=(
            "Print the next non-reused task id by scanning task files, index/state "
            "records, and git history when available."
        ),
    )
    parser.add_argument("--find", metavar="T###", help="Locate one active or archived task; fail on duplicate ids.")
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
        completed=field_value(lines, "Completed", ""),
        archived=field_value(lines, "Archived", ""),
    )


def link_target(path: Path, base: Path | None = None) -> str:
    return "./" + quote(os.path.relpath(path, base or path.parent), safe="/")


def escape_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", r"\|")


def task_link(task: Task, text: str, base: Path | None = None) -> str:
    return f"[{escape_cell(text)}]({link_target(task.path, base)})"


def status_icon(status: str) -> str:
    return STATUS_ICONS.get(status, "❔")


def status_counts(tasks: list[Task]) -> dict[str, int]:
    counts = {status: 0 for status in KNOWN_STATUSES}
    for task in tasks:
        counts.setdefault(task.status, 0)
        counts[task.status] += 1
    return counts


def task_sort_key(task: Task) -> tuple[int, str]:
    match = TASK_ID_RE.search(task.task_id)
    if not match:
        return (sys.maxsize, task.task_id)
    return (int(match.group(1)), task.task_id)


def archived_task(task: Task) -> bool:
    return task.path.parent.name != "tasks"


def render_index(tasks: list[Task], base: Path | None = None, archive: bool = False) -> str:
    selected = [t for t in tasks if archived_task(t) == archive]
    counts = status_counts(selected)
    base = base or (selected[0].path.parent if selected else Path("."))
    lines = ["# LEDev Archived Tasks" if archive else "# LEDev Tasks", "",
             f"- Total: {len(selected)}",
             "- Status: " + " · ".join(f"{status_icon(s)} `{s}` {counts[s]}" for s in counts)]
    if archive:
        lines += ["- [返回任务索引](../index.md)"]
        groups = [("Archived", sorted(selected, key=lambda t: (t.archived, task_sort_key(t))))]
    else:
        lines += [f"- Archived: {sum(archived_task(t) for t in tasks)} · [历史任务目录](./archive/index.md)"]
        ended = [t for t in selected if t.status in {"done", "obsolete"}]
        groups = [
            ("Unfinished", sorted([t for t in selected if t.status not in {"done", "obsolete", "awaiting_acceptance"}], key=task_sort_key)),
            ("Awaiting Acceptance", sorted([t for t in selected if t.status == "awaiting_acceptance"], key=task_sort_key)),
            ("Ended", sorted([t for t in ended if t.completed], key=lambda t: (t.completed, task_sort_key(t)))),
            ("Completion Date Unknown", sorted([t for t in ended if not t.completed], key=task_sort_key)),
        ]
    for title, group in groups:
        lines += ["", "## " + title, "", "| Task | Type | Title | Status | Completed | Archived |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for t in group:
            lines.append("| " + " | ".join([task_link(t, t.task_id, base), escape_cell(t.task_type),
                         escape_cell(t.title), status_icon(t.status), escape_cell(t.completed), escape_cell(t.archived)]) + " |")
    return "\n".join(lines) + "\n"


def render_unfinished_report(tasks: list[Task]) -> str:
    counts = status_counts(tasks)
    unfinished = [
        task for task in sorted(tasks, key=task_sort_key)
        if task.status not in {"awaiting_acceptance", "done", "obsolete"}
    ]
    awaiting = [
        task for task in sorted(tasks, key=task_sort_key)
        if task.status == "awaiting_acceptance"
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
                        escape_cell(task.title),
                        escape_cell(status_icon(task.status)),
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Awaiting Acceptance",
            "",
        ]
    )
    if not awaiting:
        lines.append("- None.")
    else:
        lines.extend(
            [
                "| Task | Type | Title | Status |",
                "| --- | --- | --- | --- |",
            ]
        )
        for task in awaiting:
            lines.append(
                "| "
                + " | ".join(
                    [
                        task_link(task, task.task_id),
                        escape_cell(task.task_type),
                        escape_cell(task.title),
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
    paths = list(tasks_dir.glob("T[0-9]*-*.md"))
    paths += list((tasks_dir / "archive").glob("[0-9][0-9][0-9][0-9]/T[0-9]*-*.md"))
    seen: dict[str, Path] = {}
    for path in sorted(paths):
        task = parse_task(path)
        if task:
            # Task bodies have a matching H1; similarly named attachments are not bodies.
            if not re.search(r"^# " + re.escape(task.task_id) + r"(?:\s|$)", read_text(path), re.M):
                continue
            if task.task_id in seen:
                raise ValueError(f"duplicate task {task.task_id}: {seen[task.task_id]} and {path}")
            seen[task.task_id] = path
            tasks.append(task)
    return tasks


def task_ids_from_text(text: str) -> set[int]:
    return {int(match.group(1)) for match in TASK_ID_RE.finditer(text)}


def task_ids_from_path(path: Path) -> set[int]:
    return task_ids_from_text(path.name)


def task_ids_from_existing_records(project_root: Path, tasks_dirs: list[Path]) -> set[int]:
    ids: set[int] = set()
    for tasks_dir in tasks_dirs:
        if not tasks_dir.exists():
            continue
        for path in tasks_dir.rglob("*"):
            ids.update(task_ids_from_path(path))
            if path.is_file() and path.suffix == ".md":
                try:
                    ids.update(task_ids_from_text(read_text(path)))
                except OSError:
                    pass

    state_paths = [
        project_root / ".ai" / "ledev" / "state" / "ledev-task.md",
        project_root / ".ai" / "state" / "ledev-task.md",
    ]
    for state_path in state_paths:
        if state_path.exists():
            try:
                ids.update(task_ids_from_text(read_text(state_path)))
            except OSError:
                pass

    return ids


def task_ids_from_git_history(project_root: Path) -> set[int]:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(project_root),
                "log",
                "--all",
                "--name-only",
                "--pretty=format:",
                "--",
                ".ai/ledev/tasks",
                ".ai/tasks",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, ValueError):
        return set()

    if result.returncode != 0:
        return set()
    return task_ids_from_text(result.stdout)


def next_task_id(project_root: Path, tasks_dir: Path) -> str:
    legacy_tasks_dir = project_root / ".ai" / "tasks"
    ids = task_ids_from_existing_records(project_root, [tasks_dir, legacy_tasks_dir])
    ids.update(task_ids_from_git_history(project_root))
    next_number = max(ids, default=0) + 1
    return f"T{next_number:03d}"


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    tasks_dir = project_root / ".ai" / "ledev" / "tasks"
    index_path = tasks_dir / "index.md"
    tasks = load_tasks(tasks_dir)
    if args.find:
        matches = [t for t in tasks if t.task_id == args.find.upper()]
        if not matches:
            print(f"task not found: {args.find}", file=sys.stderr)
            return 1
        print(matches[0].path.relative_to(project_root))
        return 0

    if args.next_id:
        print(next_task_id(project_root, tasks_dir))
        return 0

    if args.unfinished_report:
        sys.stdout.write(render_unfinished_report(tasks))
        return 0

    outputs = {index_path: render_index(tasks, tasks_dir),
               tasks_dir / "archive" / "index.md": render_index(tasks, tasks_dir / "archive", archive=True)}
    if args.dry_run:
        for path, rendered in outputs.items():
            print(f"<!-- {path.relative_to(project_root)} -->")
            sys.stdout.write(rendered)
        return 0
    if args.check:
        stale = [p for p, value in outputs.items() if not p.exists() or read_text(p) != value]
        for path in stale:
            print(f"missing or stale: {path}", file=sys.stderr)
        return int(bool(stale))
    if (project_root / ".ai/ledev/drafts/task-transaction.json").exists():
        raise ValueError("unfinished lifecycle transaction; recover before writing indexes")
    for path, rendered in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        print(f"generated {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
