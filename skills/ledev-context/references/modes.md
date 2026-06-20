# Project Context Builder 模式说明

这个 reference 描述 `ledev-context` 各模式的详细行为。所有运行产物以中文为主；命令、路径、状态值、字段名可以保留英文。

## 通用规则

模式名大小写不敏感。对用户展示命令时，优先使用小写模式名。

需要用户输入的短确认 token、短命令和选项必须使用英文，例如 `Y/N`、`yes/no`、`rollback`、`delete/keep`、`continue/stop`、`edit/confirm`。终端说明可以中文解释这些选项的含义，但不要要求用户输入“是/否”“确认/取消”“覆盖/跳过”“删除/保留”等中文短命令。

除 `default` 外，每次运行先做 git 工作树检查：

除非用户特别说明，所有 skill 在目标项目中产生的文件都必须限定在目标项目的 `.ai/` 目录下。运行进度统一写入目标项目 `.ai/state/`，并按 skill 分文件，例如 `.ai/state/ledev-context.md`、`.ai/state/ledev-task.md`。不要在目标项目根目录创建独立的 `state/` 目录。

- 优先运行 `git rev-parse --is-inside-work-tree` 判断目标路径是否在 git 项目内。
- 多仓库上下文中，目标路径指 `Primary repo`。对 `Related repos` 只做只读检查：路径是否存在、是否 git 工作树、`git status --short`、branch/tag/commit 信息和依赖解析证据；不要在关联仓库写 `.ai/` 或修改 ignore 文件。
- 如果是 git 项目且允许写文件，读取或创建目标项目根目录的 `.gitignore`，确保包含 `.ai/drafts/`。
- `.ai/drafts/` 规则已存在时不要重复追加；如果存在等价忽略规则，可以视为已满足。
- 如果用户要求 dry-run/no-write，只报告需要加入 `.ai/drafts/`，不修改 `.gitignore`。
- 如果不是 git 项目，不创建 `.gitignore`，只继续当前模式。

路径可移植性：

- `.ai/scope/`、`.ai/facts/`、`.ai/qa/`、`.ai/project-context.md`、`.ai/project-context.html` 和人类文档中禁止写本机绝对路径。
- 主仓库文件路径使用相对 `Primary repo` 根目录的路径，例如 `cmd/server/main.go`。
- 关联仓库路径使用相对 `Primary repo` 的仓库路径加仓库内路径，例如 `../funnel:internal/log/parser.go`；也可使用稳定别名格式 `related:funnel:internal/log/parser.go`。
- 本机绝对路径只允许写入 `.ai/drafts/local-paths.md` 或 `.ai/drafts/` 下临时文件，用于本轮路径映射、恢复或调试；任何正式产物生成前都必须改写为可移植路径。

可重复执行：

- `scope`、`scan`、`summarize`、`qa` 可以安全重复执行。
- `md`、`html`、`document` 可以重复执行。`document` 默认先执行或校验 `md`，再执行 `html`；`html` 已存在时自动备份旧版后覆盖；`md` 和人类文档写入仍按目标文件风险确认，并保留已有 `Human Notes` 和 `Corrections`。
- `maintain` 用于用户纠正、项目新增模块、命令变化、结构变化后的增量维护。
- `full` 适合首次完整建档，但写正式文件前仍然必须暂停确认。

显式模式优先：

- 用户显式执行某个模式时，本次运行必须以该模式为目标；不要因为 `.ai/state/ledev-context.md` 已经记录了后续锚点，就跳过用户指定阶段、改成执行下一阶段，或只做“当前锚点之后”的工作。
- 推荐下一步只是本次完成后的提示，不是自动续跑授权。每条推荐命令后必须附一句简短说明，说明它会做什么。用户没有执行下一步时，后续重复执行当前阶段或执行更早阶段都必须按用户命令处理。
- 当推荐 `$ledev-context md` 时，必须同时提示 `$ledev-context document`：`md` 只生成或刷新 Markdown 上下文，`document` 会组合执行 Markdown 和 HTML 文档生成。
- 如果用户显式执行前序阶段，例如当前锚点是 `html` 但用户执行 `scan`，完成后必须把锚点前置到 `scan`，并把 `summarize`、`qa`、`md`、`html`、`document` 等依赖后续产物标记为 stale 或在输出中明确说明需要重建。
- 如果用户显式重复执行当前锚点阶段，完成后锚点仍停留在该阶段；只标记依赖它的后续产物 stale。

## 事实层、草稿和长期 QA

