#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

check_absent() {
  local pattern="$1"
  shift
  if rg -n --hidden -S "$pattern" "$@"; then
    echo "ERROR: context isolation violation matched: $pattern" >&2
    fail=1
  fi
}

check_present() {
  local pattern="$1"
  local path="$2"
  if ! rg -q -S "$pattern" "$path"; then
    echo "ERROR: required context isolation rule missing from $path: $pattern" >&2
    fail=1
  fi
}

independent_skills=(
  skills/ledev-task
  skills/ledev-review
  skills/ledev-test
  skills/ledev-tool
)

check_absent '\$ledev-context' "${independent_skills[@]}"
check_absent 'Context Refresh' skills/ledev-task
check_absent '(先使用|建议.*使用|推荐.*运行|必须.*运行).*ledev-context' "${independent_skills[@]}"

check_present '仅在用户显式调用 ledev-context' skills/ledev-context/SKILL.md
check_present 'allow_implicit_invocation: false' skills/ledev-context/agents/openai.yaml
check_present 'Skill 独立运行与 context 隔离' skills/_shared/references/shared-rules.md
check_present '上述产物全部不存在时.*必须静默继续自身流程' skills/_shared/references/shared-rules.md

if [ "$fail" -ne 0 ]; then
  exit 1
fi

echo "OK: LEDev skills preserve context isolation"
