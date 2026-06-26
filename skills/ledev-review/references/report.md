# Report

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

## 报告内容

报告必须包含：

- review 范围元数据。
- 用户意图和意图一致性判断。
- 实际改造摘要。
- findings-first 审查结果。
- 测试和验证情况。
- 未确认问题。
- 后续建议。

## 状态文件

`.ai/state/ledev-review.md` 只记录最近一次运行锚点：

- active review report。
- mode、base、head、diff expression。
- intent status。
- findings count by severity。
- validation status。
- open questions。
- updated time。

不要把完整 report 塞进状态文件。
