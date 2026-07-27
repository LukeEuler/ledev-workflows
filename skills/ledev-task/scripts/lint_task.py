#!/usr/bin/env python3
"""Lint a LEDev task file before close."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]*):\s*(.*)$")
TEMPLATE_MARKER_RE = re.compile(r"^<!--\s*ledev-task-template:\s*(full|light)\s*-->\s*$")
TASK_FILENAME_RE = re.compile(r"^(T\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
TASK_HEADING_RE = re.compile(r"^#\s+(T\d{3})\s+(.+?)\s+/\s+([A-Za-z][A-Za-z0-9 .:_/()'&+-]*?)\s*$")
PLACEHOLDER_RE = re.compile(
    r"(待记录|待总结|待确认|待提出|待实现|待验证|待补充|\bTODO\b|\bTBD\b)",
)
CONTEXT_REFRESH_COMMAND_RE = re.compile(
    r"Recommended command:\s*(not-required|\$ledev-context\s+(?:status|refresh|scope|document))\b",
)
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
PATH_TOKEN_RE = re.compile(
    r"(?<![\w./-])([A-Za-z0-9_.@+-]+(?:/[A-Za-z0-9_.@()+-]+)+)(?=$|[\s,;:)。；，])"
)

FULL_SECTIONS = (
    "User Request",
    "Requirement Summary",
    "Confirmed Requirements",
    "Open Questions",
    "Scope",
    "Impact",
    "Context Notes",
    "Solution Options",
    "Final Plan",
    "Decision Log",
    "Implementation Log",
    "Validation Log",
    "Context Refresh",
    "Handoff / Next",
)

LIGHT_SECTIONS = (
    "User Request",
    "Requirement Summary",
    "Scope",
    "Plan",
    "Activity Log",
    "Validation Log",
    "Context Refresh",
    "Handoff / Next",
)

REQUIRED_FIELDS = ("Type", "Status", "Phase", "Created", "Updated")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint a .ai/ledev/tasks/T### task file.")
    parser.add_argument("task_file", help="Task markdown file to lint.")
    parser.add_argument(
        "--closing",
        action="store_true",
        help="Require implementation/activity and validation logs to be complete enough to close.",
    )
    parser.add_argument(
        "--repo",
        help=(
            "Target project root for git diff reconciliation. Defaults to the "
            "project root inferred from .ai/ledev/tasks/<task-file>."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail --closing when git changed files are missing from the implementation log.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc


def sections(text: str) -> dict[str, str]:
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            found.setdefault(current, [])
            continue
        if current:
            found[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in found.items()}


def fields(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        match = FIELD_RE.match(line.strip())
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def template_kind(text: str) -> str | None:
    lines = text.splitlines()
    if len(lines) < 2:
        return None
    match = TEMPLATE_MARKER_RE.match(lines[1].strip())
    if not match:
        return None
    return match.group(1)


def task_heading(text: str) -> tuple[str, str, str] | None:
    for line in text.splitlines():
        if line.startswith("# "):
            match = TASK_HEADING_RE.match(line.strip())
            if match:
                return match.group(1), match.group(2).strip(), match.group(3).strip()
            return None
    return None


def has_placeholder(value: str) -> bool:
    return bool(PLACEHOLDER_RE.search(value))


def close_meaningful(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if has_placeholder(stripped):
        return False
    if stripped in {"-", "- None.", "None.", "None", "not-applicable"}:
        return False
    return True


def context_refresh_meaningful(value: str) -> bool:
    if not close_meaningful(value):
        return False
    return bool(CONTEXT_REFRESH_COMMAND_RE.search(value))


def infer_repo_root(task_path: Path) -> Path:
    resolved = task_path.resolve()
    parent = resolved.parent
    if (
        parent.name == "tasks"
        and parent.parent.name == "ledev"
        and parent.parent.parent.name == ".ai"
    ):
        return parent.parent.parent.parent
    return Path.cwd()


def git_output(repo_root: Path, args: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, ValueError):
        return 1, ""
    return result.returncode, result.stdout


def changed_files(repo_root: Path) -> tuple[set[str], str | None]:
    code, _ = git_output(repo_root, ["rev-parse", "--is-inside-work-tree"])
    if code != 0:
        return set(), f"skip git diff reconciliation: {repo_root} is not a git repository"

    changed: set[str] = set()
    for args in (["diff", "--name-only"], ["diff", "--name-only", "--cached"]):
        code, output = git_output(repo_root, args)
        if code != 0:
            return set(), "skip git diff reconciliation: git diff failed"
        changed.update(line.strip() for line in output.splitlines() if line.strip())

    code, output = git_output(repo_root, ["status", "--porcelain"])
    if code != 0:
        return set(), "skip git diff reconciliation: git status failed"
    for line in output.splitlines():
        if line.startswith("?? "):
            untracked = line[3:].strip()
            path = repo_root / untracked
            if untracked.endswith("/") and path.is_dir():
                changed.update(
                    child.relative_to(repo_root).as_posix()
                    for child in path.rglob("*")
                    if child.is_file()
                )
            else:
                changed.add(untracked)
    return {path for path in changed if not is_ledev_task_artifact(path)}, None


def is_ledev_task_artifact(path: str) -> bool:
    return (
        path.startswith(".ai/ledev/tasks/")
        or path == ".ai/ledev/state/ledev-task.md"
        or path.startswith(".ai/tasks/")
        or path == ".ai/state/ledev-task.md"
    )


def normalize_path_token(value: str) -> str | None:
    token = value.strip().strip(".,;:()[]{}<>，。；：")
    if token.startswith("./"):
        token = token[2:]
    if not token or token.startswith("$") or " " in token:
        return None
    if "/" not in token:
        return None
    return token


def implementation_paths(activity: str) -> set[str]:
    paths: set[str] = set()
    for match in BACKTICK_RE.finditer(activity):
        token = normalize_path_token(match.group(1))
        if token:
            paths.add(token)
    for match in PATH_TOKEN_RE.finditer(activity):
        token = normalize_path_token(match.group(1))
        if token and Path(token).suffix:
            paths.add(token)
    return paths


def diff_reconciliation_warnings(repo_root: Path, activity: str) -> tuple[list[str], list[str]]:
    changed, skip_reason = changed_files(repo_root)
    if skip_reason:
        return [f"WARN: {skip_reason}"], []
    recorded = implementation_paths(activity)
    changed_unmentioned = sorted(changed - recorded)
    recorded_unchanged = sorted(recorded - changed)
    warnings = [
        *(f"WARN: changed but not in Implementation Log: {path}" for path in changed_unmentioned),
        *(f"WARN: in Implementation Log but no git change: {path}" for path in recorded_unchanged),
    ]
    return warnings, changed_unmentioned


def main() -> int:
    args = parse_args()
    task_path = Path(args.task_file)
    text = read_text(task_path)
    problems: list[str] = []

    filename_match = TASK_FILENAME_RE.match(task_path.name)
    if not filename_match:
        problems.append("task filename must be T###-english-hyphen-title.md")

    if not text.startswith("[返回任务索引](./index.md)"):
        problems.append("missing first-line index link")

    kind = template_kind(text)
    if kind is None:
        problems.append("missing template marker: <!-- ledev-task-template: full|light -->")

    heading = task_heading(text)
    if heading is None:
        problems.append("task heading must be: # T### 中文任务标题 / English Task Title")
    elif filename_match and heading[0] != filename_match.group(1):
        problems.append("task heading id must match filename id")

    field_map = fields(text)
    for name in REQUIRED_FIELDS:
        value = field_map.get(name, "")
        if not value:
            problems.append(f"missing field: {name}")
        elif has_placeholder(value):
            problems.append(f"field still has placeholder: {name}")

    section_map = sections(text)
    required_sections = LIGHT_SECTIONS if kind == "light" else FULL_SECTIONS
    for name in required_sections:
        value = section_map.get(name)
        if value is None:
            problems.append(f"missing section: {name}")
        elif not value.strip():
            problems.append(f"empty section: {name}")

    if args.closing:
        validation = section_map.get("Validation Log", "")
        if not close_meaningful(validation):
            problems.append("Validation Log is not complete enough for close")

        activity_section = "Activity Log" if kind == "light" else "Implementation Log"
        activity = section_map.get(activity_section, "")
        if not close_meaningful(activity):
            problems.append(f"{activity_section} is not complete enough for close")

        plan_section = "Plan" if kind == "light" else "Final Plan"
        plan = section_map.get(plan_section, "")
        if not close_meaningful(plan):
            problems.append(f"{plan_section} is not complete enough for close")

        context_refresh = section_map.get("Context Refresh", "")
        if not context_refresh_meaningful(context_refresh):
            problems.append("Context Refresh must include a concrete recommended command for close")

        repo_root = Path(args.repo).resolve() if args.repo else infer_repo_root(task_path)
        warnings, changed_unmentioned = diff_reconciliation_warnings(repo_root, activity)
        for warning in warnings:
            print(warning, file=sys.stderr)
        if args.strict and changed_unmentioned:
            problems.append("Implementation Log does not mention all changed files")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    print(f"OK: {task_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
