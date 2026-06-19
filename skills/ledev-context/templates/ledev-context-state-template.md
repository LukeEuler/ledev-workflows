# LEDev Context 状态模板

当 `ledev-context` 需要专门维护阶段锚点时，使用这个结构写入 `.ai/state/ledev-context.md`。正文以中文为主；状态值和模式名可保留英文。`.ai/state/` 是运行进度目录，不要把不同 skill 的进度合并到同一个文件。

## 阶段锚点

- 当前锚点：none | scope | scan | summarize | qa | md | html | document | maintain
- 锚点更新时间：
- 锚点更新者：
- 最后完整完成阶段：
- 正在执行阶段：

## 阶段顺序

`none -> scope -> scan -> summarize -> qa -> md -> html -> document -> maintain`

## 完成规则

- 锚点表示最后一个完整完成的阶段。
- 阶段只完成一半时，不允许推进锚点。
- 向后推进必须遵守阶段顺序。
- 重复执行前序阶段时，必须把锚点前置到那个已完成阶段。
- 锚点前置后，后续产物要标记为 stale，直到重新生成。
- 下一步建议只用于提示用户，不代表自动续跑授权。

## 跟踪产物

- `.ai/facts/manifest.md`：missing | active | partial | stale
- `.ai/scope/scan-scope.md`：missing | draft | needs-confirmation | confirmed | current | stale
- `.ai/facts/repo-structure.md`：missing | active | partial | stale
- `.ai/facts/code-inventory.md`：missing | active | partial | stale
- `.ai/facts/architecture-facts.md`：missing | active | partial | stale
- `.ai/facts/commands.md`：missing | active | partial | stale
- `.ai/facts/dependencies.md`：missing | active | partial | stale
- `.ai/facts/tests.md`：missing | active | partial | stale
- `.ai/facts/boundaries.md`：missing | active | partial | stale
- `.ai/facts/related-repos.md`：missing | active | partial | stale | not-applicable
- `.ai/facts/evidence-index.md`：missing | active | partial | stale
- `.ai/drafts/project-scan.md`：missing | active | complete | stale | promoted | archived | deleted
- `.ai/drafts/project-context-draft.md`：missing | active | complete | stale | promoted | archived | deleted
- `.ai/qa/project-qa.md`：missing | active | complete | needs-follow-up | stale

## 最终产物

- `.ai/project-context.md`：missing | active | stale | current
- `.ai/project-context.html`：missing | active | stale | current
- `.ai/drafts/project-context.<timestamp>.html`：missing | available | pruned
- `.ai/state/ledev-context.md`：missing | active | stale | current
- Markdown 人类项目文档：missing | partial | stale | current
- HTML 人类项目文档：missing | partial | stale | current

## 最近一次执行

- 执行模式：
- 完成阶段：
- 锚点变化：none | advanced | unchanged | moved-back
- 锚点变化原因：
- 标记 stale 的后续产物：
- 推荐下一步：

## 交接说明

- 给后续运行、其他 skill 或其他 AI agent 的交接说明。
- 多仓库上下文交接：Primary repo、Related repos、版本关系、只读/可写边界，以及哪些关联仓库事实可被后续 skill 继承。
