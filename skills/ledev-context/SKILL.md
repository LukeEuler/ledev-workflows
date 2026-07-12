---
name: ledev-context
description: 面向中文用户。用于在开发、review、bugfix、测试或工具生成前，先确认扫描范围，再全量观察代码并建立结构化事实层，随后基于事实层建立、刷新、纠正可复用的项目上下文和项目文档。支持 scope、scan、summarize、qa、md、html、document、maintain、full 等模式。产出以中文为主，包括 .ai/ledev/scope/ 扫描范围、.ai/ledev/facts/ 事实库、AI 工作上下文、Markdown/HTML 项目文档、长期 QA 文档、Human Notes、Corrections 和 Open Questions。
---

# Project Context Builder

## 目的

在开发、review、bugfix、测试或工具生成之前，先建立一层可复用的项目知识。

这个 skill 维护四层项目知识：

- 范围层：确认扫描范围、排除项和仓库形态。
- 事实层：全量观察代码和仓库文件，记录可验证事实。
- 上下文层：基于事实层和长期 QA 生成 AI 工作上下文。
- 文档层：把稳定、已确认的信息沉淀为 Markdown/HTML 项目文档。

支持单仓库、monorepo，以及“主仓库 + 关联仓库”的多仓库上下文。多仓库上下文必须有且只有一个 `Primary repo`；其他仓库只能作为 `Related repos` 写入主仓库 `.ai/ledev/` 产物，除非用户明确要求跨仓写入。

## 中文优先规则

遵循 `../_shared/references/shared-rules.md`；本 skill 额外要求 QA 问题、草稿、最终上下文和人类文档中的说明性内容以中文为主。

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
- 把本机绝对路径写入长期产物，例如 `.ai/ledev/scope/`、`.ai/ledev/facts/`、`.ai/ledev/qa/`、`.ai/ledev/project-context.md`、`.ai/ledev/project-context.html` 或人类文档。
- 在事实层做业务推理或意图猜测
- 把不确定推断写成确认事实
- 在没有证据的情况下写“核心”“主要”“推荐”等判断
- 把本地关联仓库的当前 checkout 直接当成主仓库实际依赖版本，除非 `go.work`、`replace`、workspace、lockfile 或构建配置能证明实际解析到该路径。

## 读取 Reference

只读取当前模式需要的 reference：

- 跨 LEDev skill 的中文优先、git、`.ai/ledev/`、路径可移植性和多仓库默认边界：读 `../_shared/references/shared-rules.md`。
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

- AI 只生成 `.ai/ledev/drafts/project-context-html-data.json` 中的纯文本占位符；脚本 `scripts/render_project_context_html.py` 负责读取模板、HTML 转义、占位符替换和结构自检。
- HTML 中需要表格、列表、流程、模型、依赖或架构边界时，AI 必须生成结构化 JSON 字段，由脚本生成 HTML；不要把 `<table>`、`<tr>`、`<div>` 等 HTML 字符串塞进普通占位符。
- `templates/project-context-html-data-template.json` 只是 skill 开发参考，不作为 `html` 运行时标准；运行时字段集合以脚本从当前 HTML 模板提取的占位符为准。
- 如果 `.ai/ledev/project-context.html` 已存在，脚本先把旧版本备份到 `.ai/ledev/drafts/project-context.<timestamp>.html`，再直接覆盖正式文件；备份最多保留 5 个，超过后删除最旧备份。
- HTML/CSS/布局调整必须先修改 `templates/project-context-html-template.html`，再重新渲染；不要只修改单次生成产物。
- 最终 HTML 固定 11 个主章节，区分事实、推断、风险和开放问题；生成判断需要内部依据，但 HTML 不展示证据路径、证据索引或内部来源标签。

## 操作入口

遵循共享 operation 规则。`ledev-context` 的 operation 对外称为 mode；把 skill 名称后的第一个词视为 mode。Codex 示例使用 `$ledev-context`，Claude Code 示例使用 `/ledev-context`。mode 大小写不敏感；面向用户展示命令时优先用小写。

推荐顺序：

1. `scope`
2. `scan`
3. `summarize`
4. `qa`
5. `md`
6. `html`
7. `document`
8. `status`
9. `refresh`
10. `maintain`

支持模式：

