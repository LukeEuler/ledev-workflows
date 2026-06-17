# 事实层模板

用于 `.ai/facts/*.md`。正文以中文为主；路径、命令、符号、字段名可保留英文。

## 事实元数据

- 目标项目：
- 文件类型：manifest | repo-structure | code-inventory | architecture-facts | commands | dependencies | tests | boundaries | evidence-index
- 扫描时间：
- 创建者：
- 状态：active | partial | stale
- 扫描范围：
- 排除范围：
- 相关 QA：

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

## 缺口

- 未扫描内容：
- 未读取原因：
- 需要后续确认：

## 非推断说明

- 本文件只记录可观察事实。
- 不写业务目的推断。
- 不写代码质量评价或修复建议。
- 不把没有证据的判断写成事实。
