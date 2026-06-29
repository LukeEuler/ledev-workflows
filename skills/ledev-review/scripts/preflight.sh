#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  preflight.sh --range <base> <head>
  preflight.sh --commit <commit>

Checks that a ledev-review target is committed, linear, non-empty, and clean.
USAGE
}

die() {
  printf 'ERROR: %s\n' "$1" >&2
  exit "${2:-1}"
}

git_required() {
  git "$@" 2>/dev/null
}

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

mode="$1"
shift

if [[ "$mode" == "-h" || "$mode" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

inside="$(git_required rev-parse --is-inside-work-tree || true)"
[[ "$inside" == "true" ]] || die "not inside a git work tree"

dirty="$(git status --porcelain)"
if [[ -n "$dirty" ]]; then
  printf 'ERROR: working tree is not clean\n' >&2
  printf '%s\n' "$dirty" >&2
  exit 10
fi

case "$mode" in
  --range)
    [[ $# -eq 2 ]] || die "--range requires <base> <head>" 2
    base_ref="$1"
    head_ref="$2"
    base_commit="$(git_required rev-parse --verify "${base_ref}^{commit}")" \
      || die "base ref does not resolve to a commit: ${base_ref}" 11
    head_commit="$(git_required rev-parse --verify "${head_ref}^{commit}")" \
      || die "head ref does not resolve to a commit: ${head_ref}" 12

    git merge-base --is-ancestor "$base_commit" "$head_commit" \
      || die "base is not an ancestor of head: ${base_ref}..${head_ref}" 13

    commits="$(git log --reverse --oneline "${base_commit}..${head_commit}")"
    [[ -n "$commits" ]] || die "range is empty: ${base_ref}..${head_ref}" 14

    merges="$(git rev-list --merges "${base_commit}..${head_commit}")"
    [[ -z "$merges" ]] || die "range contains merge commit(s): ${base_ref}..${head_ref}" 15

    commit_count="$(git rev-list --count "${base_commit}..${head_commit}")"
    diff_expression="${base_commit}..${head_commit}"

    printf 'Mode: committed-linear-range\n'
    printf 'Base ref: %s\n' "$base_ref"
    printf 'Base commit: %s\n' "$base_commit"
    printf 'Head ref: %s\n' "$head_ref"
    printf 'Head commit: %s\n' "$head_commit"
    printf 'Diff expression: %s\n' "$diff_expression"
    printf 'Commit count: %s\n' "$commit_count"
    printf 'Working tree clean: yes\n'
    printf 'Contains merge commit: no\n'
    printf '\nCommits:\n%s\n' "$commits"
    printf '\nDiff stat:\n'
    git diff --stat "$diff_expression"
    ;;

  --commit)
    [[ $# -eq 1 ]] || die "--commit requires <commit>" 2
    head_ref="$1"
    head_commit="$(git_required rev-parse --verify "${head_ref}^{commit}")" \
      || die "commit ref does not resolve to a commit: ${head_ref}" 11

    parents_line="$(git rev-list --parents -n 1 "$head_commit")"
    parent_count="$(( $(wc -w <<<"$parents_line") - 1 ))"
    [[ "$parent_count" -eq 1 ]] \
      || die "single commit target must have exactly one parent: ${head_ref}" 16

    base_commit="$(cut -d' ' -f2 <<<"$parents_line")"
    commits="$(git log --reverse --oneline "${base_commit}..${head_commit}")"
    commit_count="1"
    diff_expression="${base_commit}..${head_commit}"

    printf 'Mode: single-commit\n'
    printf 'Base ref: %s^\n' "$head_ref"
    printf 'Base commit: %s\n' "$base_commit"
    printf 'Head ref: %s\n' "$head_ref"
    printf 'Head commit: %s\n' "$head_commit"
    printf 'Diff expression: %s\n' "$diff_expression"
    printf 'Commit count: %s\n' "$commit_count"
    printf 'Working tree clean: yes\n'
    printf 'Contains merge commit: no\n'
    printf '\nCommits:\n%s\n' "$commits"
    printf '\nDiff stat:\n'
    git diff --stat "$diff_expression"
    ;;

  -h|--help)
    usage
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
