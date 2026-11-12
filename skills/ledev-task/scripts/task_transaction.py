#!/usr/bin/env python3
"""Apply an agent-reviewed lifecycle file plan with optimistic checks and recovery.

Plan: {"files": [{"path": "repo/relative", "before": sha256_or_null,
                  "content": utf8_text_or_null}]}
Null before requires absence; null content deletes. Include move sources and targets.
All semantic assessment, metadata, attachment mapping and link edits belong in the plan.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

JOURNAL = ".ai/ledev/drafts/task-transaction.json"


def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def safe_path(root, relative):
    path = root / relative
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("paths must be relative to the project")
    if ".." in Path(relative).parts or ".git" in Path(relative).parts:
        raise ValueError(f"unsafe path: {relative}")
    if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError(f"symlink or escaping path: {relative}")
    return path


def read(path):
    return path.read_bytes() if path.exists() else None


def replace(path, data):
    if data is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    # Unique temporary file, same filesystem; never overwrite a user temp file.
    import tempfile
    fd, name = tempfile.mkstemp(prefix=".ledev-", dir=path.parent)
    try:
        if path.exists():
            os.fchmod(fd, path.stat().st_mode & 0o777)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def encode(data):
    return base64.b64encode(data).decode() if data is not None else None


def decode(data):
    return base64.b64decode(data) if data is not None else None


def recover(root, journal):
    record = json.loads(journal.read_text())
    # Validate the whole recovery before reverting any file; preserve later edits.
    for item in record["files"]:
        current = digest(read(safe_path(root, item["path"])))
        if current not in {item["before"], item["after"]}:
            raise ValueError(f"recovery conflict; preserve current edit: {item['path']}")
    for item in reversed(record["files"]):
        restored = safe_path(root, item["path"])
        replace(restored, decode(item["backup"]))
        if item.get("mode") is not None and restored.exists():
            restored.chmod(item["mode"])
    journal.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root")
    parser.add_argument("plan", nargs="?")
    parser.add_argument("--apply", action="store_true", help="Without this flag only preflight the plan")
    parser.add_argument("--recover", action="store_true")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    journal = safe_path(root, JOURNAL)
    if args.recover:
        if not journal.exists():
            raise ValueError("no interrupted transaction")
        recover(root, journal)
        print("recovered")
        return
    if journal.exists():
        raise ValueError("unfinished transaction; run --recover before writing")
    if not args.plan:
        raise ValueError("a reviewed plan is required")
    plan = json.loads(Path(args.plan).read_text())
    prepared = []
    modes = {}
    seen = set()
    for item in plan["files"]:
        relative = item["path"]
        if relative == JOURNAL:
            raise ValueError("plan cannot modify its journal")
        path = safe_path(root, relative)
        if path in seen:
            raise ValueError(f"duplicate plan path: {relative}")
        seen.add(path)
        mode = item.get("mode")
        if mode is not None and (not isinstance(mode, int) or not 0 <= mode <= 0o777):
            raise ValueError("mode must be an integer permission mask between 0 and 0777")
        modes[path] = mode
        before = read(path)
        if digest(before) != item["before"]:
            raise ValueError(f"concurrent change or target collision: {relative}")
        if "content_base64" in item:
            if "content" in item:
                raise ValueError("use either content or content_base64")
            after = base64.b64decode(item["content_base64"], validate=True)
        else:
            after = item["content"].encode("utf-8") if item["content"] is not None else None
        prepared.append((path, before, after, relative))
    if not args.apply:
        print(f"preflight OK: {len(prepared)} files; no writes")
        return
    journal.parent.mkdir(parents=True, exist_ok=True)
    record = {"files": [{"path": rel, "before": digest(before), "after": digest(after),
                         "backup": encode(before), "mode": (path.stat().st_mode & 0o777) if before is not None else None}
                         for path, before, after, rel in prepared]}
    # Exclusive creation serializes lifecycle writers; a partial journal needs manual inspection.
    with journal.open("x") as stream:
        json.dump(record, stream)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        # Recheck all inputs after acquiring the journal, before the first mutation.
        for path, before, _, relative in prepared:
            if read(path) != before:
                raise ValueError(f"concurrent change: {relative}")
        for path, before, after, relative in prepared:
            if read(path) != before:
                raise ValueError(f"concurrent change: {relative}")
            replace(path, after)
            if after is not None and modes[path] is not None:
                path.chmod(modes[path])
        for path, _, after, relative in prepared:
            if read(path) != after:
                raise ValueError(f"post-write mismatch: {relative}")
    except BaseException:
        recover(root, journal)
        raise
    journal.unlink()
    print(f"applied: {len(prepared)} files")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