- `scan` 默认不写正式上下文或正式项目文档；它写结构化事实层 `.ai/facts/`。
- 显式执行 `scan` 时，除非用户要求 dry-run/no-write，否则自动写入 `.ai/facts/`。
- `summarize` 默认不写正式上下文或正式项目文档；显式执行时，除非用户要求 dry-run/no-write，否则写入可恢复草稿到 `.ai/drafts/`。
- `.ai/facts/` 是后续 AI 逻辑的基准数据源。`summarize`、`qa`、`md`、`html`、`document`、`maintain` 都必须先读取相关事实文件。
- `qa` 写入长期 QA 文档 `.ai/qa/project-qa.md`。QA 答案是长期项目知识，不是 disposable draft。
- 写草稿前要说明目标文件；如果用户已经在执行分阶段建档流程，草稿写入不需要像正式文档那样反复确认。
- 运行 Python 或其他脚本产生的解释器缓存、工具缓存如果已被 git ignore 覆盖，例如 `__pycache__/`、`*.py[cod]`，不要为了清理而额外查询或删除；用 `git status --short` 判断真实待说明变更即可。
- 推荐事实文件：
  - `.ai/scope/scan-scope.md`
  - `.ai/facts/manifest.md`
  - `.ai/facts/repo-structure.md`
  - `.ai/facts/code-inventory.md`
  - `.ai/facts/architecture-facts.md`
  - `.ai/facts/commands.md`
  - `.ai/facts/dependencies.md`
  - `.ai/facts/tests.md`
  - `.ai/facts/boundaries.md`
  - `.ai/facts/related-repos.md`
  - `.ai/facts/evidence-index.md`
- 推荐草稿文件：
  - `.ai/drafts/project-scan.md`
  - `.ai/drafts/project-context-draft.md`
  - `.ai/drafts/project-context-html-data.json`
  - `.ai/drafts/local-paths.md`
- 长期 QA 文件：
  - `.ai/qa/project-qa.md`
- `md` 应读取事实层、草稿和长期 QA，把已验证摘要提升到 `.ai/project-context.md` 或 Markdown 人类文档。`html` 应读取事实层、长期 QA 和 `.ai/project-context.md`，把信息重新编排为 `.ai/project-context.html`。
- `.ai/drafts/` 是临时恢复数据，不是长期项目知识。正式文档提升成功后，默认删除已提升的 draft 文件；如果 `.ai/drafts/` 为空，可以删除空目录。
- 删除 draft 前必须确认其中没有未提升到 `.ai/project-context.md`、人类文档、`.ai/facts/` 或 `.ai/qa/project-qa.md` 的人工补充；有未提升信息时，先提升或向用户确认。需要用户选择时使用 `delete/keep` 或 `promote/keep`。
- 正常文档提升时，不要归档或删除 `.ai/qa/project-qa.md`。

## 阶段锚点

- 在 `.ai/state/ledev-context.md` 维护 `ledev-context` 的 phase anchor。
- `.ai/state/` 是运行进度目录，不属于 `.ai/` 项目知识库；不同 skill 必须使用不同文件，例如 `.ai/state/ledev-task.md`、`.ai/state/ledev-test.md`。
- 锚点记录“最后完整完成的阶段”，不是当前正在执行的阶段。
- 合法顺序：`none -> scope -> scan -> summarize -> qa -> md -> html -> document -> maintain`。`rollback` 是恢复动作，不属于阶段锚点顺序。
- 向后推进锚点必须按顺序，并且只能在阶段完成后推进。
- 阶段只完成一半时，不推进锚点。
- 用户重复执行前序阶段时，必须把锚点前置到该阶段，并把后续草稿、正式上下文、HTML 或人类文档标记为 stale，直到重新生成。
- 不要仅因为前序阶段重复，就把长期 QA 标记为 obsolete；如果事实冲突，追加 follow-up 问题。
- 不允许跳过未完成阶段向后推进锚点。

锚点前置影响范围：

| 完成阶段 | 当前锚点应设为 | 必须标记 stale 或提示重建的后续产物 | 推荐下一步 |
| --- | --- | --- | --- |
| scope | scope | `.ai/facts/`、`.ai/drafts/project-context-draft.md`、`.ai/project-context.md`、`.ai/project-context.html`、人类文档 | `$ledev-context scan`：按已确认范围采集结构化事实。 |
| scan | scan | `.ai/drafts/project-context-draft.md`、`.ai/project-context.md`、`.ai/project-context.html`、人类文档 | `$ledev-context summarize`：基于事实层生成上下文草稿。 |
| summarize | summarize | `.ai/project-context.md`、`.ai/project-context.html`、人类文档 | `$ledev-context qa`：补齐代码无法确认的问题；或 `$ledev-context md`：生成 Markdown 上下文；也可用 `$ledev-context document`：一次生成 Markdown 和 HTML 文档。 |
| qa | qa | `.ai/project-context.md`、`.ai/project-context.html`、人类文档 | `$ledev-context md`：生成 Markdown 上下文；也可用 `$ledev-context document`：一次生成 Markdown 和 HTML 文档。 |
| md | md | `.ai/project-context.html`、HTML 人类文档 | `$ledev-context html`：基于 Markdown 上下文生成 HTML。 |
| html | html | `document` 阶段状态 | `$ledev-context document`：校验/刷新 Markdown 并生成 HTML；如果不需要组合文档，可以结束。 |
| document | document | 无，除非用户后续回到前序阶段 | `$ledev-context maintain`：在项目变化或人工纠正后增量维护上下文；没有变化时可以结束。 |

