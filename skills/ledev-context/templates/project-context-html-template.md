# 项目 HTML 文档模板

用于生成 `.ai/ledev/project-context.html`。正文以中文为主；命令、路径、代码标识、配置项、状态值可保留英文。

同目录下的 `project-context-html-template.html` 是可直接在浏览器打开的单文件 HTML 模板，用于脚本渲染输入、当前样式基线和样式调试参考。它可以随项目文档需求演进；但所有 HTML/CSS/布局调整都应该优先落到该模板，再由脚本重新渲染 `.ai/ledev/project-context.html`，避免只改单次生成产物导致模板和产物漂移。

默认使用 AI + 脚本流程：

1. AI 基于 `.ai/ledev/facts/`、`.ai/ledev/qa/project-qa.md` 和 `.ai/ledev/project-context.md` 生成 `.ai/ledev/drafts/project-context-html-data.json`。
2. `html` 运行时以 `scripts/render_project_context_html.py` 为准。脚本从当前 HTML 模板提取所需 `{{PLACEHOLDER}}` 并执行结构自检；需要查看字段集合时运行 `--print-placeholders`。`project-context-html-data-template.json` 只是 skill 开发参考，不作为运行时对齐标准。
3. 生成 JSON 时根据项目类型把真实关系映射到输入关系带、程序本身、输出关系带和运行时依赖组件；不要被 `LEFT_TIER_*`、`RIGHT_TIER_*` 的字段名限制为传统左右服务拓扑。
4. 常规生成只修改 `.ai/ledev/drafts/project-context-html-data.json`；新增组件、调整结构、改 HTML/CSS 或改变布局时，先修改 `project-context-html-template.html`。
5. 运行 `scripts/render_project_context_html.py`，由脚本读取本 HTML 模板、替换占位符、执行 HTML 转义和结构自检，并写入 `.ai/ledev/project-context.html`。如果正式 HTML 已存在，脚本先把旧版备份到 `.ai/ledev/drafts/project-context.<timestamp>.html`，再覆盖正式文件；备份最多保留 5 个。
6. 脚本报错时，优先修正中间 JSON 或模板；不要绕过脚本直接重写整份 HTML。

模板和脚本规则：

- `project-context-html-template.html` 应保留可直接打开调试的完整 HTML。
- 允许替换占位内容；如需复制并填充已有组件、按事实内容增删内容块或调整样式，应修改 `project-context-html-template.html`，再重新渲染。
- 如果后续要调整视觉样式、响应式布局或章节组件，先修改该模板，再用 `scripts/render_project_context_html.py` 生成正式 `.ai/ledev/project-context.html`。
- 写入前必须自检固定 11 个主章节、两位编号导航、状态标记、移动端和打印样式都存在。

`project-context.html` 不是 `.ai/ledev/project-context.md` 的简单翻译，也不是对外汇报页、营销页或按读者画像包装的展示文档。它是 `.ai/ledev/` 下的阶段性项目上下文产物，必须基于 `.ai/ledev/facts/`、`.ai/ledev/qa/project-qa.md` 和 `.ai/ledev/project-context.md` 重新编排信息，服务后续开发、review、测试、修复和文档维护时快速查阅。

本 HTML 的设计定位是“离线工程上下文档案”：安静、可审计、可扫描、少装饰。它应该像一份内部技术尽调材料或工程事实索引，而不是网站首页、管理驾驶舱或美化报告。设计优先级依次是：项目理解效率、事实可信度、状态可见、工程查阅路径、视觉记忆点。

设计原则：

- 事实优先：重要结论必须来自事实层或长期 QA；依据用于生成判断，但最终 HTML 不展示依据路径、索引或内部来源标签。
- 状态可见：confirmed、inferred、risk、open question 必须能通过文字、颜色和边框形态共同区分，不能只依赖颜色。
- 工程查阅优先：首屏优先让读者知道“这个程序做什么”，使用一句话功能描述和少量主要组件/外部依赖标签；细节索引放入对应主题章节，不再单独设置收尾索引章节。
- 密度有层级：允许高信息密度，但要用编号、表格、代码路径、状态标记和标题下结构线组织阅读节奏。
- 本地可信：除固定 Mermaid 运行时外不引入外部网络依赖；网络不可用时图源和 fallback 提示仍可读，生成物可打开、打印和长期追溯。

