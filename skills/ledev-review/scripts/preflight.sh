#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  preflight.sh [--json] --range <base> <head>
  preflight.sh [--json] --commit <commit>

Checks that a ledev-review target is committed, linear, non-empty, and clean.
USAGE
}

die() {
  printf 'ERROR: %s\n' "$1" >&2
  exit "${2:-1}"
}

git_required() {
  git "$@"
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\t'/\\t}"
  printf '"%s"' "$value"
}

json_array_from_lines() {
  local lines="$1"
  local first=1

  printf '['
  if [[ -n "$lines" ]]; then
    while IFS= read -r line; do
      if [[ "$first" -eq 0 ]]; then
        printf ','
      fi
      json_escape "$line"
      first=0
    done <<<"$lines"
  fi
  printf ']'
}

changed_line_count() {
  local diff_expression="$1"
  local added deleted total

  total=0
  while IFS=$'\t' read -r added deleted _path; do
    [[ "$added" =~ ^[0-9]+$ ]] || added=0
    [[ "$deleted" =~ ^[0-9]+$ ]] || deleted=0
    total=$((total + added + deleted))
  done < <(git diff --numstat "$diff_expression")
  printf '%s\n' "$total"
}

warn_large_range() {
  local commit_count="$1"
  local diff_expression="$2"
  local changed_lines

  changed_lines="$(changed_line_count "$diff_expression")"
  if [[ "$commit_count" -ge 30 || "$changed_lines" -ge 1000 ]]; then
    printf 'WARNING: review range is large (%s commit(s), %s changed line(s)); consider splitting the review.\n' \
      "$commit_count" "$changed_lines" >&2
  fi
}

print_result_text() {
  printf 'Mode: %s\n' "$result_mode"
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
}

print_result_json() {
  local diff_stat

  diff_stat="$(git diff --stat "$diff_expression")"
  printf '{'
  printf '"mode":'; json_escape "$result_mode"; printf ','
  printf '"baseRef":'; json_escape "$base_ref"; printf ','
  printf '"baseCommit":'; json_escape "$base_commit"; printf ','
  printf '"headRef":'; json_escape "$head_ref"; printf ','
  printf '"headCommit":'; json_escape "$head_commit"; printf ','
  printf '"diffExpression":'; json_escape "$diff_expression"; printf ','
  printf '"commitCount":%s,' "$commit_count"
  printf '"workingTreeClean":true,'
  printf '"containsMergeCommit":false,'
  printf '"commits":'; json_array_from_lines "$commits"; printf ','
  printf '"diffStat":'; json_array_from_lines "$diff_stat"
  printf '}\n'
}

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

json_output=0
if [[ "${1:-}" == "--json" ]]; then
  json_output=1
  shift
fi

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
    result_mode="committed-linear-range"

    warn_large_range "$commit_count" "$diff_expression"
    if [[ "$json_output" -eq 1 ]]; then
      print_result_json
    else
      print_result_text
    fi
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
    result_mode="single-commit"

    base_ref="${head_ref}^"
    warn_large_range "$commit_count" "$diff_expression"
    if [[ "$json_output" -eq 1 ]]; then
      print_result_json
    else
      print_result_text
    fi
    ;;

  -h|--help)
    usage
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