每个非 `default` 模式完成后必须输出：

- 本次完成阶段。
- 当前锚点。
- 被标记 stale 或需要重建的后续产物。
- 推荐下一步命令及一句简短用途说明；如果没有必要下一步，说明可以结束或按需执行 `maintain`。
- 推荐 `$ledev-context md` 时，必须同时列出 `$ledev-context document` 作为组合生成 Markdown 和 HTML 的选择。

## Default

裸调用 skill 时：

- 说明可用模式。
- 说明哪些模式只读，哪些模式可能写文件。
- 推荐下一步，并用一句话说明推荐命令会做什么。
- 不运行仓库扫描命令。
- 不创建或修改文件。

## Scope

轻量发现仓库形态并确认扫描范围。详细规则见 `scope.md`。

包括：

- 目标路径。
- 路径展示策略：长期产物只使用可移植相对路径；本机绝对路径如需记录，写入 `.ai/drafts/local-paths.md`。
- 仓库类型判断：single-project、monorepo 或 unknown。
- 多仓库形态判断：是否存在 `Primary repo` 和 `Related repos`，以及每个关联仓库的角色、扫描深度、写入策略和版本关系。
- 主要语言候选和需要加载的语言规则。
- 文件数量、顶层目录、关键配置文件和 ignore 文件。
- deep scan、shallow record、exclude 范围。
- generated/vendor/build artifacts 判断。
- 分批扫描计划。
- `SCOPE-###` 确认问题。

除非用户要求 dry-run/no-write，否则写入 `.ai/scope/scan-scope.md`。

scope 已写入并得到确认，或用户明确要求按当前 scope 继续时，才能把阶段锚点推进到 `scope`。

## Scan

全量观察仓库，建立结构化事实层。只运行安全发现命令，例如：

- `pwd`
- `git status --short`
- `rg --files` 等快速文件列表或搜索命令

进入 scan 前必须读取 `.ai/scope/scan-scope.md`。如果 scope 缺失、未确认或明显 stale，先运行或更新 `scope`。

识别：

- 完整文件清单、目录结构和扫描排除范围。
- Primary repo 和每个 Related repo 的仓库身份、扫描范围、git 状态、声明版本、实际解析来源、本地 checkout 和版本一致性。
- 路径证据必须标准化为可移植路径；如果发现命令输出包含本机绝对路径，写入事实层前要改写为相对路径或仓库别名路径。
- 语言、包管理器、模块文件、构建文件、CI 文件。
- README、docs、scripts 和命令说明。
- generated、vendor、third-party、legacy 或高风险区域。
- dirty files，默认视为用户改动。
- 源码入口、包/模块、公开符号、核心类型、接口、配置读取点。
- 可观察架构关系：import、调用方向、路由/API 注册、配置引用、外部边界。
- 测试文件、fixtures、mocks、集成测试和外部依赖。

输出：

- `.ai/facts/` 下的结构化事实文件。
- 多仓库上下文写入 `.ai/facts/related-repos.md`，并在 `manifest.md`、`dependencies.md`、`boundaries.md` 和 `evidence-index.md` 引用。
- 如需保留本机绝对路径映射，写入 `.ai/drafts/local-paths.md`，不要写入事实层。
- 未扫描或无法读取内容的原因。
- 事实缺口和可能进入 QA 的问题。

除非用户要求 dry-run/no-write，否则写入 `.ai/facts/`。可以额外写 `.ai/drafts/project-scan.md` 作为本次扫描摘要，但不能用扫描摘要替代事实层。

事实层完成后，才能把阶段锚点推进到 `scan`。

## Summarize

基于 `.ai/facts/`、长期 QA 和必要草稿创建项目上下文草稿。不能绕过事实层直接总结 README 或少量文件。

明确区分：

