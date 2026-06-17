---
name: ledev-impl
description: 不可用：该 skill 尚未完成开发和验证，不应被用于实现代码变更、生成工具或修改项目文件。请先使用 ledev-context 建立项目上下文，等待该 skill 正式开发后再启用。
---

# Development Implementation

> Status: unavailable
>
> 该 skill 尚未完成开发和验证。不要按本文档执行实现工作流；需要实现代码变更时，先使用 `ledev-context` 建立项目上下文，并按用户明确指令手动处理。

## Inputs

Read, when present:

- `.ai/project-context.md`
- `.ai/state/ledev-impl.md`
- `.ai/state/ledev-context.md` when project context phase state is relevant
- language rules identified by `ledev-context`, such as `rules/go.md`

If project context is missing or stale for the task, run or recommend `ledev-context` first.

## 文件布局约定

- 运行规则、流程说明和背景材料放在 `references/`。
- 可复制或可实例化的文档、状态、报告、脚本输入输出样例模板放在 `templates/`。
- 新增模板时不要放进 `references/`；如果当前 skill 暂无模板，不需要创建空 `templates/` 目录。

## Workflow

1. Scope the change.
   - Identify the package, module, plugin, config, or service boundary involved.
   - Find 2-3 similar implementations in the repo.
   - Avoid changing unrelated packages or user-modified files.

2. Design with local patterns.
   - Match existing names, file layout, error handling, logging, config style, and public contracts.
   - Prefer existing helpers from shared packages.
   - Add new abstractions only when they reduce real duplication or clarify a shared contract.

3. Coordinate with other skills or agents.
   - Check `.ai/state/ledev-impl.md` for current phase, owner, touched files, open questions, and blocked items. Read other `.ai/state/ledev-*.md` files only when coordination requires it.
   - Update `.ai/state/ledev-impl.md` when a substantial implementation phase starts or finishes.
   - Do not overwrite another agent's stated work without explicit user direction.

4. Edit narrowly.
   - Use `apply_patch` for manual edits.
   - Keep comments sparse and useful.
   - Do not rewrite generated or vendored code unless the task explicitly targets it.

5. Format and verify.
   - Prefer the project's format command when available.
   - Run focused validation first, then broader validation when risk is cross-module.
   - If dependencies or external services block validation, report the exact blocker and command attempted.

## Output

Report:

- files changed
- important behavior changes
- commands run
- residual risk
