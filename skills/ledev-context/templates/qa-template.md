# 项目 QA 模板

用于长期维护的项目 QA 文档：`.ai/qa/project-qa.md`。正文以中文为主；字段名、状态值和 QA 编号可保留英文。
需要用户输入的短确认 token 使用英文，例如 `yes/no`、`defer`、`not-applicable`、`continue/stop`；不要要求输入中文短命令。

## QA 元数据

- 目标项目：
- 创建者：
- 创建时间：
- 最后检查时间：
- 状态：active | complete | needs-follow-up | stale
- 来源草稿：
- 已提升摘要：

## 回答方式

可以直接编辑这个文件回答，也可以在对话或命令里按 QA 编号回答：

```text
QA-001: ...
QA-002: not-applicable.
```

## QA 条目

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

## 已确认 QA 结论

- 可以提升到 `.ai/project-context.md` 或人类文档的简洁结论。

## 已推迟或仍开放的追问

- 仍未解决、已推迟或需要未来确认的 QA 编号。

## 已过期答案

- 经用户明确确认已经不再适用的旧回答编号。
