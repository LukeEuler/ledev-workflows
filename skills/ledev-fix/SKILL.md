---
name: ledev-fix
description: 不可用：该 skill 尚未完成开发和验证，不应被用于诊断或修复 bug。请先使用 ledev-context 建立项目上下文，等待该 skill 正式开发后再启用。
---

# Bugfix SOP

> Status: unavailable
>
> 该 skill 尚未完成开发和验证。不要按本文档执行 bugfix 工作流；需要诊断或修复问题时，先使用 `ledev-context` 建立项目上下文，并按用户明确指令手动处理。

## Inputs

Read, when present:

- `.ai/project-context.md`
- `.ai/state/ledev-fix.md`
- `.ai/state/ledev-context.md` when project context phase state is relevant
- language rules identified by `ledev-context`

## 文件布局约定

- 运行规则、流程说明和背景材料放在 `references/`。
- 可复制或可实例化的文档、状态、报告、脚本输入输出样例模板放在 `templates/`。
- 新增模板时不要放进 `references/`；如果当前 skill 暂无模板，不需要创建空 `templates/` 目录。

## Workflow

1. Reproduce or characterize.
   - Capture the failing command, log, panic, bad output, data mismatch, or user-provided symptom.
   - If no reproduction exists, inspect likely paths and create a minimal focused test when practical.

2. Localize.
   - Trace from public entry point to failing package/module.
   - Search symbols with `rg`.
   - Compare with similar working packages or modules.
   - Record active hypothesis and touched files in `.ai/state/ledev-fix.md` when useful.

3. Explain the bug before patching.
   - Identify the broken assumption.
   - Identify affected inputs, module, config mode, or data shape.
   - Keep the explanation short and testable.

4. Patch narrowly.
   - Fix the cause, not only the observed symptom.
   - Preserve existing interfaces unless the bug is in the interface contract.
   - Add regression tests when the behavior is unit-testable.

5. Verify.
   - Run focused tests for the changed package/module.
   - Run broader tests when the fix touches shared code or contracts.
   - Update `.ai/state/ledev-fix.md` with commands and residual risk when present.

6. Report.
   - State root cause.
   - State files changed.
   - State tests run and remaining risk.
