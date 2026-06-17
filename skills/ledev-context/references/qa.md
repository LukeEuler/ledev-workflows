# Project Context Builder QA

用于 `ledev-context qa` 模式。所有 QA 运行产物以中文为主；命令、路径、字段名、状态值和 QA 编号可以保留英文。

短确认答案和短命令使用英文 token，例如 `yes/no`、`defer`、`not-applicable`、`continue/stop`；可以用中文说明含义，但不要要求用户输入中文短命令。

## 交互模型

QA 是文件优先、长期维护的项目知识。

当需要提问时：

1. 如果存在 `.ai/qa/project-qa.md`，先读取。
2. 除非用户要求 dry-run/no-write，否则把新增或更新问题写入 `.ai/qa/project-qa.md`。
3. 终端输出保持简短。
4. 提示用户可以编辑文件回答，也可以按 QA 编号 inline 回答。

终端只输出：

- QA 文件路径
- 问题编号和短标题
- 回答方式

不要在终端完整打印每个详细问题，除非用户要求 terminal-only。

QA 文档是项目上下文和人类文档的长期补充。它保存详细的人类回答、决策、未解决问题和冲突追问。最终上下文或正式文档可以总结 QA 结论，但不能替代完整 QA 记录。

## 存储位置

主 QA 文档：

```text
.ai/qa/project-qa.md
```

不要把 active QA 存到 `.ai/drafts/`。drafts 只用于临时 scan 和 summarize 输出；QA answers 是长期项目知识。

## 编号规则

- 每个问题必须有稳定编号：`QA-001`、`QA-002` 等。
- 追加或重生成问题时，从 `.ai/qa/project-qa.md` 中已有最大编号继续递增。
- 问题展示给用户后，不允许重编号。
- 不复用已删除或 obsolete 的编号。
- 过期问题标记为 `Status: obsolete`。

## 问题结构

每个 QA 条目都要能脱离终端独立阅读。

使用这个结构：

```md
### QA-001: 简短问题标题

- Status: pending | answered | deferred | not-applicable | obsolete
- Required: yes | no
- Related:
- Context: 触发该问题的仓库事实、草稿推断、既有 QA 或冲突点。
- Why it matters: 这个回答会如何影响上下文、文档、命令、模块边界或风险记录。
- Requested answer format: 简短文本、命令列表、路径列表、带说明的 `yes/no`，或 `not-applicable`。
- Answer:
- Answer source: file edit | inline reply | prior human note
- Last updated:
- Promoted to:
```

## 答案处理

接受按编号 inline 回答，例如：

```text
QA-001: 这个项目用于维护 Codex skill 工作流。
QA-003: not-applicable.
```

允许写文件时：

- 把 inline answers 合并回 `.ai/qa/project-qa.md`。
- 根据答案设置 `Status: answered`、`deferred` 或 `not-applicable`。
- 设置 `Answer source: inline reply`。
- 更新 `Last updated`。

用户直接编辑 `.ai/qa/project-qa.md` 时：

- 继续前先读取文件。
- 保留用户在 `Answer` 中的原文。
- 如果缺失，补充 `Answer source: file edit`。
- 不改写无关答案。

## 既有 QA 和冲突

创建新问题前，先读取已有 `.ai/qa/project-qa.md`。

已 answered 的 QA 视为人工项目知识。如果既有 QA 和已验证仓库事实、当前草稿上下文或新的用户说明冲突：

- 不覆盖旧答案。
- 用新的 `QA-###` 编号追加 follow-up 问题。
- 在 `Context` 里说明冲突事实。
- 如果冲突会影响最终上下文、命令、风险区域或模块边界，设置 `Required: yes`。
- 用 `Related` 关联之前的 QA 编号，例如 `QA-001, QA-014`。

只有用户明确确认旧答案不再适用时，才把旧问题标记为 `Status: obsolete`。

## 完成条件

只有所有必答问题都是以下状态之一，QA 阶段才算完成：

- `answered`
- `deferred`
- `not-applicable`
- `obsolete`

可选问题如果不影响当前工作流，可以继续 pending。

QA 阶段完成后，QA 文档仍然长期维护。未来的 `qa`、`md`、`html`、`document`、`maintain` 都应该复用它。

## 提问选择

只问无法从源码可靠推断的事实。

优先 5-10 个高价值问题，不做长问卷。

常见问题：

- 这个项目真实业务目标是什么？
- 哪些模块是核心开发区域？
- 哪些模块是 legacy、generated、third-party 或通常不要动？
- 本地最可靠的 build、test、lint、run 命令是什么？
- 哪些测试依赖外部服务？
- 新增功能最推荐参考哪个已有模块？
- 有哪些线上问题、历史坑或团队约定需要未来工作遵守？

## 终端示例

```text
QA 已更新：.ai/qa/project-qa.md

待回答：
- QA-001: 确认核心业务目标
- QA-002: 确认可靠验证命令
- QA-003: 确认不要修改的目录

可以编辑文件回答，也可以按编号 inline 回答，例如：
QA-001: ...
```
