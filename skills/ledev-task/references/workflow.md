# Workflow

## 总流程

1. 识别操作：`default`、`new`、`continue`、`restart`、`close` 或 `block`。
2. 检查 git 状态，识别用户已有改动。
3. 对 `new` 先完成需求澄清；对其他操作读取已有 task 的阶段和上下文。
4. 读取已有 `.ai/ledev/project-context.md`、`.ai/ledev/facts/`、`.ai/ledev/qa/` 和相关 task；如果存在多仓库上下文，读取 `.ai/ledev/scope/scan-scope.md` 和 `.ai/ledev/facts/related-repos.md`。
5. 如果存在 `ledev-context` 产物，优先执行或建议 `$ledev-context status`，记录上下文是否 current、stale、missing 或 unknown。
6. 观察目标代码架构和相关实现。
7. 创建或更新 task，记录上下文、需求、范围、影响面、方案选项、阶段和 `Context Refresh` 初始判断。
8. 给出方案选项，必要时让用户选择；用户选择后给出最终执行摘要并等待确认。
9. 收到后续用户消息中的最终确认后实现或修复。创建/更新 task 草案的同一轮不得继续实现。
10. 更新实现记录。
11. 根据实际改动更新 `Context Refresh`：判断是否影响 `ledev-context`，并写入推荐命令。
12. 运行聚焦验证，必要时扩大验证范围或交接 `ledev-test`。
13. 更新验证记录，用 `scripts/generate_task_index.py` 刷新索引，并更新状态文件。
14. 收尾报告。

## default / 无参数

用于用户只输入 `$ledev-task`，没有其他参数时。

执行：

- 检查目标项目是否存在 `.ai/ledev/tasks/`。
- 读取 `.ai/ledev/tasks/index.md`；缺失或明显 stale 时，优先运行 `python3 <ledev-task-skill-dir>/scripts/generate_task_index.py <target-project-root>` 刷新索引。若当前场景不允许写文件，使用 `--dry-run` 或 `--unfinished-report` 只读输出。
- 展示 task 总数和状态统计。
- 列出可继续推进的未完成任务。未完成任务指状态不是 `awaiting_acceptance`、`done` 且不是 `obsolete` 的 task，通常包括 `todo`、`in_progress` 和 `blocked`。
- 将 `awaiting_acceptance` task 作为待验收任务单独列出；它不进入催办式未完成清单，但必须出现在状态统计和待验收分组中。
- 询问用户下一步意图，给出简短可执行选项，例如：`continue T###`、`new <需求>`、`restart T###`、`close T###`、`block T###`。
- 如果识别到唯一 `in_progress` task，把推荐命令实例化为具体编号，例如 `continue T003`，不要只给 `continue T###` 占位符。
- 不进入需求澄清、方案设计或实现；必须等用户明确下一步操作。

推荐只读命令：

```sh
python3 <ledev-task-skill-dir>/scripts/generate_task_index.py --unfinished-report <target-project-root>
```

如果没有任何 task，说明当前没有 task，并询问用户是否要 `new <需求>`。

## new / 新建

执行：

- 检查 `.ai/ledev/tasks/index.md`、`.ai/ledev/tasks/`、`.ai/ledev/state/ledev-task.md` 和 git 历史中已有 task 编号及未完成任务，避免重复创建。
- 创建 task 文件前必须先分配下一个不复用编号。优先运行只读命令：

```sh
python3 <ledev-task-skill-dir>/scripts/generate_task_index.py --next-id <target-project-root>
```