缺失和不确定内容使用固定表达：

- `未发现：...` 表示已检查相关事实范围但没有观察到该内容。
- `未确认：...` 表示当前事实层不足，不能写成确认事实。
- `open question: QA-### ...` 表示需要人工回答或已有长期 QA 编号。
- `不适用：...` 表示该项目类型天然不需要该内容，并说明原因。
- `missing` 只用于文件或阶段状态；正文里不要用 `none`。

HTML 中只展示项目事实、已确认人工补充、未确认问题和风险边界；不要展示依据路径、索引、内部来源标签、“更新时间”“面向读者”、内部 skill 名称、事实层状态、上下文阶段或模式名这类生成过程信息。如果需要记录生成时间、事实层状态或阶段状态，放入 `.ai/ledev/state/ledev-context.md`，不要放到 HTML 首屏或 footer。

## 前置检查

生成前必须确认：

- `.ai/ledev/facts/manifest.md` 存在，且事实层不是明显 stale。
- `.ai/ledev/project-context.md` 存在，且已经由 `md` 生成或维护到当前事实层和当前 `project-context-template.md` 结构。
- `.ai/ledev/project-context.md` 包含 HTML 所需的结构化来源：业务能力、关键业务流程、数据域、核心对象、数据关系、状态机/状态流转、业务安全、加密相关、安全关注点、外部依赖与集成、配置与控制、新人快速上手、失败与恢复机制。缺少这些来源时，先执行 `ledev-context md`，不要只刷新 HTML。
- `.ai/ledev/qa/project-qa.md` 已读取；没有 QA 文档时明确记录为 missing，不编造人工结论。
- `.ai/ledev/project-context.html` 已存在时，脚本必须先自动备份旧版到 `.ai/ledev/drafts/project-context.<timestamp>.html`，再覆盖正式文件；生成完成后提示用户可执行 `rollback` 回退，并列出可回退版本。

如果 Markdown 文档缺失或 stale，先完成 `ledev-context md`。

## 固定章节

HTML 必须包含以下章节，章节可有子标题，但不要省略主章节：

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

## 章节说明

### 章节说明表

章节说明表适合放在模板说明或生成规则中，不建议放入最终 HTML 主体。推荐字段为：编号、章节名、内容来源、主要组件、内容说明、补充说明。这个表可用于开发和维护模板，帮助确认每个章节从 `.ai/ledev/project-context.md`、事实层、QA 或依赖清单中取什么内容；最终 HTML 应优先展示项目事实本身。

