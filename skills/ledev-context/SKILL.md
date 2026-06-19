---
name: ledev-context
description: 面向中文用户。用于在开发、review、bugfix、测试或工具生成前，先确认扫描范围，再全量观察代码并建立结构化事实层，随后基于事实层建立、刷新、纠正可复用的项目上下文和项目文档。支持 scope、scan、summarize、qa、md、html、document、maintain、full 等模式。产出以中文为主，包括 .ai/scope/ 扫描范围、.ai/facts/ 事实库、AI 工作上下文、Markdown/HTML 项目文档、长期 QA 文档、Human Notes、Corrections 和 Open Questions。
---

# Project Context Builder

## 目的

在开发、review、bugfix、测试或工具生成之前，先建立一层可复用的项目知识。

这个 skill 维护四层项目知识：

- 范围层：确认扫描范围、排除项和仓库形态。
- 事实层：全量观察代码和仓库文件，记录可验证事实。
- 上下文层：基于事实层和长期 QA 生成 AI 工作上下文。
- 文档层：把稳定、已确认的信息沉淀为 Markdown/HTML 项目文档。

支持单仓库、monorepo，以及“主仓库 + 关联仓库”的多仓库上下文。多仓库上下文必须有且只有一个 `Primary repo`；其他仓库只能作为 `Related repos` 写入主仓库 `.ai/` 产物，除非用户明确要求跨仓写入。

## 中文优先规则

- 面向中文用户时，终端说明、QA 问题、草稿、最终上下文和人类文档都必须以中文为主。
- 命令、文件路径、配置项、代码标识、模式名、状态值、字段名可以保留英文，例如 `qa`、`Status`、`QA-001`、`.ai/project-context.md`。
- 需要用户输入的短确认 token、短命令和选项必须使用英文，例如 `Y/N`、`yes/no`、`rollback`、`delete/keep`、`continue/stop`、`edit/confirm`。可以用中文解释含义，但不要要求用户输入“是/否”“确认/取消”“覆盖/跳过”“删除/保留”等中文短命令。
- 如果用户用英文回答，可以保留原文；需要进入正式上下文或人类文档时，用中文总结。
- 不要因为模板字段是英文就输出整段英文说明。

## 范围

需要捕获：

- 结构化代码事实：目录树、文件清单、语言/框架、包/模块、入口、导出符号、核心类型、接口、路由/API、配置、脚本、测试、生成代码。
- 架构事实：模块依赖、调用方向、数据流入口和出口、外部依赖、存储/消息/网络边界、构建和运行边界。
- 命令事实：build、run、test、lint、format、generate 命令及证据来源。
- 风险边界事实：generated、vendor、third-party、legacy、敏感目录、dirty files、不能覆盖的文件。
- 多仓库事实：Primary repo、Related repos、仓库角色、扫描深度、写入策略、声明依赖版本、实际解析版本、本地检出版本、版本不一致风险。
- Human Notes、Corrections、QA answers、Open Questions

工程支撑事实可以进入事实层，但生成 Markdown/HTML 时必须和业务能力、业务上下游、运行时依赖分开；`go.mod`、`Makefile`、CI、lint、测试、本地 dev scripts、generated 和 third-party 不应写成业务能力或业务外部依赖。

不要做：

- 实现产品功能
- 直接修 bug
- 大范围重构
- 把大段源码复制进文档
- 把本机绝对路径写入长期产物，例如 `.ai/scope/`、`.ai/facts/`、`.ai/qa/`、`.ai/project-context.md`、`.ai/project-context.html` 或人类文档。
- 在事实层做业务推理或意图猜测
- 把不确定推断写成确认事实
- 在没有证据的情况下写“核心”“主要”“推荐”等判断
- 把本地关联仓库的当前 checkout 直接当成主仓库实际依赖版本，除非 `go.work`、`replace`、workspace、lockfile 或构建配置能证明实际解析到该路径。

## 读取 Reference

只读取当前模式需要的 reference：