- 如果 `--next-id` 不可用，按 `references/task-files.md` 的编号规则手工扫描所有可见历史编号，取最大编号加一；不得因为索引缺失、目录为空、没有 active task 或解析失败而回退到 `T001`。
- 如果用户诉求可能属于未完成 task，先提示可 `continue T###`，除非用户明确要新建。
- 如果 `$ledev-task new` 后没有需求描述，先要求用户描述需求；如果后面已有文字，将其作为 `User Request` 原始诉求。
- 总结 agent 对需求的理解，至少包括目标、预期交付物、可能涉及的功能或模块、已知不做范围和当前假设。
- 列出模糊点、需求边界和待确认问题。优先确认成功标准、输入输出、必须支持的场景、不支持的场景、兼容性/API/数据格式/配置/权限/安全影响、是否允许重构、验证期望和交付限制。
- 用户补充后重新总结需求；如果仍有不明确问题，继续追问。只要目标、范围、边界、成功标准或关键约束不清楚，不得进入方案设计或实现。
- 需求初步明确后，读取项目上下文并扫描项目结构和相关代码，形成基于代码事实的 task 草案。
- 如果代码事实与用户诉求或前序假设冲突，必须回到需求确认阶段，说明冲突并要求用户确认。
- 如果 `ledev-context` 声明了 `Primary repo` / `Related repos`，确认本次 task 的目标仓库、只读关联仓库、可能跨仓影响和版本一致性。
- 记录用户原始诉求、需求理解、已确认需求、待确认问题、范围、影响面和上下文观察。
- 如果有多个合理方案，列出每个方案的改动范围、成本、风险、兼容性影响、验证方式和适用场景，让用户选择。
- 如果只有一个合理方案，也要说明为什么采用该方案，并给出预期改动和验证计划。
- 用户选择或认可方案后，给出最终执行摘要：确认需求、不做范围、采用方案、预计修改位置、验证计划、剩余风险。
- 收到后续用户消息中的明确确认（例如 `confirm`、`按这个执行`、`继续实现`）后，才把阶段推进到实现；未确认前状态保持 `todo` 或 `in_progress`，阶段保持在需求确认或方案确认。
- `new` 首次创建或更新 task 草案的 assistant turn 必须以确认请求结束，不得继续读取“刚写好的 task”并自动执行。用户在原始需求里写“帮我实现/修复/完成”只能作为需求意图，不是对最终方案的确认。

低风险例外：

- 对范围很小、需求明确、不会影响公共 API、数据格式、权限、安全边界或跨模块契约的任务，可以压缩提问轮次。
- 对 `chore`、`docs`、`tooling`、`config` 等低风险维护任务，可以使用 `templates/task-light-template.md`。如果执行中发现风险升高，切回完整模板并补齐缺失字段。
- 除 fast-path 外，即使压缩流程，也必须输出确认摘要和验证计划，并在用户确认后再实现。
- 用户明确要求“直接实现”，且请求已给出 what+where、无方案分支、改动极小、低风险（typo、一行 fix、局部重命名、纯文案或单行配置），可以走 fast-path：跳过隔轮确认，在同一轮记录关键假设、范围和验证计划后直接实现。
- fast-path 不适用于公共 API、数据格式、权限、安全边界、迁移、跨模块契约、跨仓改动、依赖升级或无法用聚焦验证覆盖的变更；发现歧义或风险升高时，必须暂停并回到最终确认点。

## continue / 继续

执行：

- 读取指定 task；未指定时从索引中选择唯一 `in_progress` task。若有多个，列出并要求用户指定。
- 读取 task 的当前阶段、open questions、上次 touched files 和验证状态。
- 重新检查 git 状态，确认期间是否有外部改动。
- 如果存在 `.ai/ledev/state/ledev-context.md` 或 `.ai/ledev/facts/manifest.md`，检查 context 快照是否可能 stale；发现外部改动或无法判断时，记录 `Context before task: unknown` 并推荐 `$ledev-context status`。
- 多仓库 task 还要检查相关 `Related repos` 的只读 git 状态和 checkout 是否变化；如果变化影响事实层，先更新或建议更新 `ledev-context`。
- 从上次未完成阶段继续，不重复已确认事项，除非代码事实、用户需求、方案选择或风险边界发生变化。
- 如果当前阶段早于 `solution_confirmed`，不得进入实现；先完成需求澄清、方案选择和最终确认。

## restart / 重启

用于任务目标不变，但上一阶段实现、方案或假设不再适用。

执行：

