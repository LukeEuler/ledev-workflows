# 报告

## 落盘位置

普通项目中写入：

```text
.ai/
  reviews/
    RYYYYMMDD-HHMM-短标题.md
  state/
    ledev-review.md
```

当前仓库是 workflow、skill、prompt、agent 配置或类似开发流程仓库，且用户正在修改这些工作流本身时，不创建 `.ai/`。此时在最终回复中说明 review 记录语义，并依赖 git diff 和对话记录保留证据。

## Git Ignore

普通项目中，执行 review 前按共享规则确保本地 review 产物不会进入业务代码 git。本 skill 需要覆盖的具体条目是：

```gitignore
.ai/reviews/
.ai/state/ledev-review.md
```

当前仓库是 workflow、skill、prompt、agent 配置或类似开发流程仓库，且本次不落盘 review 报告时，跳过 `.gitignore` 修改。如果用户明确要求把 review 报告纳入版本控制，不执行本规则，并在报告中记录该用户决策。

## 报告内容

报告必须包含：

- review 范围元数据。
- 用户意图和意图一致性判断。
- 实际改造摘要。
- findings-first 审查结果。
- 复现命令，包括预检、diff、log 和实际执行过的验证命令。
- 读取文件清单，列出为形成结论而打开的关键文件。
- 测试和验证情况。
- 未确认问题。
- 后续建议。

报告的标题、字段名和说明文字必须中文为主。可以保留稳定英文关键词或枚举值，例如 `Severity`、`Mode`、`Blocker`、`Major`、`committed-linear-range`；代码符号、命令、路径、文件名、包名、类型名和 API 名称保持原样。

## 状态文件

`.ai/state/ledev-review.md` 只记录最近一次运行锚点：

- 当前审查报告。
- mode、base、head、diff expression。
- 意图状态。
- 按严重级别统计的问题数量。
- 验证状态。
- 待确认问题。
- 更新时间。

不要把完整 report 塞进状态文件。
