#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/skills"
MARKER=".ledev-workflows-managed"

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

sync_directory() {
  local source="$1"
  local target="$2"
  local temporary

  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ ! -L "$target" ] && [ ! -f "$target/$MARKER" ]; then
      echo "Skipping unmanaged skill: $target" >&2
      return
    fi
    rm -rf "$target"
  fi

  temporary="${target}.tmp.$$"
  rm -rf "$temporary"
  cp -R "$source" "$temporary"
  : > "$temporary/$MARKER"
  mv "$temporary" "$target"
  echo "synced $target"
}

sync_destination() {
  local label="$1"
  local home="$2"
  local destination
  local skill
  local name
  local target

  if [ ! -d "$home" ]; then
    echo "Skipping $label: directory does not exist: $home"
    return
  fi

  destination="$home/skills"
  mkdir -p "$destination"
  echo "Syncing $label skills to $destination"

  for name in "${legacy_names[@]}"; do
    target="$destination/$name"
    if [ -L "$target" ]; then
      rm "$target"
      echo "removed legacy symlink $target"
    fi
  done

  sync_directory "$SOURCE/_shared" "$destination/_shared"

  for skill in "$SOURCE"/*; do
    [ -d "$skill" ] || continue
    [ -f "$skill/SKILL.md" ] || continue

    name="$(basename "$skill")"
    target="$destination/$name"

    if grep -Eq '^> Status: unavailable[[:space:]]*$' "$skill/SKILL.md"; then
      if [ -L "$target" ]; then
        rm "$target"
        echo "removed unavailable skill symlink $target"
      elif [ -f "$target/$MARKER" ]; then
        rm -rf "$target"
        echo "removed unavailable skill $target"
      elif [ -e "$target" ]; then
        echo "Skipping unavailable unmanaged skill: $target" >&2
      else
        echo "skipped unavailable skill $name"
      fi
      continue
    fi

    sync_directory "$skill" "$target"
  done
}

codex_home="${LEDEV_CODEX_HOME:-${CODEX_HOME:-$HOME/.codex}}"
claude_home="${LEDEV_CLAUDE_CODE_HOME:-${CLAUDE_CODE_HOME:-$HOME/.claude}}"

sync_destination "Codex" "$codex_home"
sync_destination "Claude Code" "$claude_home"
