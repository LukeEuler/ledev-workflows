# Task 文件规则

## 文件布局

在目标项目中使用：

```text
.ai/ledev/
  tasks/
    index.md
    T001-short-title.md
    T002-short-title.md
  state/
    ledev-task.md
```

如果目标项目不允许写文件，先说明将写入的路径，并按 dry-run 输出 task 草案。

不要在这些场景创建 `.ai/ledev/`：

- 当前仓库是 workflow、skill、prompt、agent 配置或类似开发流程仓库，用户正在修改这些工作流本身。
- 用户明确要求不写入 `.ai/ledev/`。
- 当前请求只是解释、讨论、评审或规划，不需要落地开发任务记录。

不落盘时仍要在对话中说明 task 语义、类型、范围、验证结果和剩余风险；以 git diff、命令输出和最终回复作为本次工作的记录。

## 编号规则

- 编号格式固定为 `T###`，例如 `T001`、`T023`。
- 创建新 task 前必须先分配编号，禁止因为 `.ai/ledev/tasks/index.md` 缺失、`.ai/ledev/tasks/` 目录不存在、当前未发现未完成任务或解析失败而直接使用 `T001`。
- 新 task 编号取所有可见历史编号的最大值加一；历史编号包括：
  - `.ai/ledev/tasks/` 下任意文件名中的 `T###`。
  - `.ai/ledev/tasks/` 下 Markdown 文件内容中的 `T###`。
  - `.ai/ledev/tasks/index.md` 中的 `T###` 链接或文本。
  - `.ai/ledev/state/ledev-task.md` 中的 active task、历史记录或 touched files。
  - git 历史中曾出现过的 `.ai/ledev/tasks/T###-*` 路径；如果目标项目不是 git 仓库或历史不可读，记录无法读取历史的事实。
- 迁移兼容：新 task 只写入 `.ai/ledev/tasks/`，但分配编号时必须同时扫描旧版 `.ai/tasks/`、`.ai/tasks/index.md`、`.ai/state/ledev-task.md` 和 git 历史中的 `.ai/tasks/T###-*`，避免从旧目录迁移后复用编号。
- 不复用已删除、废弃、`obsolete`、重启过、已完成或当前不存在但有记录的编号。
- 允许写入目标项目 `.ai/ledev/` 时，优先运行只读命令获取编号：

```sh
python3 <ledev-task-skill-dir>/scripts/generate_task_index.py --next-id <target-project-root>
```

- 如果脚本不可用，必须按上述历史来源手工扫描并取最大值加一；手工扫描结果要写入 task 的 `Decision Log` 或本次对话记录。
- 文件名使用 `T###-english-short-title.md`。短标题必须是英文小写 hyphen-case，例如 `export-csv`、`fix-login-timeout`；禁止使用中文、空格、下划线或过长描述。
- 每个 task 文件第一行必须提供返回索引的相对链接：`[返回任务索引](./index.md)`，方便从 task 详情跳回 `.ai/ledev/tasks/index.md`。
- 每个 task 文件第二行必须提供模板 marker：完整模板写 `<!-- ledev-task-template: full -->`，轻量模板写 `<!-- ledev-task-template: light -->`。
- task 文件主标题必须使用中文 / 英文双语格式：`# T### 中文任务标题 / English Task Title`。中文标题在前，英文标题在后，中间固定使用 ` / ` 分隔，例如 `# T001 更新任务索引链接 / Update Task Index Links`。
- task 文件中的说明性内容以中文为主；字段名、状态值、阶段值、类型值、命令、路径、代码符号、测试名称和短确认 token 可以保留英文。

## task 状态

task 状态使用稳定英文值，中文说明可以写在旁边：

- `todo`：已创建，尚未开始实现。
- `in_progress`：正在理解、设计、实现或验证。
- `awaiting_acceptance`：待验收；代码线交付完成，agent 能执行的验证已执行或已记录未执行原因，只剩人工、运行时或目标环境验收。
- `blocked`：缺少用户决策、权限、依赖、环境或外部条件。
- `done`：实现、验证和收尾已完成。
- `obsolete`：任务不再适用，但编号和历史保留。

`restart` 是事件，不是长期状态。重启后通常回到 `in_progress`。

状态边界：

- 只剩人工、运行时或目标环境验收时，用 `awaiting_acceptance`，不要继续挂 `in_progress`。
- 缺少外部条件、权限、依赖、用户决策或环境，导致 agent 无法继续推进时，用 `blocked`。
- 验证和必要验收已经跑通、记录完整后，才用 `done`。

## task 阶段

`Status` 表示任务整体状态，`Phase` 表示当前执行阶段。`Phase` 使用稳定英文值：

