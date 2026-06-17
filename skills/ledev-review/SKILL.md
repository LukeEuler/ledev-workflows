---
name: ledev-review
description: 不可用：该 skill 尚未完成开发和验证，不应被用于代码审阅、diff 审查或变更评估。请先使用 ledev-context 建立项目上下文，等待该 skill 正式开发后再启用。
---

# Code Review

> Status: unavailable
>
> 该 skill 尚未完成开发和验证。不要按本文档执行 review 工作流；需要代码审阅时，先使用 `ledev-context` 建立项目上下文，并按用户明确指令手动处理。

## Review Stance

Lead with findings. Focus on bugs, behavioral regressions, data loss, missing validation, missing tests, and risky contracts. Keep style comments secondary unless they cause real maintenance or correctness issues.

## Inputs

Read, when present:

- `.ai/project-context.md`
- `.ai/state/ledev-review.md`
- relevant `.ai/state/ledev-*.md` files when reviewing prior implementation, testing, or bugfix work
- language rules identified by `ledev-context`

## 文件布局约定

- 运行规则、流程说明和背景材料放在 `references/`。
- 可复制或可实例化的文档、状态、报告、脚本输入输出样例模板放在 `templates/`。
- 新增模板时不要放进 `references/`；如果当前 skill 暂无模板，不需要创建空 `templates/` 目录。

## Workflow

1. Establish diff and context.
   - Run `git status --short`.
   - Inspect diffs for changed files.
   - Read nearby code that defines the contract being changed.
   - Check `.ai/state/ledev-review.md` and relevant `.ai/state/ledev-*.md` files for known assumptions, blockers, and validation already run.

2. Check correctness.
   - Error handling: ignored errors, wrong wrapping, swallowed failures.
   - Data consistency: writes, idempotency, duplicate handling, ordering, checkpoints.
   - External APIs: pagination, retries, rate limits, nil/empty responses, edge cases.
   - Numeric handling: overflow, precision loss, decimal/string conversion.
   - Concurrency: shared mutable state, lifecycle, cancellation, channel/queue behavior.
   - Config: defaults, required fields, mode divergence, backward compatibility.

3. Check tests and validation.
   - Confirm changed behavior has focused tests or a clear reason coverage is impractical.
   - Verify validation claims against actual commands in logs or workflow state.
   - Identify the smallest useful missing validation.

4. Output format.
   - Findings first, ordered by severity.
   - Include file and line references.
   - Include open questions only when they affect correctness.
   - If no issues are found, say that and mention validation gaps.
