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
- 新 task 编号取 `.ai/tasks/` 中最大编号加一。
- 不复用已删除、废弃、obsolete 或重启过的编号。
- 文件名使用 `T###-短标题.md`。短标题用小写 hyphen-case 或中文短词均可，避免空格和过长描述。

## task 状态

task 状态使用稳定英文值，中文说明可以写在旁边：

- `todo`：已创建，尚未开始实现。
- `in_progress`：正在理解、设计、实现或验证。
- `blocked`：缺少用户决策、权限、依赖、环境或外部条件。
- `done`：实现、验证和收尾已完成。
- `obsolete`：任务不再适用，但编号和历史保留。

`restart` 是事件，不是长期状态。重启后通常回到 `in_progress`。

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

- `Task`：编号和标题。
- `Type`：task 主类型。
- `Status`：当前状态。
- `Created` 和 `Updated`：日期或时间戳。
- `User Request`：用户原始诉求，尽量保留原意。
- `Confirmed Requirements`：已确认需求。
- `Open Questions`：待确认问题。
- `Scope`：会改什么、不会改什么。
- `Impact`：影响面、风险边界、兼容性判断。
- `Context Notes`：代码架构观察、相关文件、相似实现、命令和测试入口。
- `Decision Log`：方案、取舍、用户确认和重启原因。
- `Implementation Log`：实际改动记录。
- `Validation Log`：命令、结果、失败或未执行原因。
- `Handoff / Next`：交接给 `ledev-test`、后续事项或阻塞项。

## 索引规则

`.ai/tasks/index.md` 汇总：

- task 总数。
- 各状态数量。
- 当前 `in_progress` task。
- `blocked` task 和阻塞原因。
- 最近完成的 task。
- task 列表：编号、类型、标题、状态、更新时间、摘要。

每次创建、改状态、重启或完成 task 后都要同步更新索引。

## 状态文件规则

`.ai/state/ledev-task.md` 只记录运行锚点，不替代 task 文件：

- 当前 active task。
- 当前阶段。
- 最近操作。
- touched files。
- open questions。
- validation status。

其他 skill 必须使用自己的 `.ai/state/<skill-name>.md`，不要共用 `ledev-task` 状态文件。