- `requirements_draft`：已记录原始诉求，正在总结需求和开放问题。
- `requirements_confirming`：正在等待用户补充或确认需求边界。
- `requirements_confirmed`：需求、范围和成功标准已初步明确，可以观察代码和设计方案。
- `context_reviewed`：已完成必要上下文观察，发现的代码事实已记录。
- `solution_options`：已列出一个或多个方案，等待用户选择或认可。
- `solution_confirmed`：用户已确认最终方案和验证计划，可以进入实现。
- `implementing`：正在实现或修复。
- `validating`：正在验证。
- `done`：实现、验证和收尾完成。
- `blocked`：缺少用户决策、权限、依赖、环境或外部条件。

`new` 创建的 task 通常从 `requirements_draft`、`requirements_confirming` 或 `requirements_confirmed` 开始；不得在最终方案确认前进入 `implementing`。

## task 类型

task 类型使用稳定英文值，中文说明可以写在旁边。`Type` 是必填字段；如果用户没有明确说明，先根据诉求和代码事实推断，不能可靠推断时写入 `Open Questions` 并向用户确认。

核心类型：

- `feature`：开发新功能、补齐能力、实现新模块或新流程。
- `bugfix`：复现、定位并修复错误行为、异常、回归或数据不一致。

常见扩展类型：

- `refactor`：不改变外部行为的结构调整、代码整理、模块拆分或接口内聚。
- `test`：新增、修复或重组测试；不以业务功能实现为主。
- `docs`：实现相关文档、skill 文档、开发说明或任务规范变更。
- `tooling`：脚本、CLI、代码生成器、开发工具或自动化流程。
- `config`：配置、构建、CI、lint、格式化、环境或部署参数调整。
- `dependency`：依赖新增、升级、替换、锁文件维护或兼容性处理。
- `performance`：性能、资源占用、缓存、并发或吞吐优化。
- `security`：权限、认证、授权、数据保护、漏洞修复或安全边界收紧。
- `migration`：数据迁移、API 迁移、框架迁移、目录迁移或兼容层处理。
- `research`：技术调研、方案验证、spike 或原型，不直接承诺生产实现。
- `chore`：维护性杂项，难以归入以上类型且影响面较小。

一个 task 只选择一个主类型。若任务横跨多类，选择驱动本次成功标准的类型，并在 `Impact` 或 `Decision Log` 中说明次要影响。

## task 模板选择

默认使用 `templates/task-template.md`。满足以下全部条件时，可以使用 `templates/task-light-template.md`：

- 类型是 `chore`、`docs`、`tooling`、`config` 或其他低风险维护类任务。
- 需求明确，影响面小。
- 不改变公共 API、数据格式、权限、安全边界、迁移逻辑或跨模块契约。
- 不需要多方案取舍或复杂回滚计划。

如果轻量 task 执行中发现影响面扩大、需求不清或存在高风险，必须切回完整模板结构，保留已有记录并补齐缺失字段。

## 完整 task 必填内容

使用完整模板时，task 文件必须包含：

- 第一行返回索引链接：`[返回任务索引](./index.md)`。
- 第二行模板 marker：`<!-- ledev-task-template: full -->`。
- `Task`：编号和标题。
- `Type`：task 主类型。
- `Status`：当前状态。
- `Phase`：当前阶段。
- `Created` 和 `Updated`：日期或时间戳。
- `User Request`：用户原始诉求，尽量保留原意。
- `Requirement Summary`：agent 对需求的当前理解，包括目标、交付物、成功标准和关键假设。
- `Confirmed Requirements`：已确认需求。
- `Open Questions`：待确认问题。
- `Scope`：会改什么、不会改什么。
- `Impact`：影响面、风险边界、兼容性判断。
- `Context Notes`：代码架构观察、相关文件、相似实现、命令和测试入口。
- `Solution Options`：可选方案、差异、成本、风险、验证方式；只有一个方案时记录采用理由。
- `Final Plan`：用户最终确认的需求、不做范围、采用方案、预计修改位置、验证计划和剩余风险。
- `Decision Log`：方案、取舍、用户确认和重启原因。
- `Implementation Log`：实际改动记录。
- `Validation Log`：命令、结果、失败或未执行原因。
- `Context Refresh`：本 task 对 `ledev-context` 的影响、刷新原因和推荐命令。
- `Handoff / Next`：交接给 `ledev-test`、后续事项或阻塞项。

## 轻量 task 必填内容

使用轻量模板时，task 文件必须包含：

