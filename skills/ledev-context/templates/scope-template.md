# 扫描范围模板

用于 `.ai/scope/scan-scope.md`。正文以中文为主；路径、命令、状态值可保留英文。
需要用户输入的短确认 token 使用英文，例如 `yes/no`、`edit/confirm`、`continue/stop`；不要要求输入中文短命令。

## Scope 元数据

- 目标路径：
- Primary repo：
- 创建时间：
- 最后确认时间：
- 创建者：
- Status: draft | needs-confirmation | confirmed | current | stale
- 可复用：yes | no
- 相关事实层：

## 仓库形态

- 仓库类型：single-project | monorepo | unknown
- 多仓库形态：single-repo | primary-with-related-repos | monorepo-with-related-repos | unknown
- 主要语言候选：
- 规则文件：
- 文件数量：
- 顶层目录：
- 关键配置文件：
- ignore 文件：

## 多仓库覆盖

- Primary repo name：
- Primary repo path：
- Context output location：`.ai/` in primary repo
- 默认写入策略：Primary repo writable；Related repos read-only

| Related repo | local_path | role | scan_depth | write_policy | declared_version | resolved_source | local_checkout | version_match | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | dependency/upstream/downstream/protocol-source/reference/workspace-member/unknown | deep/shallow/metadata-only | read-only |  |  |  | match/mismatch/not-applicable/unknown |  |

## 扫描策略

- Deep scan：
- Shallow record：
- Exclude：
- Generated/vendor/build artifacts：
- 分批计划：
- Token 风险：
- 准确度风险：
- 多仓版本风险：

## Scope 确认问题

### SCOPE-001: 确认扫描范围

- Status: pending | answered | obsolete
- Context:
- Requested answer format: `yes`，或说明需要新增/排除/改为 shallow 的目录。
- Answer:
- Answer source: file edit | inline reply
- Last updated:

## 复用规则

- 复用条件：
- stale 条件：
- 下次 scan 前是否需要重新确认：
