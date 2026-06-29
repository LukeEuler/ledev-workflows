#!/usr/bin/env python3
"""Lint a LEDev task file before close."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]*):\s*(.*)$")
PLACEHOLDER_RE = re.compile(
    r"(待记录|待总结|待确认|待提出|待实现|待验证|待补充|\bTODO\b|\bTBD\b)",
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
    "Handoff / Next",
)

LIGHT_SECTIONS = (
    "User Request",
    "Requirement Summary",
    "Scope",
    "Plan",
    "Activity Log",
    "Validation Log",
    "Handoff / Next",
)

REQUIRED_FIELDS = ("Type", "Status", "Phase", "Created", "Updated")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint a .ai/tasks/T### task file.")
    parser.add_argument("task_file", help="Task markdown file to lint.")
    parser.add_argument(
        "--closing",
        action="store_true",
        help="Require implementation/activity and validation logs to be complete enough to close.",
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


def is_light(section_map: dict[str, str]) -> bool:
    return "Plan" in section_map and "Activity Log" in section_map and "Final Plan" not in section_map


def has_placeholder(value: str) -> bool:
    return bool(PLACEHOLDER_RE.search(value))


def meaningful(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if has_placeholder(stripped):
        return False
    if stripped in {"-", "- None.", "None.", "None", "not-applicable"}:
        return False
    return True


def main() -> int:
    args = parse_args()
    task_path = Path(args.task_file)
    text = read_text(task_path)
    problems: list[str] = []

    if not text.startswith("[返回任务索引](./index.md)"):
        problems.append("missing first-line index link")

    field_map = fields(text)
    for name in REQUIRED_FIELDS:
        value = field_map.get(name, "")
        if not value:
            problems.append(f"missing field: {name}")
        elif has_placeholder(value):
            problems.append(f"field still has placeholder: {name}")

    section_map = sections(text)
    required_sections = LIGHT_SECTIONS if is_light(section_map) else FULL_SECTIONS
    for name in required_sections:
        value = section_map.get(name)
        if value is None:
            problems.append(f"missing section: {name}")
        elif not value.strip():
            problems.append(f"empty section: {name}")

    if args.closing:
        validation = section_map.get("Validation Log", "")
        if not meaningful(validation):
            problems.append("Validation Log is not complete enough for close")

        activity_section = "Activity Log" if is_light(section_map) else "Implementation Log"
        activity = section_map.get(activity_section, "")
        if not meaningful(activity):
            problems.append(f"{activity_section} is not complete enough for close")

        plan_section = "Plan" if is_light(section_map) else "Final Plan"
        plan = section_map.get(plan_section, "")
        if not meaningful(plan):
            problems.append(f"{plan_section} is not complete enough for close")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    print(f"OK: {task_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
