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
- 不要因为 `.ai/ledev/state/` 中已有后续锚点而改写用户显式指定的 operation；本次运行必须服务于用户指定入口。

## 目标项目与自宿主豁免

- `.ai/ledev/` 产物默认写入被分析、开发、测试或审查的目标项目。
- 当前仓库是 workflow、skill、prompt、agent 配置或类似开发流程仓库，且用户正在维护这些工作流本身时，默认不创建目标项目 `.ai/ledev/` 运行产物。
- 用户明确要求 dry-run、no-write 或不落盘时，只在对话中说明本应写入的路径和内容摘要。

## Git 工作树检查

- 需要写入、审查或建立长期上下文前，优先运行 `git rev-parse --is-inside-work-tree` 判断目标路径是否在 git 工作树中。
- 需要读取当前文件状态时，运行 `git status --short` 或对应 skill 指定的只读预检脚本。
- dirty files 默认视为用户改动；除非能确认是本轮 agent 创建的文件，否则不要覆盖、清理或回滚。

## `.ai/ledev/` 与 `.gitignore`

- 运行进度统一写入 `.ai/ledev/state/<skill-name>.md`，不同 skill 不共用状态文件。
- 临时草稿、备份和恢复数据写入 `.ai/ledev/drafts/`；长期事实、任务、审查和 QA 写入各自子目录。
- 普通业务项目中，如 skill 会写入本地临时或运行产物，应确保对应目标路径被 Git 的有效 ignore 规则覆盖。检查必须在 `Primary repo` 根目录执行；`Related repos` 仍遵循只读边界。
- 修改项目根 `.gitignore` 前，对每个目标路径运行 `git check-ignore -q --no-index -- <target-path>`。该检查以 Git 实际生效结果为准，会同时考虑项目内各级 `.gitignore`、`.git/info/exclude`、`core.excludesFile`（例如用户配置的 `~/.gitignore`）及反向规则；不要只读取或解析某一个 ignore 文件。需要诊断匹配来源时使用 `git check-ignore -v --no-index -- <target-path>`。
- 文件目标直接检查文件路径；目录目标按该 skill 实际会写入的文件类型检查一个或多个无需创建的代表性子路径，例如 Markdown、JSON 和 HTML 草稿分别检查 `.ai/ledev/drafts/.ledev-ignore-probe.md`、`.ai/ledev/drafts/.ledev-ignore-probe.json` 和 `.ai/ledev/drafts/.ledev-ignore-probe.html`。所有实际产物类型都已被有效规则覆盖时才视为该目录已覆盖，避免扩展名规则造成误判。
- 目标路径已被任何有效规则覆盖时，不修改项目 `.gitignore`；这包括用户全局 ignore 或 `.git/info/exclude` 已覆盖的情况。只有未覆盖的目标才向项目根 `.gitignore` 追加最窄的缺失条目，不重排已有内容，也不因为项目缺少同名规则而重复追加。
- `git check-ignore --no-index` 只判断规则是否匹配，不会让已被 Git 跟踪的文件自动取消跟踪。目标已被跟踪时，不运行 `git rm --cached`；先记录现状并让用户决定是否继续纳入版本控制。
- dry-run、no-write 和只读 operation 只报告有效 ignore 状态和建议，不修改 `.gitignore`。用户明确要求把目标产物纳入版本控制时，也不添加 ignore 规则，并记录该决策。
- 如果某个 skill 要求工作树干净，而补充项目 `.gitignore` 会产生变更，追加后必须停止当前 operation，提示用户检查并提交该变更，再重新执行；不要在已经变脏的工作树上继续要求 clean-worktree 的流程。

## 路径可移植性

- 长期产物禁止写本机绝对路径，例如 `/Users/...`、`/home/...`、`C:\...`。
- 主仓库文件路径使用相对 `Primary repo` 根目录的路径。
- 关联仓库路径使用相对 `Primary repo` 的路径加仓库内路径，或稳定别名 `related:<repo>:<path>`。
- 本机绝对路径只允许进入 `.ai/ledev/drafts/local-paths.md` 或其他临时草稿，用于本轮路径映射、恢复或调试。

## 多仓库默认边界

- 多仓库上下文必须有且只有一个 `Primary repo`。
- `Related repos` 默认只读参考；除非用户明确切换目标或确认跨仓写入，不在关联仓库创建 `.ai/ledev/`、修改 `.gitignore` 或改业务文件。
- 如果关联仓库 checkout 与主仓库声明或实际解析版本不一致，必须记录风险；实现和验证判断优先依据主仓库实际解析版本。