- 模式行为、阶段锚点、草稿落盘、输出规则和工作流细节：读 `references/modes.md`。
- scope 模式、扫描范围确认、`SCOPE-###` 问题和复用规则：读 `references/scope.md`。
- 事实层目录、采集规则、证据要求和事实模板：读 `references/facts.md`。
- QA 模式、长期 QA 文档、稳定问题编号、终端输出格式、冲突处理、答案合并：读 `references/qa.md`。
- 目标项目语言规则：已知语言时读 `rules/<language>.md`。Go 项目读 `rules/go.md`。
- 输出文件结构模板：按需要读取 `templates/` 下的模板：
  - `draft-template.md`
  - `fact-template.md`
  - `scope-template.md`
  - `qa-template.md`
  - `project-context-template.md`
  - `project-context-html-template.md`
  - `project-context-html-template.html`
  - `project-context-html-data-template.json`
  - `ledev-context-state-template.md`
  - `skill-state-template.md`

文件布局约定：`references/` 只放模式规则、流程说明、采集规则和背景材料；`templates/` 放可复制或可实例化的 Markdown/HTML/状态文件模板。新增模板时不要放进 `references/`。

如果没有对应语言规则，使用通用流程，并把缺失语言规则记录为可改进点。

### HTML 生成方式

`html`、`document` 和 `full` 中默认使用 AI + 脚本流程生成 HTML。详细流程见 `references/modes.md` 和 `templates/project-context-html-template.md`，主规则只保留以下约束：

- AI 只生成 `.ai/drafts/project-context-html-data.json` 中的纯文本占位符；脚本 `scripts/render_project_context_html.py` 负责读取模板、HTML 转义、占位符替换和结构自检。
- `templates/project-context-html-data-template.json` 只是 skill 开发参考，不作为 `html` 运行时标准；运行时字段集合以脚本从当前 HTML 模板提取的占位符为准。
- 如果 `.ai/project-context.html` 已存在，脚本先把旧版本备份到 `.ai/drafts/project-context.<timestamp>.html`，再直接覆盖正式文件；备份最多保留 5 个，超过后删除最旧备份。
- HTML/CSS/布局调整必须先修改 `templates/project-context-html-template.html`，再重新渲染；不要只修改单次生成产物。
- 最终 HTML 固定 11 个主章节，区分事实、推断、风险和开放问题；生成判断需要内部依据，但 HTML 不展示证据路径、证据索引或内部来源标签。

## 调用模式

把 skill 名称后的第一个词视为模式名。模式名大小写不敏感；面向用户展示命令时优先用小写。

推荐顺序：

1. `scope`
2. `scan`
3. `summarize`
4. `qa`
5. `md`
6. `html`
7. `document`
8. `maintain`

支持模式：

- `default`：说明可用模式和副作用；不扫描、不运行命令、不写文件。
- `scope`：轻量发现仓库规模、语言、目录和排除项，写入 `.ai/scope/scan-scope.md` 并请求用户确认。
- `scan`：读取已确认 scope，全量观察代码和仓库文件，建立 `.ai/facts/` 结构化事实层；除非 dry-run/no-write，否则写入事实文件。
- `summarize`：基于 `.ai/facts/` 和长期 QA 生成 `.ai/drafts/project-context-draft.md`。
- `qa`：维护 `.ai/qa/project-qa.md`，使用稳定 `QA-###` 编号；用户可编辑文件或按编号 inline 回答。
- `md`：把已确认草稿和 QA 结论提升到 `.ai/project-context.md`、`.ai/state/ledev-context.md` 或 Markdown 人类文档。
- `html`：基于事实层、长期 QA 和 `.ai/project-context.md` 重新编排信息，生成 `.ai/project-context.html`。
- `rollback`：列出 `.ai/drafts/project-context.<timestamp>.html` 备份，按时间倒序让用户选择版本并恢复到 `.ai/project-context.html`。
- `document`：默认组合执行 `md` 和 `html`；先刷新或校验 `.ai/project-context.md` 是否符合当前 Markdown 模板，再生成 HTML。
- `maintain`：根据用户纠正或项目变化增量维护上下文，保留 `Human Notes` 和 `Corrections`。
- `full`：按 scope、scan、summarize、qa、md、html 分阶段执行；写正式文件前暂停，问题超过 10 个前暂停。

