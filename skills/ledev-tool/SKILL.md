---
name: ledev-tool
description: 不可用：该 skill 尚未完成开发和验证，不应被用于创建工具、脚本、生成器或项目自动化。请先使用 ledev-context 建立项目上下文，等待该 skill 正式开发后再启用。
---

# Tool Generator

> Status: unavailable
>
> 该 skill 尚未完成开发和验证。不要按本文档执行工具生成工作流；需要创建工具或脚本时，先使用 `ledev-context` 建立项目上下文，并按用户明确指令手动处理。

## Inputs

Read, when present:

- `.ai/project-context.md`
- `.ai/scope/scan-scope.md`
- `.ai/facts/related-repos.md`
- `.ai/state/ledev-tool.md`
- relevant `.ai/state/ledev-*.md` files when the tool supports another skill workflow
- language rules identified by `ledev-context`

If `ledev-context` declares `Primary repo` and `Related repos`, inherit that multi-repo context. Generated tools default to the primary repo write boundary; related repos can provide API/protocol/reference facts but must not be modified unless the user explicitly requests a cross-repo tool.

## 文件布局约定

- 运行规则、流程说明和背景材料放在 `references/`。
- 可复制或可实例化的文档、状态、报告、脚本输入输出样例模板放在 `templates/`。
- 新增模板时不要放进 `references/`；如果当前 skill 暂无模板，不需要创建空 `templates/` 目录。

## Workflow

1. Define the repeated job.
   - Identify inputs, outputs, side effects, and failure modes.
   - Prefer deterministic tools for repeated or fragile operations.
   - Keep one-off exploratory commands out of permanent scripts unless they become repeatable workflow.

2. Choose location and implementation language.
   - Match existing project conventions for tool directories and command wrappers.
   - Use the project language when it improves parsing, package awareness, distribution, or maintainability.
   - Use shell only for simple command orchestration.

3. Implement safely.
   - Support dry-run when the tool edits files or executes broad changes.
   - Print clear errors and exit non-zero on failure.
   - Avoid hidden network access unless explicitly required.
   - Do not overwrite user changes without an explicit flag or confirmation path.

4. Coordinate with context.
   - If the tool becomes part of normal workflow, update `.ai/project-context.md` or project docs with its command.
   - Record tool purpose, invocation, and output location.

5. Validate.
   - Add tests for parsing, planning, and generation logic where practical.
   - Run the tool against a small fixture or focused package first.
   - Run project formatting after generated output.

## Output

Report the tool location, invocation, validation run, and any limitations.