- 第一行返回索引链接：`[返回任务索引](./index.md)`。
- 第二行模板 marker：`<!-- ledev-task-template: light -->`。
- `Task`：编号和标题。
- `Type`、`Status`、`Phase`、`Created`、`Updated`。
- `User Request`：用户原始诉求。
- `Requirement Summary`：目标、交付物、成功标准和关键假设。
- `Scope`：会改什么、不会改什么、风险等级和多仓库适用性。
- `Plan`：采用方案、预计修改位置、验证计划和剩余风险。
- `Activity Log`：需求确认、实现和重要决策的时间线。
- `Validation Log`：命令、结果、失败或未执行原因。
- `Context Refresh`：本 task 对 `ledev-context` 的影响、刷新原因和推荐命令。
- `Handoff / Next`：后续事项或阻塞项。

close 前优先运行：

```sh
python3 <ledev-task-skill-dir>/scripts/lint_task.py --closing <task-file>
```

脚本会检查缺失字段、实现/活动记录、验证记录、`Context Refresh`，并用 git unstaged、staged 和 untracked 改动对账 `Implementation Log` / `Activity Log`。默认对账不一致只打印 WARN；需要把“真实改动未记录”作为失败时，加 `--strict`；task 文件不在标准 `.ai/ledev/tasks/` 路径下时，加 `--repo <target-project-root>`。

脚本失败时不要标记 `done`，先补齐缺失字段、实现/活动记录或验证记录。

## Context Refresh 规则

每个 task 在实现或收尾时必须记录是否需要刷新 `ledev-context`。字段建议：

```md
## Context Refresh

- Context before task: current | stale | missing | unknown | not-checked
- Context-impacting changes: yes | no | unknown
- Reason:
- Recommended command: not-required | $ledev-context status | $ledev-context refresh | $ledev-context scope | $ledev-context document
```

推荐命令规则：

- `not-required`：未改代码、配置、测试、脚本、依赖、目录结构或架构事实；例如只更新 task 记录。
- `$ledev-context status`：task 期间发现用户或外部工具也改了文件，无法确认 context 是否仍然 current。
- `$ledev-context refresh`：修改了源码、入口、配置、依赖、测试命令、公共符号、路由/API、数据结构、架构边界或事实层会捕获的内容。
- `$ledev-context scope`：新增/删除顶层目录、模块边界、扫描排除项、关联仓库、workspace/replace/vendor 关系或其他会改变扫描范围的内容。
- `$ledev-context document`：事实层已经由本次或外部流程更新，但 Markdown/HTML 仍需重新生成。

如果不确定改动是否影响 context，写 `Context-impacting changes: unknown`，推荐 `$ledev-context status` 或 `$ledev-context refresh`，并在 `Reason` 中说明不确定来源。

## 索引规则

`.ai/ledev/tasks/index.md` 汇总：

- task 总数。
- 各状态数量。
- task 列表：编号、类型、标题、状态。
- `## Tasks` 表格中，`Task` 列的 task id 必须链接到对应 task 文件，例如 `[T001](./T001-export-csv.md)`。
- `## Tasks` 表格中，`Title` 列的标题也必须链接到同一个 task 文件，例如 `[导出 CSV / Export CSV](./T001-export-csv.md)`。
- `## Tasks` 表格中的 `Status` 列使用常见彩色状态图标展示；状态统计区必须保留“图标 + 原始状态值”的映射，方便识别。
- 默认状态图标：`⬜` = `todo`，`🔄` = `in_progress`，`🔵` = `awaiting_acceptance`，`⛔` = `blocked`，`✅` = `done`，`🗑️` = `obsolete`。
- 状态图标必须是纯文本图标，不使用 HTML 标签或内联样式。
- task 文件路径使用相对 `index.md` 的链接，优先使用 `./T###-english-short-title.md`；链接目标必须和实际英文文件名一致。

每次创建、改状态、重启或完成 task 后都要同步更新索引。优先运行：

```sh
python3 <ledev-task-skill-dir>/scripts/generate_task_index.py <target-project-root>
```

脚本从 `<target-project-root>/.ai/ledev/tasks/T###-*.md` 读取 task 文件，重建 `<target-project-root>/.ai/ledev/tasks/index.md`，并自动生成 task id 和 title 链接。

如果脚本不可用，才手工维护索引；手工维护时必须保持统计和 Tasks 表格一致。

## 状态文件规则

`.ai/ledev/state/ledev-task.md` 只记录运行锚点，不替代 task 文件：

- 当前 active task。
- 当前阶段。阶段值使用 task 阶段规则。
- 最近操作。
- touched files。
- open questions。
- validation status。
- context refresh status：`Context before task`、`Context-impacting changes`、推荐的 `ledev-context` 命令和原因。

其他 skill 必须使用自己的 `.ai/ledev/state/<skill-name>.md`，不要共用 `ledev-task` 状态文件。