示例：

- `$ledev-context`
- `$ledev-context scope`
- `$ledev-context scan`
- `$ledev-context summarize`
- `$ledev-context qa`
- `$ledev-context md`
- `$ledev-context html`
- `$ledev-context rollback`
- `$ledev-context document`
- `$ledev-context maintain`
- `$ledev-context full`

## 硬性规则

### 启动与阶段

- 除 `default` 外，所有模式启动时先判断目标路径是否在 git 工作树内：优先运行 `git rev-parse --is-inside-work-tree`。
- 多仓库上下文中，启动检查以 `Primary repo` 为目标项目；对每个 `Related repo` 只做只读存在性、git 状态和版本信息检查，默认不写入关联仓库。
- `scope` 是正式第一阶段；不再使用 `plan` 作为阶段锚点。裸调用 `default` 只说明模式和推荐下一步。
- 用户显式指定某个模式时，必须按该模式执行；不要因为当前阶段锚点已经在后续阶段，就自动跳到“下一步”或只执行后续阶段。下一步建议只作为执行完成后的提示，不改变本次用户指定的命令。
- `scan` 必须先读取 `.ai/scope/scan-scope.md`。如果 scope 缺失、未确认或明显 stale，先运行或更新 `scope`。
- `.ai/facts/` 是后续 AI 逻辑的基准数据源；`summarize`、`qa`、`md`、`html`、`document`、`maintain` 都必须先读取相关事实文件。
- 分阶段工作时，在 `.ai/state/ledev-context.md` 维护 `ledev-context` 自己的阶段锚点。其他 skill 必须写各自的 `.ai/state/<skill-name>.md`，不要共用一个状态文件。
- 不允许跳过未完成阶段向后推进锚点。
- 显式重复执行当前锚点之前的阶段时，执行成功后必须把 `.ai/state/ledev-context.md` 的锚点前置到本次完成阶段，并把依赖后续产物标记为 stale；不要继续保留较新的锚点。
- 每个非 `default` 模式完成后，都要报告本次完成的阶段、当前锚点、受影响产物，并给出推荐下一步命令。每条推荐命令后必须附一句简短说明，说明它会做什么。推荐下一步不能替代用户下一次显式输入。
- 当推荐 `$ledev-context md` 时，必须同时提示 `$ledev-context document`：`md` 只生成或刷新 Markdown 上下文，`document` 会组合执行 Markdown 和 HTML 文档生成。

### 事实与推断

- 最终上下文和文档必须以事实为主，明确区分 Confirmed Facts 和 Inferred Assumptions。
- 事实层只记录可观察事实和证据，不写业务推理、价值判断或未经验证的架构解释。
- 每条重要事实必须有证据来源，优先使用文件路径、符号名、命令输出或配置项；能定位行号时写行号。
- 长期产物中的路径必须使用可移植路径：主仓库内使用相对 `Primary repo` 根目录的路径；关联仓库使用相对 `Primary repo` 的相对路径加仓库内路径，例如 `../funnel:cmd/server/main.go` 或 `related:funnel:cmd/server/main.go`。不要写 `/Users/...`、`/home/...`、`C:\...` 这类本机绝对路径。
- 如果确实需要记录本机绝对路径用于本轮恢复、调试或路径映射，只能写入 `.ai/drafts/local-paths.md` 或 `.ai/drafts/` 下其他临时文件；提升到正式上下文、事实层、人类文档或 HTML 前必须改写为可移植路径。
- dirty files 默认视为用户改动，除非明确是当前任务创建的。
- 运行脚本产生的解释器缓存或工具缓存如果已被 git ignore 覆盖，例如 `__pycache__/`、`*.py[cod]`，不要主动查询或清理；只处理会进入 `git status`、影响事实层或影响正式产物的文件。

