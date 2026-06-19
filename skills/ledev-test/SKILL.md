---
name: ledev-test
description: 不可用：该 skill 尚未完成开发和验证，不应被用于测试、验证或构建检查任务。请先使用 ledev-context 建立项目上下文，等待该 skill 正式开发后再启用。
---

# Test Validation

> Status: unavailable
>
> 该 skill 尚未完成开发和验证。不要按本文档执行测试工作流；需要测试或验证时，先使用 `ledev-context` 建立项目上下文，并按用户明确指令手动处理。

## Inputs

Read, when present:

- `.ai/project-context.md`
- `.ai/scope/scan-scope.md`
- `.ai/facts/related-repos.md`
- `.ai/state/ledev-test.md`
- relevant `.ai/state/ledev-*.md` files when validating prior implementation or bugfix work
- language rules identified by `ledev-context`

If `ledev-context` declares `Primary repo` and `Related repos`, inherit that multi-repo context. Validation selection must use the primary repo's actual resolved dependency versions; related repos are read-only references unless the user explicitly asks for cross-repo validation or modification.

## 文件布局约定

- 运行规则、流程说明和背景材料放在 `references/`。
- 可复制或可实例化的文档、状态、报告、脚本输入输出样例模板放在 `templates/`。
- 新增模板时不要放进 `references/`；如果当前 skill 暂无模板，不需要创建空 `templates/` 目录。

## Workflow

1. Read context.
   - Check `git status --short` and identify changed files.
   - Determine whether changes are package-local, module-local, config-only, integration-heavy, or cross-cutting.
   - Respect generated/vendor/third-party exclusions recorded in project context.

2. Choose validation level.
   - Local change: run the smallest relevant package/module test.
   - Shared change: run direct tests plus obvious dependent tests.
   - Config or data change: inspect matching scripts and run only when local environment supports required services.
   - Cross-cutting change: run the project's full validation command.

3. Add or adjust tests when behavior changed.
   - Use nearby tests as style references.
   - Keep external network and service dependencies out of unit tests unless the repo already has a controlled pattern.
   - Prefer deterministic regression coverage for bug fixes.

4. Coordinate state.
   - Record commands, pass/fail status, blockers, and residual risk in `.ai/state/ledev-test.md` when present or useful.
   - Do not mark full validation complete if only focused validation ran.

5. Diagnose failures.
   - Separate compile/type errors, lint errors, deterministic test failures, flaky tests, and environment failures.
   - Fix code-caused failures when the task includes repair.
   - Report environment-caused failures with the exact missing tool, service, dependency, or command.

## Output

Report commands run, pass/fail status, and remaining validation gaps.