- 保留原 task 编号和文件。
- 在 `Decision Log` 追加 restart 事件，写明原因、废弃假设、保留产物和新方向。
- 区分重启类型：补丁式重启是在原目标和原结论基本成立时追加小修正；推翻式重启是原结论、方案或跨多文件实现方向被推翻。
- 补丁式重启可以继续使用原 task；推翻式重启或影响面明显扩大时，倾向新建后续 T###，并在原 task 的 `Handoff / Next` 或 `Decision Log` 留下指向。
- 反复重启、完成很久后才发现的问题，倾向封盘原 task，把 follow-up 独立成新 task，避免单个 task 文件无限膨胀。
- 将状态设为 `in_progress`。
- 重新做必要的上下文观察和需求确认。
- 不删除历史实现记录；如果需要回滚代码，必须得到用户明确指令或只修改当前 agent 自己刚做的改动。

## close / 完成

执行：

- 确认实现记录和验证记录完整。
- 确认 `Context Refresh` 已记录：本 task 是否影响 `ledev-context`、原因和具体推荐命令。
- 优先运行 `python3 <ledev-task-skill-dir>/scripts/lint_task.py --closing <task-file>`；必要时传 `--repo <target-project-root>`。脚本会用 unstaged、staged 和 untracked git 改动对账 `Implementation Log` / `Activity Log`，默认只打印 WARN，`--strict` 才因真实改动未记录而失败。脚本失败时，先补齐 task 记录或说明不能 close 的原因。
- 若未运行验证，必须说明原因和剩余风险；通常不要标记 `done`。
- 若 agent 能执行的实现和验证均已完成，只剩人工、运行时或目标环境验收，将 task 状态设为 `awaiting_acceptance`，在 `Handoff / Next` 记录具体验收动作；验收跑通后再改为 `done`。
- 若验证和必要验收已完成，更新 task 状态为 `done`；否则按上条设为 `awaiting_acceptance`。随后同步索引和 `.ai/ledev/state/ledev-task.md`。
- 同步索引时优先运行 `scripts/generate_task_index.py`，确保 `## Tasks` 表格里只有 task id 链接到对应 task 文件，Title 列保留纯文本。
- 最终回复包含文件变更、验证命令、结果、`ledev-context` 刷新建议和剩余风险。

## Context Refresh

`ledev-task` 不直接代替 `ledev-context` 刷新事实层或文档，但必须在 task 文件和最终回复中给出明确交接。

开始任务时：

- 如果目标项目存在 `.ai/ledev/project-context.md`、`.ai/ledev/facts/manifest.md` 或 `.ai/ledev/state/ledev-context.md`，优先执行或建议 `$ledev-context status`。
- 如果 status 显示 `current`，记录 `Context before task: current`。
- 如果 status 显示 stale、缺少快照或无法执行，记录 `stale`、`missing` 或 `unknown`，并把风险写入 `Context Notes`。
- 如果目标项目没有任何 context 产物，记录 `Context before task: missing`。

实现或验证后，根据实际改动选择推荐命令：

- `not-required`：未改变代码、配置、测试、脚本、依赖、目录结构、公共 API、数据模型、架构边界或跨仓关系。
- `$ledev-context status`：发现用户或其他工具在 task 期间也改了文件，无法判断 context 是否 stale。
- `$ledev-context refresh`：修改了源码、入口、配置、依赖、测试命令、公共符号、路由/API、数据结构、架构边界或其他事实层会捕获的内容。
- `$ledev-context scope`：新增/删除顶层目录、模块边界、扫描排除项、关联仓库、workspace/replace/vendor 关系或 scan depth 相关内容。
- `$ledev-context document`：事实层已更新，但正式 Markdown/HTML 仍需重建。

如果多条规则同时匹配，选择最保守的命令，优先级为：`$ledev-context scope` > `$ledev-context refresh` > `$ledev-context document` > `$ledev-context status` > `not-required`。

## block / 阻塞

执行：

- 记录阻塞原因、阻塞分类、已完成工作、需要用户或外部系统提供的信息。
- 阻塞分类使用稳定短语：`waiting-for-user`、`waiting-for-permission`、`waiting-for-dependency`、`waiting-for-environment`、`waiting-for-external-service`、`waiting-for-repo-state`。
- 在 task 的 `Handoff / Next` 记录最小可行动作，格式优先为：`Next action: <actor> - <specific action> - <expected unblock condition>`。
- 状态设为 `blocked`，同步索引。
- 给出最小可行动作，例如回答某个问题、授权某个命令、提供配置、恢复服务或清理工作树。
- 解除阻塞后用 `continue T###` 恢复；如果原方案仍有效，从阻塞前阶段继续，否则追加 `restart` 事件并回到相应阶段。