### 写入与临时文件

- 除非用户特别说明，所有 skill 在目标项目中产生的文件都必须限定在目标项目的 `.ai/` 目录下；运行进度写入 `.ai/state/<skill-name>.md`，长期知识写入 `.ai/facts/`、`.ai/qa/`、`.ai/project-context.md` 等对应子路径。
- 多仓库上下文的 `.ai/` 产物默认只写入 `Primary repo`。不要为了记录事实在 `Related repos` 中创建 `.ai/`、修改 `.gitignore` 或写状态文件，除非用户明确把该关联仓库切换为独立目标项目。
- 如果目标路径是 git 项目且允许写文件，必须确保 `.gitignore` 包含 `.ai/drafts/`；如果 `.gitignore` 不存在则创建。如果用户要求 dry-run/no-write，只报告需要加入该规则。
- 显式 `scan` 模式写 `.ai/facts/`；显式 `summarize` 模式可以写 `.ai/drafts/` 草稿，除非用户要求 dry-run/no-write。
- QA 写入长期文档 `.ai/qa/project-qa.md`，除非用户要求 dry-run/no-write。
- `.ai/drafts/` 是临时恢复数据，不是长期知识库。`md` 成功提升后，删除已提升的 draft 文件；如果 draft 中存在未提升到正式文档、事实层或长期 QA 的人工补充，先提升或向用户确认后再删除。
- 写 `.ai/project-context.md`、`.ai/project-context.html`、`.ai/state/ledev-context.md` 或人类文档前，必须说明目标文件，除非用户已经明确要求写入。
- `md` 写入或校验时必须以当前 `templates/project-context-template.md` 为结构标准。即使代码事实没有变化，只要现有 `.ai/project-context.md` 缺少当前模板要求的章节、表格、字段或生成规则，也视为 stale，必须刷新 Markdown 后再进入 HTML。
- `html` 写入前必须检查 `.ai/project-context.md` 是否存在、基于当前事实层，并且符合当前 Markdown 模板结构；如果缺失、stale 或缺少 HTML 所需的数据源章节，先运行或要求运行 `md`。如果 `.ai/project-context.html` 已存在，渲染脚本必须先自动备份旧版本到 `.ai/drafts/project-context.<timestamp>.html`，再覆盖正式 HTML；运行完成后告诉用户可以用 `rollback` 回退，并列出可回退版本（时间倒序）。
- `rollback` 必须先列出 `.ai/drafts/project-context.<timestamp>.html` 中可用备份，按时间倒序展示，让用户选择一个版本后再恢复；不要在没有用户选择的情况下覆盖 `.ai/project-context.html`。

### 维护与冲突

- 刷新和维护时必须保留 `Human Notes` 和 `Corrections`。
- 如果人工补充和代码事实冲突，记录冲突并向用户确认，不要直接覆盖。

## QA 硬性规则

- QA 是文件优先、长期维护的项目知识。只要有问题，先写入 `.ai/qa/project-qa.md`，再提示用户回答。
- 创建新问题前先读已有 `.ai/qa/project-qa.md`；已有答案作为人工项目知识使用，除非它和已验证代码事实冲突。
- 如果已有 QA 和当前理解冲突，追加新的 follow-up 问题，不覆盖旧答案。
- 终端 QA 输出保持简短：QA 文件路径、问题编号、短标题、回答方式。
- 每个问题必须有稳定编号，例如 `QA-001`、`QA-002`。
- 追加问题时，从当前 QA 文档中最大编号继续递增。
- 问题展示给用户后不允许重编号。
- 过期问题标记 `Status: obsolete`，不要删除后复用编号。
- 接受 `QA-001: ...` 这类 inline 回答；允许写文件时合并回 QA 文档。
- QA 文档是最终上下文和人类文档的长期补充；可以把简洁结论提升到 `.ai/project-context.md` 或人类文档，但必须保留完整 QA 历史。