- `default`：说明可用模式和副作用；不扫描、不运行命令、不写文件。
- `scope`：轻量发现仓库规模、语言、目录和排除项，写入 `.ai/ledev/scope/scan-scope.md` 并请求用户确认。
- `scan`：读取已确认 scope，全量观察代码和仓库文件，建立 `.ai/ledev/facts/` 结构化事实层；除非 dry-run/no-write，否则写入事实文件。
- `summarize`：基于 `.ai/ledev/facts/` 和长期 QA 生成 `.ai/ledev/drafts/project-context-draft.md`。
- `qa`：维护 `.ai/ledev/qa/project-qa.md`，使用稳定 `QA-###` 编号；用户可编辑文件或按编号 inline 回答。
- `md`：把已确认草稿和 QA 结论提升到 `.ai/ledev/project-context.md`、`.ai/ledev/state/ledev-context.md` 或 Markdown 人类文档。
- `html`：基于事实层、长期 QA 和 `.ai/ledev/project-context.md` 重新编排信息，生成 `.ai/ledev/project-context.html`。
- `rollback`：列出 `.ai/ledev/drafts/project-context.<timestamp>.html` 备份，按时间倒序让用户选择版本并恢复到 `.ai/ledev/project-context.html`。
- `document`：默认组合执行 `md` 和 `html`；先刷新或校验 `.ai/ledev/project-context.md` 是否符合当前 Markdown 模板，再生成 HTML。
- `status`：只读检查当前代码、scope、事实层、上下文和文档是否相对上次源码快照过期；不写文件，输出 stale 级别和推荐刷新命令。
- `refresh`：根据源码快照和 stale 级别刷新受影响的 scope、事实层、草稿、QA、Markdown 和 HTML；默认最小必要刷新，`refresh --full` 强制按完整链路重建。
- `maintain`：根据用户纠正或项目变化增量维护上下文，保留 `Human Notes` 和 `Corrections`。
- `full`：按 scope、scan、summarize、qa、md、html 分阶段执行；写正式文件前暂停，问题超过 10 个前暂停。

示例：

- Codex：`$ledev-context scope`
- Claude Code：`/ledev-context scope`
- `ledev-context scan`
- `ledev-context summarize`
- `ledev-context qa`
- `ledev-context md`
- `ledev-context html`
- `ledev-context rollback`
- `ledev-context document`
- `ledev-context status`
- `ledev-context refresh`
- `ledev-context maintain`
- `ledev-context full`

## 核心硬性规则

- 用户显式指定某个模式时，本次运行必须执行该模式；不要因为状态锚点已在后续阶段就自动跳过或改跑下一阶段。
- `scope` 是正式第一阶段；`scan` 必须基于已确认且未 stale 的 `.ai/ledev/scope/scan-scope.md`。
- `.ai/ledev/facts/` 是后续 AI 逻辑的基准数据源；`summarize`、`qa`、`md`、`html`、`document` 和 `maintain` 都必须先读取相关事实文件。
- 事实层只记录可观察事实和证据；最终上下文和文档必须区分 Confirmed Facts、Inferred Assumptions、风险和开放问题。
- 分阶段工作时，在 `.ai/ledev/state/ledev-context.md` 维护本 skill 的阶段锚点；不允许跳过未完成阶段向后推进锚点。阶段锚点合法值见 `references/modes.md` 的“阶段锚点”段。
- `status` 和 `refresh` 使用 `.ai/ledev/state/ledev-context.md` 与 `.ai/ledev/facts/manifest.md` 中的源码快照判断 stale；快照缺失时必须明确说明只能做保守判断。
- `md` 必须以当前 `templates/project-context-template.md` 为结构标准；`html` 必须基于当前事实层和符合模板的 `.ai/ledev/project-context.md`。
- `html`、`document` 和 `full` 默认通过 `scripts/render_project_context_html.py` 渲染 HTML；不要把 AI 生成的 HTML 字符串塞进普通占位符。
- QA 是文件优先、长期维护的项目知识。新问题使用稳定 `QA-###` 编号，过期问题标记 `obsolete`，不删除后复用编号。
- 刷新和维护时必须保留 `Human Notes` 和 `Corrections`；人工补充和代码事实冲突时，记录冲突并向用户确认。

详细启动检查、写入规则、阶段锚点、QA 合并、rollback、HTML 生成和 maintain 流程见对应 reference；不要在 SKILL.md 中重复展开。
