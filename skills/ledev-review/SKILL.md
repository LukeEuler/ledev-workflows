---
name: ledev-review
description: 面向中文用户。用于对 Git 项目中已经 commit 的线性代码变更执行代码审阅，要求明确 base/head 或单 commit，拒绝未提交变更、非线性历史和 merge commit；结合用户意图、项目上下文、通用规则和语言规则输出 findings-first 的审查结论，并记录 review 范围、目标、达成情况、问题和验证缺口。
---

# LEDev Review

## 目的

`ledev-review` 专注做代码审阅：确认一段已提交、线性、无 merge commit 的 Git 变更是否达成用户意图，并识别 bug、行为回归、数据风险、契约风险、测试缺口和高价值维护问题。

不要用本 skill 整理分支、修改代码、补测试、处理未提交变更或治理复杂 Git 状态。遇到复杂输入时，要求用户先用 commit、stash、rebase、拆分任务或其他工具把问题简化。

## 读取 Reference

- 跨 LEDev skill 的中文优先、git、`.ai/`、路径可移植性和多仓库默认边界：读 `../_shared/references/shared-rules.md`。
- Git 范围、合法性检查和拒绝条件：读 `references/git-range.md`。
- findings 严重级别、证据和输出要求：读 `references/findings.md`。
- 用户意图识别和沟通规则：读 `references/intent.md`。
- 报告和状态记录规则：读 `references/report.md`。
- 通用审查规则：读 `rules/common.md`。
- 根据变更语言读取对应规则：
  - Go：读 `rules/golang.md`。
  - Java：读 `rules/java.md`。
  - JavaScript / TypeScript：读 `rules/javascript.md`。
  - Python：读 `rules/python.md`。
- 写报告或状态时使用：
  - `templates/review-report-template.md`
  - `templates/review-state-template.md`
- Git 范围预检优先使用脚本：`scripts/preflight.sh`。

## 输入边界

`ledev-review` 遵循共享 operation 规则。用户显式提供 `commit <B>` 时归一化为 single-commit；其他 `A..B`、`from A to B` 或 `base to head` 输入归一化为 committed-linear-range。

只接受以下 review 目标：

- `A..B`、`from A to B`、`branch base to branch head`：归一化为 committed linear range。
- `commit B`：归一化为 single commit review。

硬性拒绝：

- 工作区存在 staged、unstaged 或 untracked 变更。
- base 不是 head 的祖先。
- 范围为空。
- 范围内存在 merge commit。
- 单 commit 是 merge commit、root commit 或 parent 数量不是 1。
- revision 无法解析。
- 用户给出反向范围时，不自动调换。

## Workflow

1. 建立 Git 范围。
   - 读取 `references/git-range.md`。
   - 把用户输入解析成 `committed-linear-range` 或 `single-commit`。
   - 优先运行 `scripts/preflight.sh --json --range <base> <head>` 或 `scripts/preflight.sh --json --commit <commit>` 完成只读预检；需要人类可读输出时可省略 `--json`。
   - 如果脚本不可用，按 `references/git-range.md` 手工检查工作区干净、revision 存在、范围线性、无 merge commit、范围非空。
   - 将预检输出的 mode、base/head commit、diff expression、commit list、diff stat 和大范围 warning 用作报告范围元数据。
   - 失败时停止 review，给出最小修复命令提示。

2. 建立上下文和意图。
   - 普通项目中，先按 `references/report.md` 确保 `.ai/reviews/` 和 `.ai/state/ledev-review.md` 已加入 `.gitignore`；当前仓库是 workflow/skill 仓库或不落盘场景时跳过。
   - 读取 `.ai/project-context.md`、`.ai/scope/scan-scope.md`、`.ai/facts/`、`.ai/state/ledev-*.md` 和相关 task 文件，存在则优先使用。
   - 从用户说明、commit message、task、issue/PR 描述、测试变更和代码差异提取用户意图。
   - 如果无法判断变更目的，或目的与 diff 明显不一致，先向用户提问；不要臆测业务正确性。

3. 读取变更和相关代码。
   - 查看 `git log --reverse --oneline <range>` 理解提交演进。
   - 查看 `git diff --stat <range>` 和 `git diff <range>`。
   - 读取变更文件附近代码、调用方、被调用方、接口定义、配置、测试和迁移脚本。
   - 只读取与审查结论相关的上下文，避免把 review 扩展成泛化重构。

4. 应用规则。
   - 始终读取 `rules/common.md`。
   - 根据变更文件语言读取对应语言规则。
   - 多语言变更只读取实际涉及的语言规则。
   - 发现语言规则缺失时，使用通用规则并在报告中记录覆盖缺口。

5. 输出 findings-first 结论。
   - findings 按严重级别排序。
   - 每条 finding 必须包含位置、问题、影响、证据和建议。
   - 没有发现问题时明确说明，并列出仍未验证的风险或测试缺口。
   - 风格意见只在影响正确性、维护成本或一致性契约时提出。

6. 记录 review。
   - 写入或更新 `.ai/reviews/` 和 `.ai/state/ledev-review.md`，除非当前仓库是 workflow/skill 仓库或用户要求不落盘。
   - 记录 review 范围、用户意图、实际改造、达成情况、findings、验证情况、未确认问题和后续建议。

## 与其他 LEDev Skill 的关系

- `ledev-context`：review 前优先读取其事实层；上下文缺失且影响面较大时，建议先建立或刷新上下文。
- `ledev-task`：如果变更来自 task，读取 task 的目标、方案、实现记录、验证记录和 `Handoff / Next`，用于意图一致性检查与遗留事项识别。
- `ledev-test`：review 只指出测试缺口和建议验证，不接管独立测试治理。
- `ledev-review` 默认不改代码；用户明确要求修复 finding 时，转入开发/修复 task 工作流。