- `Confirmed Facts`：从仓库文件、命令或用户补充中确认的事实。
- `Inferred Assumptions`：AI 推断但仍需确认的内容。
- `Open Questions`：需要人确认的问题。

多仓库草稿必须明确哪些结论来自 `Primary repo`，哪些来自 `Related repos`。如果本地关联仓库版本和主仓库实际解析版本不一致，草稿中不得把本地版本事实写成主仓库的 confirmed runtime behavior。

草稿要足够简洁，方便后续任务开始前快速阅读。

除非用户要求 dry-run/no-write，否则保存到 `.ai/drafts/project-context-draft.md`。

上下文草稿完成后，才能把阶段锚点推进到 `summarize`。

## QA

详细交互规则见 `qa.md`。

本模式要求：

- 如果存在 `.ai/qa/project-qa.md`，先读取。
- 先读取 `.ai/facts/manifest.md` 和相关事实文件。
- 只询问无法从代码可靠推断的事实。
- 如果已有 QA 答案和已验证代码事实或当前草稿冲突，追加 follow-up 问题。
- 优先提出 5-10 个高价值问题，不做长问卷。
- 每个问题写成 `.ai/qa/project-qa.md` 中详细的 `QA-###` 条目。
- 告知用户可以编辑文件回答，也可以按 QA 编号 inline 回答。
- 详细答案保留在 `.ai/qa/project-qa.md`；必要时把简洁结论提升到 `Human Notes`。

只有必答问题已经 answered、deferred 或 not-applicable，才把阶段锚点推进到 `qa`。

## md

写入或更新已确认的 Markdown 上下文和文档，例如：

- `.ai/facts/`
- `.ai/project-context.md`
- `.ai/state/ledev-context.md`
- `.ai/qa/project-qa.md`
- `docs/architecture.md`
- `docs/development.md`
- `docs/testing.md`
- `docs/module-map.md`

`.ai/project-context.md` 默认使用 `templates/project-context-template.md` 生成；该模板以项目定位、系统边界、架构总览、核心抽象、业务能力、模块映射、新人上手、数据状态模型、关键流程、安全、配置、依赖、失败恢复、场景差异、代码导航、项目约定和其他补充为主线。生成时必须区分业务链路、运行时依赖、工程支撑和代码边界：`go.mod`、`Makefile`、CI、lint、测试、dev scripts、generated、third-party 不应写成业务上下游、业务外部依赖或业务能力。

前置检查：

- 必须先读取 `.ai/facts/manifest.md`、相关事实文件、`.ai/drafts/project-context-draft.md` 和 `.ai/qa/project-qa.md`。
- 如果存在 `.ai/facts/related-repos.md`，必须读取，并把多仓版本关系、只读边界和跨仓依赖事实提升到合适章节。
- 如果 scope、scan、summarize 或 qa 缺失、未完成或明显 stale，先回到对应阶段，不直接写正式文档。
- 如果 `.ai/project-context.md` 已存在，先读取并保留 `Human Notes`、`Corrections`、仍然相关的 QA 结论和人工补充。
- 必须读取当前 `templates/project-context-template.md` 并用它校验现有 `.ai/project-context.md` 的结构。只要现有 Markdown 缺少当前模板要求的章节、表格、字段或生成规则，即使事实层没有变化，也视为 stale，必须刷新 Markdown。
- 当前 HTML 依赖 Markdown 中的结构化来源：`5. 业务能力与模块划分`、`8. 核心数据与状态模型`、`9. 关键业务流程`、`10. 安全防控`、`12. 外部依赖与集成`。如果这些章节仍是旧结构，或者缺少数据域、核心对象、数据关系、状态机、状态流转、参与方边界、时序步骤、阶段拆解、业务安全、加密相关、安全关注点等表述，必须先更新 `.ai/project-context.md`，不能只刷新 HTML。

写入前说明目标文件并确认，除非用户已经明确要求写入。

只把事实层中有证据、或长期 QA 中已人工确认的内容提升到正式文档。人类文档应写稳定知识，不写临时 dirty 状态或未经确认的 AI 推断。

提升到 Markdown 或人类文档前必须检查路径可移植性：删除或改写本机绝对路径；关联仓库路径保留为相对 `Primary repo` 的路径或 `related:<name>:<path>` 别名。

内容分层要求：

