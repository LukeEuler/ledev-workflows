#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/skills"
MARKER=".ledev-workflows-managed"

trae_home="${LEDEV_TRAE_HOME:-$HOME/.trae-cn}"

if [ ! -d "$trae_home" ]; then
  echo "Skipping TRAE: product directory does not exist: $trae_home"
  exit 0
fi

destination="$trae_home/skills"
mkdir -p "$destination"
echo "Syncing TRAE skills to $destination"

synced=0
skipped=()

is_unavailable() {
  local file="$1"

  if grep -Eq '^> Status: unavailable[[:space:]]*$' "$file"; then
    return 0
  fi
  grep -Eq '^description:[[:space:]]*"?不可用' "$file"
}

sync_directory() {
  local source="$1"
  local target="$2"
  local temporary

  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ ! -L "$target" ] && [ ! -f "$target/$MARKER" ]; then
      echo "Skipping unmanaged skill: $target" >&2
      return 1
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

if [ -e "$destination/_shared" ] && [ ! -L "$destination/_shared" ] && [ ! -f "$destination/_shared/$MARKER" ]; then
  echo "Skipping unmanaged directory: $destination/_shared" >&2
else
  sync_directory "$SOURCE/_shared" "$destination/_shared"
fi

for skill in "$SOURCE"/*; do
  [ -d "$skill" ] || continue
  [ -f "$skill/SKILL.md" ] || continue

  name="$(basename "$skill")"
  target="$destination/$name"

  if is_unavailable "$skill/SKILL.md"; then
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
    skipped+=("$name")
    continue
  fi

  if sync_directory "$skill" "$target"; then
    synced=$((synced + 1))
  fi
done

echo "TRAE skills directory: $destination"
echo "Synced skills: $synced"
if [ "${#skipped[@]}" -gt 0 ]; then
  echo "Skipped unavailable skills: ${skipped[*]}"
else
  echo "Skipped unavailable skills: none"
fi
