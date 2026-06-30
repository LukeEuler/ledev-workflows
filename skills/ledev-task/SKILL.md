---
name: ledev-task
description: 面向中文用户。用于把代码开发、bug 修复、重构、小型工具生成和实现相关文档变更统一纳入编号 task 工作流。Use when Codex needs to create, continue, restart, implement, fix, or close typed development tasks before modifying project code, configs, tests, scripts, docs tied to implementation, or diagnosing bugs that may require code changes. 产物包括 .ai/tasks/ 下的 T### task 文件、.ai/tasks/index.md 状态索引和 .ai/state/ledev-task.md 运行状态；验证阶段可读取或交接给 ledev-test，但不替代独立测试治理。
---

# LEDev Task

## 目的

把每一次开发、修复和相关验证都绑定到可追踪 task，避免在没有上下文、需求确认、范围判断和验证记录的情况下直接改代码。

`ledev-task` 是开发和 bug 修复统一入口。`ledev-test` 暂时保持独立；本 skill 只规定任务内必须完成验证记录，复杂测试治理可交接给 `ledev-test`。

## 读取 Reference

- 跨 LEDev skill 的中文优先、git、`.ai/`、路径可移植性和多仓库默认边界：读 `../_shared/references/shared-rules.md`。
- task 字段、编号、索引和状态文件规则：读 `references/task-files.md`。
- 默认入口、新建、继续、重启、收尾等操作细节：读 `references/workflow.md`。
- 写文件时使用模板：
  - `templates/task-template.md`
  - `templates/task-light-template.md`
  - `templates/task-index-template.md`
  - `templates/ledev-task-state-template.md`
- 维护 task 索引时优先使用脚本：`scripts/generate_task_index.py`。
- close 前检查 task 完整性优先使用脚本：`scripts/lint_task.py --closing <task-file>`。

## 操作入口

遵循共享 operation 规则。`ledev-task` 的 operation 对外称为操作；把 skill 名称后的第一个词视为操作名。操作名大小写不敏感；中文和英文都支持。

- `default`：当用户只输入 `$ledev-task` 且没有其他参数时，读取 task 状态，展示任务统计和未完成任务，并询问用户下一步意图；默认不写文件，除非索引缺失或 stale 且用户允许刷新。
- `new` / `新建`：为新的开发、修复、重构或工具生成工作启动需求澄清、方案选择和最终确认流程；确认前只允许创建或更新 task 草案，不允许推进实现。
- `continue` / `继续`：读取现有 task，从上次阶段继续。
- `restart` / `重启`：需求不变但上一阶段实现或方案不适用时，保留历史并重启当前 task。
- `close` / `完成`：实现和验证结束后收尾，标记 task 为 `done`。
- `block` / `阻塞`：缺少用户决策、权限、依赖或外部条件时，标记 task 为 `blocked`。

示例：

- `$ledev-task`
- `$ledev-task new 实现导出 CSV`
- `$ledev-task continue T003`
- `$ledev-task restart T003`
- `$ledev-task close T003`

## 硬性规则

### 写入边界

- `.ai/tasks/` 和 `.ai/state/ledev-task.md` 是目标项目的运行产物，只在被开发、修复或验证的目标项目中创建。
- 当目标项目就是 `ledev-workflows` 这类 workflow/skill 仓库本身，或用户明确不希望落盘时，不创建目标项目 `.ai/`。用对话说明当前 task 语义、改动范围、验证结果，并依赖 git diff 保留变更证据。
- 如果不确定当前仓库是业务目标项目还是 workflow/skill 仓库，先根据目录结构和用户诉求判断；仍不确定时向用户确认再写 `.ai/`。

### 代码改动前

- 任何代码、配置、测试、脚本或实现相关文档改动前，必须确认当前改动属于某个 `T###` task；没有则先创建。
- 创建或继续 task 前，必须先检查目标项目是否在 git 工作树中，并读取 `git status --short`，识别用户已有改动。
- `new` 不等于立即实现。必须先让用户描述需求，或把操作名后已有文字作为原始需求；然后总结理解、列出模糊点、需求边界和待确认问题，等待用户补充。
- 需求澄清可以多轮进行。只要目标、成功标准、输入输出、范围边界、兼容性风险或验证方式仍不明确，就继续提问，不得为了推进而自行脑补进入实现。
- 需求初步明确后，必须观察代码架构和相关上下文，再给出解决方案。方案必须基于代码事实，而不是只基于抽象需求推断。
- 如果存在多个合理方案，必须列出各方案的差异、成本、风险、影响范围和验证方式，并让用户选择。
- 用户选择方案后，必须给出最终执行摘要，包括确认需求、明确不做范围、采用方案、预计修改位置、验证计划和剩余风险；收到用户明确确认（例如 `confirm`）后，才允许进入实现。
- 实现前必须观察代码架构和相关上下文。至少确认项目结构、技术栈、相关模块、相似实现、命令入口、测试方式和风险边界。
- 如果目标项目存在 `.ai/project-context.md`、`.ai/facts/` 或 `.ai/state/ledev-context.md`，必须优先读取。缺失、明显过期或任务影响面较大时，先运行或建议运行 `ledev-context`。
- 如果 `ledev-context` 事实层声明了 `Primary repo` 和 `Related repos`，必须继承多仓库上下文：读取 `.ai/scope/scan-scope.md`、`.ai/facts/related-repos.md`、`.ai/facts/dependencies.md`、`.ai/facts/boundaries.md` 和相关事实文件。
- task 写入边界默认只在 `Primary repo`。`Related repos` 默认只读参考；除非用户明确要求跨仓改动，否则不得修改关联仓库。
- 如果任务必须跨仓修改，先在 task 的 `Scope`、`Impact` 和 `Decision Log` 记录涉及的仓库、写入边界、版本关系、验证命令和用户确认。
- 如果关联仓库本地 checkout 与主仓库声明或实际解析版本不一致，task 中必须记录该风险；实现判断优先以实际解析版本为准，本地 checkout 只能作为参考，除非解析证据指向本地路径。
- 不允许把需求不清、影响面不明、方案取舍未定或最终方案未确认的工作直接推进到实现。先把疑问写入 task，并向用户确认。

