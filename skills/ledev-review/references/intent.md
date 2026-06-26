# Intent

## 目标

review 必须比较“用户想解决什么”和“代码实际改变了什么”。如果意图不清，不要只凭 diff 猜业务正确性。

## 意图来源

按优先级读取：

- 用户当前说明。
- `.ai/tasks/T###-*.md` 中的需求、方案、实现记录和验证记录。
- commit message 和提交序列。
- issue、PR/MR 描述或本地文档。
- 测试变更、快照变更、迁移脚本和配置变更。
- 代码 diff 本身。

## 必须询问用户的情况

- diff 无法解释变更目的。
- commit message 和代码行为冲突。
- task 目标与实际变更不一致。
- 需要业务规则才能判断正确性。
- 变更明显多做、少做或偏离目标，但无法从上下文确认是否有意。

## 意图一致性检查

记录：

```text
Intent:
- Stated goal:
- Inferred goal:
- Actual changes:
- Goal alignment: met | partially met | not met | unclear
- Notes:
```

如果 `Goal alignment` 是 `unclear`，先沟通；如果用户不提供信息，只能给出基于技术事实的有限 review。
