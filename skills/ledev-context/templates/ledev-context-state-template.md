# LEDev Context 状态模板

当 `ledev-context` 需要专门维护阶段锚点时，使用这个结构写入 `.ai/ledev/state/ledev-context.md`。正文以中文为主；状态值和模式名可保留英文。`.ai/ledev/state/` 是运行进度目录，不要把不同 skill 的进度合并到同一个文件。

## 阶段锚点

- 当前锚点：none | scope | scan | summarize | qa | md | html | document | maintain
- 锚点更新时间：
- 锚点更新者：
- 最后完整完成阶段：
- 正在执行阶段：

## 阶段顺序

`none -> scope -> scan -> summarize -> qa -> md -> html -> document -> maintain`

`status` 是只读检查，不推进锚点。`refresh` 是组合刷新动作，不是独立锚点；刷新完成后按实际完成的最后阶段设置锚点。

## 完成规则

- 锚点表示最后一个完整完成的阶段。
- 阶段只完成一半时，不允许推进锚点。
- 向后推进必须遵守阶段顺序。
- 重复执行前序阶段时，必须把锚点前置到那个已完成阶段。
- 锚点前置后，后续产物要标记为 stale，直到重新生成。
- 下一步建议只用于提示用户，不代表自动续跑授权。

## 跟踪产物

- `.ai/ledev/facts/manifest.md`：missing | active | partial | stale
- `.ai/ledev/scope/scan-scope.md`：missing | draft | needs-confirmation | confirmed | current | stale
- `.ai/ledev/facts/repo-structure.md`：missing | active | partial | stale
- `.ai/ledev/facts/code-inventory.md`：missing | active | partial | stale
- `.ai/ledev/facts/architecture-facts.md`：missing | active | partial | stale
- `.ai/ledev/facts/commands.md`：missing | active | partial | stale
- `.ai/ledev/facts/dependencies.md`：missing | active | partial | stale
- `.ai/ledev/facts/tests.md`：missing | active | partial | stale
- `.ai/ledev/facts/boundaries.md`：missing | active | partial | stale
- `.ai/ledev/facts/related-repos.md`：missing | active | partial | stale | not-applicable
- `.ai/ledev/facts/evidence-index.md`：missing | active | partial | stale
- `.ai/ledev/drafts/project-scan.md`：missing | active | complete | stale | promoted | archived | deleted
- `.ai/ledev/drafts/project-context-draft.md`：missing | active | complete | stale | promoted | archived | deleted
- `.ai/ledev/qa/project-qa.md`：missing | active | complete | needs-follow-up | stale

## 源码快照

- 快照状态：missing | current | unknown | stale-minor | stale-facts | stale-scope | stale-document
- 快照时间：
- Primary repo git_head：
- Primary repo git_status_short：
- tracked_file_count：
- tracked_file_list_hash：
- tracked_content_hash：
- scope_hash：
- facts_hash：
- context_hash：
- html_hash：
- Related repos：
  - `related:<name>`：role / resolved_source / local_checkout / dirty_state / scan_depth / version_match

## stale 判断

- 当前判断：current | unknown | stale-minor | stale-facts | stale-scope | stale-document
- 触发原因：
- 受影响产物：
- 推荐刷新命令：
- 最近一次只读 status：

## 最终产物

- `.ai/ledev/project-context.md`：missing | active | stale | current
- `.ai/ledev/project-context.html`：missing | active | stale | current
- `.ai/ledev/drafts/project-context.<timestamp>.html`：missing | available | pruned
- `.ai/ledev/state/ledev-context.md`：missing | active | stale | current
- Markdown 人类项目文档：missing | partial | stale | current
- HTML 人类项目文档：missing | partial | stale | current

## 最近一次执行

- 执行模式：
- 完成阶段：
- 锚点变化：none | advanced | unchanged | moved-back
- 锚点变化原因：
- 标记 stale 的后续产物：
- 推荐下一步：
- 推荐下一步说明：

## 交接说明

- 给后续运行、其他 skill 或其他 AI agent 的交接说明。
- 多仓库上下文交接：Primary repo、Related repos、版本关系、只读/可写边界，以及哪些关联仓库事实可被后续 skill 继承。
