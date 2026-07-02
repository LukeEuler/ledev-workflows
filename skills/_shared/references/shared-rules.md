# LEDev 共享规则

这些规则适用于 `ledev-context`、`ledev-task`、`ledev-review` 以及后续 LEDev skill。各 skill 的专有 workflow 优先写在自身 `references/` 中；本文件只放跨 skill 一致性协议。

## 中文优先

- 面向中文用户时，对话、报告、任务记录、上下文和状态文件以中文为主。
- 命令、路径、代码符号、配置项、状态值、枚举值、文件名和短 token 保留英文。
- 需要用户输入的短确认 token 使用英文，例如 `yes/no`、`continue/stop`、`confirm/edit`、`not-applicable`。

## 操作入口

- LEDev skill 统一把 skill 名称后的第一个 token 视为操作入口（operation）。
- Codex 直接调用通常写作 `$ledev-task new ...`；Claude Code 直接调用写作 `/ledev-task new ...`。两者都把 skill 名称后的第一个 token 作为 operation。
- 操作入口大小写不敏感；面向用户展示命令时优先使用小写英文 token。
- 各 skill 可以保留领域别名：`ledev-context` 的 operation 可称为 mode，`ledev-task` 可称为 op/action，`ledev-review` 的 operation 之后通常跟 review range 或 commit。
- 不要因为 `.ai/state/` 中已有后续锚点而改写用户显式指定的 operation；本次运行必须服务于用户指定入口。

## 目标项目与自宿主豁免

- `.ai/` 产物默认写入被分析、开发、测试或审查的目标项目。
- 当前仓库是 workflow、skill、prompt、agent 配置或类似开发流程仓库，且用户正在维护这些工作流本身时，默认不创建目标项目 `.ai/` 运行产物。
- 用户明确要求 dry-run、no-write 或不落盘时，只在对话中说明本应写入的路径和内容摘要。

## Git 工作树检查

- 需要写入、审查或建立长期上下文前，优先运行 `git rev-parse --is-inside-work-tree` 判断目标路径是否在 git 工作树中。
- 需要读取当前文件状态时，运行 `git status --short` 或对应 skill 指定的只读预检脚本。
- dirty files 默认视为用户改动；除非能确认是本轮 agent 创建的文件，否则不要覆盖、清理或回滚。

## `.ai/` 与 `.gitignore`

- 运行进度统一写入 `.ai/state/<skill-name>.md`，不同 skill 不共用状态文件。
- 临时草稿、备份和恢复数据写入 `.ai/drafts/`；长期事实、任务、审查和 QA 写入各自子目录。
- 普通业务项目中，如 skill 会写入本地临时或运行产物，应确保对应路径被 `.gitignore` 覆盖；只追加缺失条目，不重排已有 `.gitignore`。
- 如果项目已有更宽泛规则覆盖目标路径，例如 `.ai/`，不重复追加。

## 路径可移植性

- 长期产物禁止写本机绝对路径，例如 `/Users/...`、`/home/...`、`C:\...`。
- 主仓库文件路径使用相对 `Primary repo` 根目录的路径。
- 关联仓库路径使用相对 `Primary repo` 的路径加仓库内路径，或稳定别名 `related:<repo>:<path>`。
- 本机绝对路径只允许进入 `.ai/drafts/local-paths.md` 或其他临时草稿，用于本轮路径映射、恢复或调试。

## 多仓库默认边界

- 多仓库上下文必须有且只有一个 `Primary repo`。
- `Related repos` 默认只读参考；除非用户明确切换目标或确认跨仓写入，不在关联仓库创建 `.ai/`、修改 `.gitignore` 或改业务文件。
- 如果关联仓库 checkout 与主仓库声明或实际解析版本不一致，必须记录风险；实现和验证判断优先依据主仓库实际解析版本。
