# 事实层模板

用于 `.ai/ledev/facts/*.md`。正文以中文为主；路径、命令、符号、字段名可保留英文。

## 事实元数据

- 目标项目：
- Primary repo：
- Related repo：
- 路径策略：repo-relative | related-repo-relative；禁止本机绝对路径
- 文件类型：manifest | repo-structure | code-inventory | architecture-facts | commands | dependencies | tests | boundaries | related-repos | evidence-index
- 扫描时间：
- 创建者：
- 状态：active | partial | stale
- 源码快照状态：missing | current | unknown | stale-minor | stale-facts | stale-scope | stale-document
- 扫描范围：
- 排除范围：
- 多仓库角色：primary | related | not-applicable
- 版本关系：declared_version / resolved_source / local_checkout / version_match
- 相关 QA：

## 源码快照摘要

- git_head：
- git_status_short：
- tracked_file_count：
- tracked_file_list_hash：
- tracked_content_hash：
- scope_hash：
- related_repo_snapshot：

## 已观察事实

```md
- Fact:
  - Type:
  - Evidence:
  - Notes:
```

## 证据索引

- 事实编号：
- 证据来源：
- 证据类型：file | symbol | command | config | test | ci | docs | human
- 路径格式：primary-relative | related:<repo>:path | primary-relative-related-repo | no-path

## 缺口

- 未扫描内容：
- 未读取原因：
- 需要后续确认：

## 非推断说明

- 本文件只记录可观察事实。
- 不写业务目的推断。
- 不写代码质量评价或修复建议。
- 不把没有证据的判断写成事实。