## 需求确认规则

必须向用户确认的情况：

- `new` 的需求、边界、成功标准、方案或验证计划尚未最终确认。
- 需求可能有多种合理解释。
- 改动会影响公共 API、数据格式、迁移、权限、计费、删除行为或安全边界。
- 需要选择实现策略，且不同策略有明显成本或兼容性差异。
- 发现用户诉求和代码事实冲突。

可以先假设并继续的情况：

- 改动范围小、风险低，项目模式清晰，且已给出确认摘要；此处的“继续”只允许继续需求整理、上下文观察、task 草案更新或方案说明，不允许越过最终确认进入实现。
- 用户明确要求直接实现：若命中 fast-path 窄条件（what+where 明确、无方案分支、改动极小低风险），可以同轮直接实现并记录假设；否则仍必须先输出最终执行摘要并等待后续用户确认。
- 问题可以通过代码事实验证，不依赖业务决策；可以先观察代码事实，但不得在 `new` 的同一轮直接改代码。

无论是否暂停确认，都要把假设写入 task。`new` 场景中，假设不能替代最终确认。

## 阶段规则

task 阶段使用稳定英文值，写入 task 文件和 `.ai/ledev/state/ledev-task.md`：

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

阶段推进要求：

- `new` 必须从需求阶段开始；除 fast-path 外，不得跳过需求总结、开放问题、方案说明和最终确认。
- 从 `requirements_confirmed` 到 `solution_options` 前，必须完成必要的代码上下文观察。
- 从 `solution_options` 到 `solution_confirmed` 必须有后续用户消息中的选择、认可或明确确认。
- 从 `solution_confirmed` 到 `implementing` 前，最终执行摘要必须包含需求、不做范围、采用方案、预计修改位置、验证计划和风险。
- 创建或更新 task 草案的同一轮不得进入 `implementing`；最早只能在用户看到最终执行摘要后，用下一条消息确认再进入实现。fast-path 例外必须满足“需求确认规则”中的窄触发条件，并把关键假设写入 task。
- 如果实现中发现需求或方案判断错误，回退到相应阶段并记录原因。

## 多仓库上下文继承

当 `.ai/ledev/scope/scan-scope.md` 或 `.ai/ledev/facts/related-repos.md` 声明多仓库上下文时，`ledev-task` 必须继承这些事实，而不是重新猜测仓库关系。

执行要求：

- `Primary repo` 是 task 文件、索引和状态文件的默认写入位置。
- `Related repos` 默认 `read-only`；可以读取用于理解 API、协议、类型、日志格式、测试夹具、上游/下游行为或参考实现。
- `Context Notes` 必须标明哪些观察来自主仓库，哪些来自关联仓库。
- `Scope` 必须写清楚本次会修改哪些仓库；未获确认时，关联仓库默认 `Out of Scope`。
- `Impact` 必须记录跨仓接口、协议、数据格式、依赖版本和兼容性风险。
- `Validation Log` 必须分别记录主仓库和跨仓验证命令；只验证主仓库时，说明关联仓库未验证原因。

版本处理：

- 实现和验证优先依据主仓库的实际解析版本，例如 lockfile、`go.mod` + `replace`、`go.work`、vendor 或构建脚本。
- 如果主仓库声明依赖 B 的版本是 `101`，但本地 B checkout 是 `102`，且没有证据表明构建会解析到本地 B，则不能把 B@102 的行为当作主仓库 confirmed behavior。
- 如果构建配置明确解析到本地 B@102，则 task 必须记录它与声明版本 `101` 的差异，并把兼容性风险写入 `Impact`。
- 需要精确修复/验证 `101` 时，优先使用独立 worktree、独立 clone 或 module cache；切换现有关联仓库 checkout 前必须确认，避免覆盖用户工作区。
