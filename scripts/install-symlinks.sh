#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$DEST"

legacy_names=(
  project-context-builder
  dev-implementation
  dev-context
  dev-fix
  dev-impl
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