### task 记录

- task 编号使用 `T###`，从 `T001` 开始递增；创建新 task 前必须先分配下一个编号，禁止凭空假定 `T001`。
- 新 task 编号必须取所有可见历史编号的最大值加一，历史来源至少包括 `.ai/tasks/` 文件名和内容、`.ai/tasks/index.md`、`.ai/state/ledev-task.md`，以及 git 历史中曾出现过的 `.ai/tasks/T###-*` 路径；不复用已删除、废弃、`obsolete`、重启过或当前不存在但有记录的编号。
- 允许写入目标项目 `.ai/` 时，优先用只读命令 `python3 <skill>/scripts/generate_task_index.py --next-id <target-project-root>` 获取新编号；命令不可用时，按上述历史来源手工扫描后再取最大值加一。
- 允许写入目标项目 `.ai/` 时，task 文件写入 `.ai/tasks/T###-english-short-title.md`；文件名短标题必须使用英文小写 hyphen-case，禁止使用中文、空格或过长描述；索引写入 `.ai/tasks/index.md`；运行状态写入 `.ai/state/ledev-task.md`。
- 每个 task 文件第一行必须写入返回索引链接：`[返回任务索引](./index.md)`，指向同目录下的 `.ai/tasks/index.md`。
- task 文件主标题必须明确写成 `# T### 中文任务标题 / English Task Title`；中文标题在前、英文标题在后，用 ` / ` 分隔。task 内容说明以中文为主。
- 每个 task 必须记录类型、当前阶段、用户原始诉求、需求理解、需求确认、开放问题、范围、影响面、方案选项、方案决策、最终确认、实现记录、验证结果、剩余风险和历史事件。
- 低风险 `chore`、`docs`、`tooling`、`config` task 可以使用 `templates/task-light-template.md`，但仍必须记录用户诉求、需求理解、范围、方案、实现活动、验证结果和后续事项。
- 每个 task 必须有 `Type`。优先使用 `feature`（开发）或 `bugfix`（修复 bug）；其他常见类型见 `references/task-files.md`。
- `restart` 不应删除历史。追加重启事件，说明为什么上一阶段不适用、保留哪些产物、废弃哪些假设。
- `.ai/tasks/index.md` 是状态汇总，不替代单个 task 详情。更新 task 状态后同步更新索引；索引优先由 `python3 <skill>/scripts/generate_task_index.py <target-project-root>` 生成，确保 Tasks 表格里的 task id 和 title 都链接到对应 task 文件。

### 实现与修复

- 开发和 bug 修复都走同一 task 工作流。
- bug 修复必须先记录复现方式、现象、初始假设和根因解释；无法复现时记录已尝试的证据和当前判断。
- 实现必须匹配仓库既有模式，优先复用现有 helper、命名、错误处理、配置和测试风格。
- 改动保持窄范围。不要顺手重构无关代码，不要覆盖用户已有改动。
- 手动编辑文件优先使用 `apply_patch`。

### 验证与收尾

- 每个 task 收尾前必须记录验证：命令、结果、失败原因或未验证原因。
- close 前优先运行 `scripts/lint_task.py --closing <task-file>`；若脚本不可用，按 `references/task-files.md` 手工检查必填字段、实现记录和验证记录。
- 低风险任务可运行聚焦验证；跨模块、共享契约或修复 bug 时，优先补充或运行回归测试。
- 测试策略复杂、用户明确要求测试治理，或需要独立验证阶段时，交接给 `ledev-test`，但 task 内仍要记录交接和结果。
- 只有实现、验证和收尾记录完整后，才把 task 标记为 `done`。
- 如果验证被权限、依赖、网络、外部服务或环境阻塞，记录具体命令和阻塞原因，状态设为 `blocked` 或保留为 `in_progress` 并说明风险。

## 默认输出

完成一次操作后报告：

- 当前 task 编号和状态。
- 本次完成的阶段和写入的 task 文件。
- 代码或文档变更摘要。
- 验证命令和结果。
- 剩余风险、阻塞项或建议下一步。