| 编号 | 章节名 | 内容来源 | 主要组件 | 内容说明 | 补充说明 |
| --- | --- | --- | --- | --- | --- |
| 01 | 项目概述 | `.ai/ledev/project-context.md` 的“1. 项目定位”和“5. 业务能力与模块划分”，必要时补充 QA 结论 | `PROJECT_POSITIONING`、`CORE_CAPABILITY_*_NAME`、`CORE_CAPABILITY_*_SUMMARY` | 展示一句话定位和核心能力卡。卡片只放能力名与一句话说明。 | 首屏只承载项目理解摘要：一句话程序功能描述和 3-6 个主要语言、框架、内部组件或外部依赖标签；标签必须来自事实层、依赖清单、配置、导入路径或项目上下文。不要放读者画像、运行阶段、事实层状态、skill 阶段或长句。 |
| 02 | 架构 | `.ai/ledev/project-context.md` 的“3. 架构总览”、事实层架构事实、依赖和边界事实 | `arch-html`、`arch-html-label`、`arch-mid`、`arch-col`、`arch-engine`、`arch-engine-head`、`arch-engine-grid`、`arch-svc-row-label`、`arch-svc-row`、`SCOPE_BOUNDARY_HTML` | 严格使用模板 HTML 中的固定骨架画系统组件全景：外层 `arch-html`、标签、三列中段、中心 engine、底部服务行；只替换节点内容和占位符，不新增结构层级。项目负责范围和不负责范围由脚本从 `project_owned_scope_items`、`project_out_of_scope_items` 生成表格。 | 中心 `arch-engine` 必须展示程序本身，例如项目名、主二进制、核心服务名或核心 runtime；左右列只展示围绕程序本身的上游/输入侧和下游/输出侧组件短名；底部行只放运行时依赖组件。图中禁止写路径、QA、长句、构建工具、测试工具、dev scripts、generated/third-party 边界。`FLOW` 必须是 1-3 个动词，所有 `NOTE` 约 6-10 字、简单干练。缺失关系不要编造，写“未确认”。架构图下方必须保留“项目负责范围”和“不负责范围”表；不要把 HTML 字符串放入 `PROJECT_OWNED_SCOPE` 或 `PROJECT_OUT_OF_SCOPE`。 |
| 03 | 核心业务 | `.ai/ledev/project-context.md` 的“9. 关键业务流程”，必要时参考“5. 业务能力与模块划分”和长期 QA | `BUSINESS_FLOWS_HTML`、Mermaid `sequenceDiagram`、阶段卡片、`BUSINESS_CONFIDENCE` | 按业务流程逐条展示：每条流程独立标题、业务意图、脚本生成的时序图和轻量阶段卡片，避免把未经确认的业务推断写成事实。 | 参与方只允许外部触发源、本系统整体、直接外部下游或承载业务语义的消息/锁等中间件；内部类、Controller、Service、Task、Cache、Util、Manager、DB、配置中心和监控系统不要作为 Mermaid 参与方。 |
| 04 | 核心数据模型与状态机 | `.ai/ledev/project-context.md` 的“8. 核心数据与状态模型”、事实层模型事实、枚举/状态事实和必要 QA | `MODEL_HTML`、Mermaid `flowchart TB` ER 图、Mermaid `stateDiagram-v2` 状态机图、`STATE_MACHINE_STATUS` | 按数据域、核心对象、对象关系、状态机和状态流转渲染为图；没有状态机时明确写未发现。 | HTML 数据来自 `data_domains`、`data_entities`、`data_relations`、`state_machine`。状态名优先保留中文名、枚举名和数值，展示为 `中文名(ENUM_NAME=数值)`。最终 HTML 不展示证据、路径、QA 索引或内部来源；字段级大表、DDL、包路径和方法签名只用于判断，不进入页面主体。 |
| 05 | 安全相关 | `.ai/ledev/project-context.md` 的“10. 安全防控”、配置事实、依赖事实、QA | `SECURITY_HTML`、`security-blocks`、`security-controls`、`crypto-scenarios`、`security-concerns`、`SECURITY_STATUS` | 展示业务安全表、加密相关场景表和安全关注点；依据不足时标注未确认。 | HTML 数据来自 `security_controls`、`crypto_scenarios`、`security_concerns`。业务安全表字段为防控点、防什么、怎么防、失败结果；加密相关只展示场景、保护对象、加密/签名/脱敏手段、凭据托管概念级位置和失败结果；关注点用 `callout.warn`。最终 HTML 不展示证据、路径、QA 索引、具体凭据变量名、密钥值、算法参数明细、完整标准对照或审计打分。 |
| 06 | 上下游和服务依赖 | `.ai/ledev/project-context.md` 的“12. 外部依赖与集成”、依赖事实、架构事实 | `DEPENDENCIES_HTML`、Mermaid `flowchart TB` 链路图 | 展示上下游服务、运行时外部依赖、调用方向、协议/方式、认证方式和失败传播。 | 链路图箭头必须标注方向、协议和认证方式；只记录运行时真实交互，不渲染 `go.mod`、`Makefile`、CI、lint、测试、dev scripts、generated 或 third-party 目录边界。 |
| 07 | 配置项 | `.ai/ledev/project-context.md` 的“11. 配置与控制”、配置事实、长期 QA | `CONFIGURATION_HTML`、安全相关开关精简表 | 仅展示安全相关开关和控制项，表格必须包含“安全影响”。 | 不渲染纯业务调参类配置，例如阈值、上限、批大小、展示配置。配置项默认值、具体凭据变量名和细节参数留在 Markdown。 |
| 08 | 新人快速上手 | `.ai/ledev/project-context.md` 的“7. 新人快速上手”、事实层模块入口、命令事实、长期 QA | `ONBOARDING_HTML`、上手任务卡、入口表、阅读路径列表 | 帮新人建立系统心智模型，快速知道先看哪里、改哪里、排障从哪里入手。 | 不渲染完整代码导航索引、内部方法清单或大段路径清单；只保留任务导向入口和注意事项。 |
| 09 | 故障与恢复 | `.ai/ledev/project-context.md` 的“13. 失败与恢复机制”、测试事实、错误处理事实、QA | `RECOVERY_HTML`、失败场景表、设计原则 `callout.info` | 展示失败场景、触发条件、当前处理、恢复方式、观测信号和设计原则。 | 失败场景聚焦系统设计的容错机制，不渲染具体实现缺陷、Bug、待修复项或代码问题。 |
| 10 | 项目约定 | `.ai/ledev/project-context.md` 的“16. 项目约定”、事实层边界、测试和命令事实 | `PROJECT_CONVENTIONS_HTML`、`<ul>` | 使用列表展示项目约定，每条为“加粗短语 + 一句话说明”。 | 可包含目录、命名、错误处理、日志、测试、生成代码和不要修改区域；不展开完整代码导航索引、内部方法清单或大段路径列表。 |
| 11 | 项目特化 | `.ai/ledev/project-context.md` 的“14. 多场景/多实现的差异矩阵”和“17. 其他”、Human Notes、Corrections | `PROJECT_SPECIFICS_HTML`、差异矩阵表 | 展示多场景、多实现、部署环境、集成方式或项目独有规则之间的差异。 | 差异矩阵字段为场景/实现、适用条件、入口、关键差异、依赖、风险；刷新时必须保留 Human Notes 和 Corrections 的简洁结论。 |

