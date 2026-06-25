# Task 文件规则

## 文件布局

在目标项目中使用：

```text
.ai/
  tasks/
    index.md
    T001-short-title.md
    T002-short-title.md
  state/
    ledev-task.md
```

如果目标项目不允许写文件，先说明将写入的路径，并按 dry-run 输出 task 草案。

不要在这些场景创建 `.ai/`：

- 当前仓库是 workflow、skill、prompt、agent 配置或类似开发流程仓库，用户正在修改这些工作流本身。
- 用户明确要求不写入 `.ai/`。
- 当前请求只是解释、讨论、评审或规划，不需要落地开发任务记录。

不落盘时仍要在对话中说明 task 语义、类型、范围、验证结果和剩余风险；以 git diff、命令输出和最终回复作为本次工作的记录。

## 编号规则

- 编号格式固定为 `T###`，例如 `T001`、`T023`。
- 创建新 task 前必须先分配编号，禁止因为 `.ai/tasks/index.md` 缺失、`.ai/tasks/` 目录不存在、当前未发现未完成任务或解析失败而直接使用 `T001`。
- 新 task 编号取所有可见历史编号的最大值加一；历史编号包括：
  - `.ai/tasks/` 下任意文件名中的 `T###`。
  - `.ai/tasks/` 下 Markdown 文件内容中的 `T###`。
  - `.ai/tasks/index.md` 中的 `T###` 链接或文本。
  - `.ai/state/ledev-task.md` 中的 active task、历史记录或 touched files。
  - git 历史中曾出现过的 `.ai/tasks/T###-*` 路径；如果目标项目不是 git 仓库或历史不可读，记录无法读取历史的事实。
- 不复用已删除、废弃、`obsolete`、重启过、已完成或当前不存在但有记录的编号。
- 允许写入目标项目 `.ai/` 时，优先运行只读命令获取编号：

```sh
python3 <ledev-task-skill-dir>/scripts/generate_task_index.py --next-id <target-project-root>
```

- 如果脚本不可用，必须按上述历史来源手工扫描并取最大值加一；手工扫描结果要写入 task 的 `Decision Log` 或本次对话记录。
- 文件名使用 `T###-短标题.md`。短标题用小写 hyphen-case 或中文短词均可，避免空格和过长描述。
- 每个 task 文件第一行必须提供返回索引的相对链接：`[返回任务索引](./index.md)`，方便从 task 详情跳回 `.ai/tasks/index.md`。
- task 标题优先中文；需要保留英文模块名、概念或检索关键词时，可以使用中文为主、英文为辅的双语标题，例如 `更新任务索引链接 / Link Task Index`。
- task 文件中的说明性内容以中文为主；字段名、状态值、阶段值、类型值、命令、路径、代码符号、测试名称和短确认 token 可以保留英文。

## task 状态

task 状态使用稳定英文值，中文说明可以写在旁边：

- `todo`：已创建，尚未开始实现。
- `in_progress`：正在理解、设计、实现或验证。
- `blocked`：缺少用户决策、权限、依赖、环境或外部条件。
- `done`：实现、验证和收尾已完成。
- `obsolete`：任务不再适用，但编号和历史保留。

`restart` 是事件，不是长期状态。重启后通常回到 `in_progress`。

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

## task 必填内容

每个 task 文件必须包含：

- 第一行返回索引链接：`[返回任务索引](./index.md)`。
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
- `Handoff / Next`：交接给 `ledev-test`、后续事项或阻塞项。

## 索引规则

`.ai/tasks/index.md` 汇总：

- task 总数。
- 各状态数量。
- task 列表：编号、类型、标题、状态。
- `## Tasks` 表格中，`Task` 列的 task id 必须链接到对应 task 文件，例如 `[T001](./T001-导出CSV.md)`。
- `## Tasks` 表格中，`Title` 列的标题也必须链接到同一个 task 文件，例如 `[导出 CSV](./T001-导出CSV.md)`。
- `## Tasks` 表格中的 `Status` 列使用常见彩色状态图标展示；状态统计区必须保留“图标 + 原始状态值”的映射，方便识别。
- 默认状态图标：`⬜` = `todo`，`🔄` = `in_progress`，`⛔` = `blocked`，`✅` = `done`，`🗑️` = `obsolete`。
- 状态图标必须是纯文本图标，不使用 HTML 标签或内联样式。
- task 文件路径使用相对 `index.md` 的链接，优先使用 `./T###-短标题.md`；链接目标必须和实际文件名一致。

每次创建、改状态、重启或完成 task 后都要同步更新索引。优先运行：

```sh
python3 <ledev-task-skill-dir>/scripts/generate_task_index.py <target-project-root>
```

脚本从 `<target-project-root>/.ai/tasks/T###-*.md` 读取 task 文件，重建 `<target-project-root>/.ai/tasks/index.md`，并自动生成 task id 和 title 链接。

如果脚本不可用，才手工维护索引；手工维护时必须保持统计和 Tasks 表格一致。

## 状态文件规则

`.ai/state/ledev-task.md` 只记录运行锚点，不替代 task 文件：

- 当前 active task。
- 当前阶段。阶段值使用 task 阶段规则。
- 最近操作。
- touched files。
- open questions。
- validation status。

其他 skill 必须使用自己的 `.ai/state/<skill-name>.md`，不要共用 `ledev-task` 状态文件。