- 多仓库上下文必须区分主仓库负责范围、关联仓库参考范围和跨仓接口/协议边界。关联仓库不是本项目业务能力，除非它就是本项目运行时实际解析到的 workspace 成员或用户明确要求把多个仓库作为一个系统上下文描述。
- 架构总览只画业务链路和核心执行单元；工程支撑、构建工具、测试工具、本地开发脚本、generated/third-party 边界不要进入主架构图。
- 核心抽象只列影响业务理解和运行链路的抽象；普通 helper、配置辅助、测试夹具、构建脚本和生成代码不要列为核心抽象。
- 业务能力只列项目对业务或运行链路提供的能力；构建、lint、测试、发版、代码生成、CI 和本地辅助能力放入工程支撑能力。
- 外部依赖与集成必须拆分为业务上下游与运行时依赖、工程支撑依赖、代码边界依赖。
- 新人快速上手必须区分阅读路径、开发入口、排障入口和不建议先读的区域。

`.ai/qa/project-qa.md` 是人工确认、决策和未解决上下文的长期来源。最终文档可以提炼结论，但 QA 文档应保留为补充细节。

Markdown 上下文或文档写入成功后，才能把阶段锚点推进到 `md`。

阶段锚点推进到 `md` 后，删除已提升的 `.ai/drafts/project-scan.md` 和 `.ai/drafts/project-context-draft.md`；如果目录为空，删除 `.ai/drafts/`。如果用户要求保留或当前执行是 dry-run/no-write，只把 draft 状态标记为 `promoted` 或报告待清理项。

## html

生成 `.ai/project-context.html`。它是 `.ai/` 下的阶段性项目上下文产物，用于把事实层、长期 QA 和 Markdown 上下文整理成可查阅的单文件 HTML；不是对外汇报页、营销页或按读者画像包装的展示文档。

前置检查：

- 必须先读取 `.ai/facts/manifest.md`、相关事实文件、`.ai/qa/project-qa.md` 和 `.ai/project-context.md`。
- 如果存在 `.ai/facts/related-repos.md`，必须读取；HTML 可以展示跨仓边界和版本风险的结论，但不要展示内部扫描路径或完整证据索引。
- 如果 `.ai/project-context.md` 缺失、未完成、相对当前事实层明显 stale，或不符合当前 `templates/project-context-template.md` 的结构要求，先运行或要求运行 `md`。
- 如果 HTML 当前章节需要的结构化来源在 Markdown 中缺失，例如业务能力、关键业务流程、数据域、核心对象、数据关系、状态机、状态流转、业务安全、加密相关或安全关注点，先运行或要求运行 `md`；不要直接从事实层临时拼 HTML 来掩盖 Markdown 过期。
- 如果 scope、scan、summarize 或 qa 缺失、未完成或明显 stale，先回到对应阶段。
- 如果 `.ai/project-context.html` 已存在，渲染脚本必须先把旧版本备份到 `.ai/drafts/project-context.<timestamp>.html`，再覆盖 `.ai/project-context.html`。备份最多保留 5 个，超过后删除最旧备份。生成完成后提示用户可执行 `rollback` 回退，并列出可回退版本（时间倒序）。

产物定位：

- 作为 `ledev-context` 阶段性输出，服务后续开发、review、测试、修复和文档维护时快速查阅。
- 设计定位是“离线工程上下文档案”：安静、可审计、可扫描、少装饰，像内部技术尽调材料或工程事实索引，不像网站首页、管理驾驶舱或美化报告。
- 只展示项目事实、已确认人工补充、未确认问题和风险边界；不展示依据路径、索引或内部来源标签；不按“新人、维护者、领导汇报”等读者画像组织文案。
- 不展示“更新时间”“面向读者”、内部 skill 名称、事实层状态、上下文阶段或模式名这类生成过程信息；如果需要记录生成、事实层或阶段状态，放入 `.ai/state/ledev-context.md`，不要放到 HTML 首屏或 footer。

信息编排要求：

- 优先使用事实层、长期 QA 和 Markdown 上下文中有依据的内容。
- 明确区分 confirmed facts、inferred assumptions、open questions 和 known risks。
- 状态标记必须同时使用文本和视觉样式表达含义，不能只靠颜色；confirmed、inferred、risk、open question 的语义色、边框或符号应保持一致。
- 首屏优先呈现一句话程序功能描述，以及来自代码主要组件、语言、框架、依赖清单、配置或导入路径的 3-6 个短标签；避免封面式 hero、读者画像、内部运行状态或汇报口径。
- 不复制 Markdown 文档结构；要按事实类别和后续工程查阅路径重新组织信息。
- 重要判断在生成过程中必须能追溯到事实文件、QA 编号、配置文件或代码路径，但最终 HTML 不展示这些内部依据。
- 不把未确认推断包装成确定结论；风险、约束和后续建议也要标注不确定性。
- 缺失和不确定内容使用固定表达：`未发现：...`、`未确认：...`、`open question: QA-### ...`、`不适用：...`。`missing` 只用于文件或阶段状态；正文不要使用 `none`。

