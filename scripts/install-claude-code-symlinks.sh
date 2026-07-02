#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${CLAUDE_CODE_HOME:-$HOME/.claude}/skills"

mkdir -p "$DEST"

legacy_names=(
  project-context-builder
  dev-implementation
  dev-context
  dev-fix
  dev-impl
  ledev-fix
  ledev-impl
  dev-review
  dev-test
  dev-tool
  test-validation
  code-review
  bugfix-sop
  tool-generator
)

for name in "${legacy_names[@]}"; do
  target="$DEST/$name"
  if [ -L "$target" ]; then
    rm "$target"
    echo "removed legacy symlink $target"
  fi
done

for skill in "$ROOT"/skills/*; do
  [ -d "$skill" ] || continue
  [ -f "$skill/SKILL.md" ] || continue

  name="$(basename "$skill")"
  target="$DEST/$name"
  if [ -L "$target" ]; then
    rm "$target"
  elif [ -e "$target" ]; then
    echo "Refusing to replace existing non-symlink: $target" >&2
    exit 1
  fi
  ln -s "$skill" "$target"
  echo "linked $target -> $skill"
done
