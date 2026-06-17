# Scope 模式说明

`scope` 是 `ledev-context` 的正式第一阶段。它替代旧的 `plan` 阶段，用于轻量发现和确认扫描范围。

## 定位

`scope` 不生成项目理解，不做代码事实采集，不写最终上下文。

它只回答：

- 应该扫描哪个目标路径？
- 这是单项目还是 monorepo？
- 可能使用哪些语言和规则？
- 哪些目录 deep scan？
- 哪些目录只 shallow record？
- 哪些目录排除？
- 是否存在 generated/vendor/build artifacts？
- 扫描要如何分批？
- 这个 scope 是否已被用户确认，能否复用？

## 产物

默认写入：

```text
.ai/scope/scan-scope.md
```

该文件是长期可复用的扫描策略。重跑时如果它仍然 current，可以直接复用，不必重复询问用户。

## 轻量发现

允许运行安全发现命令：

- `pwd`
- `rg --files`
- 顶层目录列表
- 文件数量统计
- 查找常见配置文件、module 文件、CI 文件、ignore 文件

不要深读源码，不要写架构事实，不要总结业务目的。

## 人工确认

scope 需要简单交互确认。

需要用户输入短确认时使用英文 token，例如 `yes/no`、`edit/confirm`、`continue/stop`；可以用中文说明含义，但不要要求用户输入“确认”“取消”等中文短命令。

使用 `SCOPE-###` 编号，例如：

```text
SCOPE-001: 请确认 deep scan、shallow record 和 exclude 范围是否正确。
```

用户可以编辑 `.ai/scope/scan-scope.md` 回答，也可以 inline 回答：

```text
SCOPE-001: yes. Exclude tmp/ as well.
```

答案要合并回 `.ai/scope/scan-scope.md`。

## stale 判断

如果出现以下情况，标记 `Status: stale` 或 `needs-confirmation`：

- 顶层目录明显变化。
- 主要语言或 module 文件变化。
- ignore 规则变化。
- 用户要求改变目标路径。
- 事实层扫描发现 scope 排除项可能错误。

scope stale 时，不要直接执行 scan；先追加新的 `SCOPE-###` 确认问题。

## scan 前置条件

`scan` 必须读取 `.ai/scope/scan-scope.md`。

只有满足以下条件之一，才能进入 scan：

- scope 状态是 `confirmed` 或 `current`。
- 用户本轮明确要求跳过确认并直接按当前 scope 扫描。

如果 scope 缺失，先运行 `scope`。