生成流程：

1. AI 读取事实层、长期 QA、`.ai/project-context.md`、HTML 模板说明和脚本要求后，先生成 `.ai/drafts/project-context-html-data.json`。普通 `placeholders` 只能填纯文本；表格、列表、流程、模型、依赖和架构边界必须使用结构化字段，由脚本生成 HTML。
2. `html` 运行时以 `scripts/render_project_context_html.py` 为准：脚本从当前 `project-context-html-template.html` 提取所需 `{{PLACEHOLDER}}`，并执行结构自检。不要把 `templates/project-context-html-data-template.json` 当作运行时对齐标准；它只是 skill 开发参考。
3. 生成 JSON 时先阅读 `generation_notes`，尤其是 `topology_mapping`；根据目标项目类型把输入、程序本身、输出和运行时依赖组件映射到 `LEFT_TIER_*`、`ENGINE_*`、`RIGHT_TIER_*` 和 `BOTTOM_TIER_*`，不要被字段名里的 left/right 限制。架构图只放组件短名和极短关系；路径、QA、完整句子、工程支撑和代码边界不要进入最终 HTML。
4. 常规生成只修改 `.ai/drafts/project-context-html-data.json`；如果需要新增组件、调整结构、改 HTML/CSS 或改变布局，先修改 `templates/project-context-html-template.html`，再重新渲染。
5. `placeholders` 中的每个值都必须是面向 HTML 读者的事实摘要、QA 编号或明确的未确认说明；不要放入依据路径、内部索引或未转义 HTML 片段。`PROJECT_OWNED_SCOPE` 和 `PROJECT_OUT_OF_SCOPE` 是兼容旧字段，只允许纯文本；新数据必须使用 `project_owned_scope_items` 和 `project_out_of_scope_items`。
6. 运行 `scripts/render_project_context_html.py`，渲染到 `.ai/project-context.html`。如果正式 HTML 已存在，脚本会先自动备份旧版本到 `.ai/drafts/project-context.<timestamp>.html`，再覆盖正式文件。
7. 如果脚本报告缺失占位符、未替换占位符或缺少固定章节，必须先修正 `.ai/drafts/project-context-html-data.json` 或模板，再重新渲染。
8. 生成完成后，如果脚本创建了备份，向用户说明可以执行 `rollback` 回退，并展示脚本输出的备份列表。

推荐命令：

```sh
# 查看当前 HTML 模板实际需要的占位符：
python3 skills/ledev-context/scripts/render_project_context_html.py \
  --template skills/ledev-context/templates/project-context-html-template.html \
  --print-placeholders

python3 skills/ledev-context/scripts/render_project_context_html.py \
  --template skills/ledev-context/templates/project-context-html-template.html \
  --data .ai/drafts/project-context-html-data.json \
  --out .ai/project-context.html

# 如果 .ai/project-context.html 已存在，脚本会自动备份旧版后覆盖：
python3 skills/ledev-context/scripts/render_project_context_html.py \
  --template skills/ledev-context/templates/project-context-html-template.html \
  --data .ai/drafts/project-context-html-data.json \
  --out .ai/project-context.html
```

AI + 脚本职责边界：

- AI 负责事实归类、摘要、内部依据选择、风险和不确定性标注；内部依据不进入最终 HTML。
- 脚本负责确定性渲染、HTML 转义、模板占位符替换和结构自检。
- 不要让 AI 直接重写整份 HTML，除非脚本无法表达且用户明确要求临时手工修复。

HTML 固定章节：

1. 项目概述
2. 架构
3. 核心业务
4. 核心数据模型与状态机
5. 安全相关
6. 上下游和服务依赖
7. 配置项
8. 新人快速上手
9. 故障与恢复
10. 项目约定
11. 项目特化

章节内容要求：