## 设计风格

默认采用适合阶段性项目上下文的工程档案风格：

- 单文件纯 HTML 优先，CSS 内联，少量原生 JavaScript 可用于导航高亮、打印等轻量交互；默认不需要 React、Vue、Next.js 或构建链。
- 默认模板采用固定导航的极简项目文档布局：固定顶部 header、固定左侧 sidebar、正文最大宽度约 `900px`、大量留白、清晰章节分隔、表格和架构图承载高密度信息。后续可按项目需要调整布局，但要同步修改 `project-context-html-template.html`。
- 信息密度适中，适合工程查阅和后续任务复用；留白要舒服，但章节、表格和风险区域必须有清晰结构。
- 首屏只承载项目理解摘要：文档类型小字、项目名称、一句话程序功能描述，以及 3-6 个来自主要组件、语言、框架或外部依赖的小号标签。不要展示更新时间、面向读者、内部 skill 名称、事实层状态、模式名、过多操作按钮或大面积统计卡片。
- 默认使用固定左侧 sidebar 作为主导航；移动端可退化为顶部后展开或自然堆叠。导航宽度参考 `260px`，背景使用极浅灰，正文区域保留纯白。
- 顶部 header、左侧 sidebar 和正文 hero 不要重复展示同一个项目名。默认只在正文 hero 使用项目名；header 只展示文档类型或文件名；sidebar 展示 `Contents` 或“章节导航”。
- 导航目录和正文主章节标题都要带两位编号，例如 `01 项目概述`、`02 架构`，方便快速定位；编号必须和固定章节顺序一致。正文标题结构应使用独立编号元素，例如 `<span class="section-num">01</span><h2>项目概述</h2>`，不要把编号直接拼进标题文本。
- 左侧 sidebar 和正文之间必须保留明确横向留白。桌面端正文容器不应贴着导航边界，主内容区域应在 sidebar 之后再留出至少 `48px` 左右的视觉缓冲。
- 用状态标记区分 confirmed、inferred、risk、open question。状态标记不能只靠颜色表达，还要通过文本标签、边框样式或小型符号区分；confirmed 偏稳态，inferred 偏待确认，risk 偏阻断或风险，open question 偏待人工回答。状态样式 class 由脚本根据状态文案归类，不要在 JSON 中手动拼 class。
- 用表格、定义列表、时间线、流程图或架构图承载结构化信息。
- 风险和演进方向要突出，但必须有事实依据或明确标注为建议。
- 默认颜色以纯白和极浅暖白为主，导航背景应比正文略暗、略退后，不能比正文更白亮。避免渐变背景和大面积色块，让内容成为主角。
- 建议定义一个易于手动修改的主题色变量，默认命名为 `--theme`。主要高亮优先体现在文字、代码、当前导航、左边线、边框或小型状态标记上；少用背景色高亮。
- 状态标记默认也应克制，优先使用浅底、语义色文字和细边框；只有安全风险等必须区分的内容才使用更强的语义色，且不要大面积铺色。
- 导航 hover 和当前章节状态必须克制：使用原导航底色加灰的低对比整行矩形，高亮横向铺满导航栏宽度，文字使用主题色并加粗；不使用局部胶囊形按钮，也不使用过深或过亮的强调色。
- 字体要偏温和、适合中文长文阅读。标题可用宋体/衬线增强企业文档质感，正文优先使用圆润清晰的中文无衬线或本地阅读字体；不依赖外部字体服务。
- 动效只服务“顺滑性”，不服务表演。允许 smooth scroll、导航 hover、当前章节定位、表格行 hover、按钮/链接/卡片的颜色、边框和阴影过渡；不使用入场动画、滚动 reveal、视差、循环动画或会消耗注意力的装饰动效。所有动效必须支持 `prefers-reduced-motion`，且不能成为理解内容的必要条件。
- 视觉节奏应有清晰的停顿和轻重：首屏快速定位，章节之间主要依靠稳定留白，不额外添加章节前后分割线；章节标题下保留结构线，架构/表格区域可以更密但必须有明确锚点，普通段落和摘要留出阅读呼吸。
- 避免营销式 hero、空泛装饰、过度渐变、无信息图形、大段无结构文本和过于紧凑的表格堆叠。
- 标签使用小号方角 chip：mono 字体、低高度、4px 左右圆角、浅灰底或白底、主题色文字；不要使用大号胶囊标签。
- Mermaid 图使用固定版本 `mermaid@10.9.6` 渲染。图源必须由 `scripts/render_project_context_html.py` 从结构化 JSON 生成，AI 不直接手写 Mermaid；脚本负责 id、participant、label 的字符清理和 Mermaid 关键字规避，并从同一份结构化 JSON 生成图的无障碍短摘要。图容器必须支持横向滚动；网络不可用时 `<pre class="mermaid">` 中的图源和 fallback 提示保留为可读降级内容。
- 响应式布局必须可读：长路径、命令、表格不能溢出；移动端导航不能遮挡正文。
- 可打印：打印时隐藏交互控件，保留章节层级、表格和导航索引。