- 项目概述：一句话定位和核心能力卡。一句话定位来自 `.ai/project-context.md` 的“1. 项目定位”；核心能力卡必须覆盖 `.ai/project-context.md` 的“5. 业务能力与模块划分”中的业务能力，不覆盖工程支撑能力；卡片只展示能力名称和一句话能力定位/解决的问题。关键代码和外部依赖放在后续业务或依赖章节。
- 架构：严格使用 `arch-html` 系统组件全景结构表达模块地图、调用方向、边界、入口、关键数据流和外部边界；可以替换节点名称和说明，但不要扩展或改写结构。中心必须是程序本身，例如项目名、主二进制、核心服务名或核心 runtime；左右列可映射输入/上游和输出/下游；底部只展示对运行链路重要的运行时依赖组件。不要强行套服务架构图，CLI、库、插件、monorepo、数据管道和工具项目可以按真实关系映射输入、程序本身、输出和运行时依赖。图中禁止写路径、QA、完整句子、工程支撑和代码边界；`go.mod`、`Makefile`、CI、lint、测试、dev scripts、generated/third-party 边界不要进入 HTML 架构图。
- 架构范围表：脚本从 `project_owned_scope_items` 和 `project_out_of_scope_items` 生成“项目负责范围/不负责范围”表格。每项使用 `{ "scope": "...", "description": "..." }`；不要把 HTML 表格字符串写入普通占位符。
- 核心业务：按 `.ai/project-context.md` “9. 关键业务流程”逐条渲染。每条流程必须有独立 `<h3>`、业务意图、脚本生成的 Mermaid `sequenceDiagram` 和轻量阶段卡片。参与方只允许外部触发源、本系统整体、直接外部下游或承载业务语义的消息/锁等中间件；内部类、Controller、Service、Task、Cache、Util、Manager、DB、配置中心和监控系统不要作为 Mermaid 参与方，相关细节折叠为本系统动作或阶段说明。
- 核心数据模型与状态机：基于 `.ai/project-context.md` “8. 核心数据与状态模型”生成 `data_domains`、`data_entities`、`data_relations`、`state_machine`，由脚本渲染为 Mermaid `flowchart TB` ER 图和 Mermaid `stateDiagram-v2` 状态机图。状态名优先保留中文名、枚举名和数值，展示为 `中文名(ENUM_NAME=数值)`；没有状态机时明确写“未发现：状态机”。最终 HTML 不展示证据、路径、QA 索引或内部来源。
- 安全相关：基于 `.ai/project-context.md` “10. 安全防控”生成 `security_controls`、`crypto_scenarios`、`security_concerns`，由脚本渲染为业务安全表、加密相关场景表和安全关注点。业务安全表只展示防控点、防什么、怎么防、失败结果；加密相关只展示场景、保护对象、加密/签名/脱敏手段、凭据托管概念级位置和失败结果；安全关注点用 `callout.warn`。最终 HTML 不展示证据、路径、QA 索引、具体凭据变量名、密钥值、算法参数明细、完整标准对照或审计打分。
- 上下游和服务依赖：脚本从 `dependency_links` 和 `external_dependencies` 生成 Mermaid `flowchart TB` 链路图；箭头标注方向、协议/方式和认证方式。不要把工程支撑依赖写成业务外部依赖。
- 配置项：只展示安全相关开关和控制项，表格必须包含“安全影响”；不渲染纯业务调参类配置。
- 新人快速上手：展示任务导向入口、适用场景、注意事项和建议阅读路径；不渲染完整代码导航索引、内部方法清单或大段路径清单。
- 故障与恢复：展示失败场景、触发条件、当前处理、恢复方式、观测信号和设计原则；不渲染具体实现缺陷、Bug、待修复项或代码问题。
- 项目约定：使用列表展示项目约定，每条为“加粗短语 + 一句话说明”；不展开完整代码导航索引、内部方法清单或大段路径列表。
- 项目特化：使用差异矩阵展示多场景、多实现、部署环境、集成方式或项目独有规则之间的差异，并保留 Human Notes 和 Corrections 的简洁结论。

设计风格：

- `templates/project-context-html-template.html` 是脚本渲染输入、当前样式基线和可直接打开的调试参考；它可以演进，但不要只修改单次生成产物。
- 生成 `.ai/project-context.html` 前必须先读取 `templates/project-context-html-template.md` 和 `templates/project-context-html-template.html`；需要确认字段集合时运行 `scripts/render_project_context_html.py --print-placeholders`。`project-context-html-data-template.json` 只作为 skill 开发参考，不参与运行时一致性判断。
- 后续调整 HTML/CSS/布局时，优先修改 `project-context-html-template.html`，再用脚本重新渲染；不要只修改单次生成的 `.ai/project-context.html`，避免模板和产物漂移。
- 允许按项目事实增删内容块、调整组件和局部样式，但这些结构和样式变化应落到模板文件；不要改成营销页、对外汇报页或无依据的信息图。
- `frontend-design` 和 `ui-ux-pro-max` 可以用于检查可读性、响应式、信息层级和无障碍细节；如果本地不存在这些参考，继续按当前 HTML 模板和脚本生成，不安装、不阻塞。
- 页面应服务阅读和查阅，不做营销落地页。避免空泛 hero、装饰性堆叠卡片、过度渐变和无信息量图形。
- 可以使用单文件 HTML，内联 CSS 和少量原生 JavaScript。业务时序、数据模型、状态机和依赖链路使用固定版本 `mermaid@10.9.6`；Mermaid 源必须由脚本从结构化 JSON 生成，脚本负责字符清理和关键字规避，AI 不直接手写 Mermaid。脚本还必须从同一份结构化 JSON 生成图的无障碍短摘要；Mermaid 加载失败时保留图源和 fallback 提示。
- 样式应保证移动端和桌面端都可读，正文宽度受控，表格和宽图都可横向滚动，长路径和命令不溢出。
- 如果生成图示，优先用 HTML/CSS 或内联 SVG 表达真实架构关系；不要为了美观编造不存在的模块或流程。

脚本自检：

生成自检：

- 固定 11 个主章节、两位编号导航、状态标记、移动端和打印样式都必须存在。
- 脚本不得残留未替换的 `{{PLACEHOLDER}}`。
- 如果为了项目信息新增组件或调整样式，应同步修改 `project-context-html-template.html`，让后续生成产物自动继承最新模板。

写入成功后，才能把阶段锚点推进到 `html`。

## Rollback

恢复最近的 HTML 备份。

行为规则：

- 只处理 `.ai/project-context.html` 的备份，备份文件匹配 `.ai/drafts/project-context.<timestamp>.html`。
- 先按时间倒序列出最多 5 个备份，并让用户选择要恢复的版本；不要在没有用户选择时覆盖正式 HTML。
- 用户选择后，把当前 `.ai/project-context.html` 也按新时间戳备份到 `.ai/drafts/`，再用所选备份覆盖 `.ai/project-context.html`。
- 恢复完成后报告当前文件和所用备份路径。
- rollback 是恢复动作，不修改事实层、Markdown 文档或 QA 文档。

## Document

组合执行文档阶段，默认顺序：

1. `md`
2. `html`

行为规则：

- 默认先执行 `md` 的刷新/提升流程，再执行 `html`。不要因为 `.ai/project-context.md` 文件存在或事实层未变化就跳过 `md`。
- 如果现有 `.ai/project-context.md` 经检查已经完全符合当前 `templates/project-context-template.md`、当前事实层和长期 QA，且用户明确要求只刷新 HTML，才可以跳过 Markdown 写入；仍要在输出中说明“MD 已校验，无需改动”。
- 如果 Markdown 模板、HTML 模板或 HTML 结构化数据需求近期发生变化，现有 `.ai/project-context.md` 必须按当前模板重新生成或维护；模板结构变化本身就构成 Markdown stale。
- 如果 `.ai/project-context.html` 已存在，`html` 会自动备份旧版后覆盖正式 HTML，并在输出中提示可用 `rollback` 回退。
- `document` 只有在 `md` 和 `html` 都完成后，才能把阶段锚点推进到 `document`。
- 如果用户要求只生成 Markdown，用 `md`；只生成 HTML，用 `html`。

## Maintain

根据用户纠正或项目变化，增量维护事实层、上下文和文档。

必须保留：

- `Human Notes`
- `Corrections`
- 仍然相关的 QA answers

维护时如果存在 `.ai/qa/project-qa.md`，要读取它。若新代码事实和已有 QA 答案冲突，追加描述冲突的新问题并请求确认，不要静默改写旧答案。

发现代码变化时，先更新 `.ai/facts/` 中受影响的事实文件，再更新 `.ai/project-context.md`、QA、人类文档或 `.ai/state/ledev-context.md`。多仓库上下文中，如果 Related repo 的 checkout、dirty 状态或解析版本变化影响 Primary repo 理解，先更新 `.ai/facts/related-repos.md` 和相关依赖事实。

如果代码事实和人工补充冲突，记录冲突并询问用户。

写文件前确认目标文件，除非用户已经明确要求写入。

维护更新写入成功后，才能把阶段锚点推进到 `maintain`。

## Full

按阶段执行：

1. Scope
2. Scan
3. Summarize
4. QA
5. md
6. html

写正式文件前暂停；scope 确认前暂停；问题超过 10 个前暂停。

不要跳过阶段锚点规则。

## 推荐输出

AI 工作上下文：

- `.ai/facts/`
- `.ai/project-context.md`
- `.ai/project-context.html`

运行进度状态：

- `.ai/state/ledev-context.md`
- `.ai/state/<skill-name>.md` for each other skill, for example `.ai/state/ledev-task.md` or `.ai/state/ledev-test.md`

长期 QA：

- `.ai/qa/project-qa.md`

人类文档，按需生成：

- `.ai/project-context.html`
- `docs/architecture.md`
- `docs/development.md`
- `docs/testing.md`
- `docs/module-map.md`

如果目标项目不应该被写入，也可以放到用户指定的外部位置。