可参考本地已安装的 `frontend-design` 或 `ui-ux-pro-max` 设计规则检查可读性、响应式、信息层级和无障碍细节；这些规则不得覆盖本 HTML 范本的结构和视觉主题。如果没有安装，使用上述默认风格继续生成，不安装、不阻塞文档。

## 输出质量门槛

写入前自检：

- 固定 11 个主章节都存在。
- `scripts/render_project_context_html.py` 已成功执行，且没有未替换占位符或缺失固定章节。
- 样式或布局变化已经同步到 `project-context-html-template.html`，不是只改了单次生成产物。
- 重要结论来自事实层或长期 QA，且没有把内部依据路径展示到 HTML。
- `.ai/ledev/project-context.md` 中的 Human Notes、Corrections 和关键 QA 结论没有丢失。
- HTML 中没有把 inferred assumptions 写成 confirmed facts。
- 除固定 Mermaid 运行时外，页面无外部网络依赖；Mermaid 加载失败时必须保留可读 fallback。
- CSS 对移动端、桌面端和打印都有基本处理。
- 已存在 `.ai/ledev/project-context.html` 时，脚本先备份旧版到 `.ai/ledev/drafts/project-context.<timestamp>.html`，再覆盖 `.ai/ledev/project-context.html`；运行后必须提示可用 `rollback` 回退。
