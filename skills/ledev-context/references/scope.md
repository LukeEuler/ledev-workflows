# Scope 模式说明

`scope` 是 `ledev-context` 的正式第一阶段。它替代旧的 `plan` 阶段，用于轻量发现和确认扫描范围。

## 定位

`scope` 不生成项目理解，不做代码事实采集，不写最终上下文。

它只回答：

- 应该扫描哪个目标路径？
- 长期产物中如何用可移植相对路径表示目标路径和关联仓库路径？
- 这是单项目还是 monorepo？
- 是否存在 Primary repo + Related repos 的多仓库上下文？
- 关联仓库是实际解析依赖、上游/下游服务、协议来源、参考实现，还是只读补充资料？
- 主仓库声明依赖版本和本地关联仓库 checkout 是否一致？
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

多仓库上下文仍只在 `Primary repo` 写入本文件。`Related repos` 的路径、角色、扫描深度、写入策略和版本关系都记录在主仓库的 `.ai/scope/scan-scope.md` 中。

`scan-scope.md` 是长期可复用产物，不应写本机绝对路径。目标路径、关联仓库路径和证据路径都使用相对 `Primary repo` 的路径或稳定仓库别名；本机绝对路径如需保留，只能写入 `.ai/drafts/local-paths.md`。

## 多仓库范围

多仓库 scope 必须区分：

- `Primary repo`：当前要开发、修复、验证或生成上下文的目标项目；`.ai/` 产物默认只写入这里。
- `Related repos`：为理解当前目标项目需要读取的本地兄弟仓库、上游库、下游服务、协议仓库、参考实现或外部工作区成员。

每个 `Related repo` 至少记录：

- `name`
- `local_path`
- `role`：`dependency` | `upstream` | `downstream` | `protocol-source` | `reference` | `workspace-member` | `unknown`
- `scan_depth`：`deep` | `shallow` | `metadata-only`
- `write_policy`：默认 `read-only`
- `declared_version`：主仓库依赖文件、lockfile 或配置中声明的版本；没有则写 `未发现明确证据`
- `resolved_source`：实际构建会解析到的来源，例如 module cache、vendor、`replace`、`go.work`、workspace、本地路径、远端版本；无法确认则写 `未确认`
- `local_checkout`：本地关联仓库当前 branch、commit、tag 或 dirty 状态；无法读取则写原因
- `version_match`：`match` | `mismatch` | `not-applicable` | `unknown`

`local_path` 使用相对 `Primary repo` 的路径，例如 `../funnel`、`vendor/funnel` 或 `third_party/funnel`；不要写 `/Users/...`、`/home/...`、`C:\...` 这类本机绝对路径。

如果 `declared_version`、`resolved_source` 和 `local_checkout` 不一致，不要自动把本地 checkout 当作实际依赖代码。应把版本不一致写入 scope 的准确度风险，并在 scan/facts 中保留三者差异。

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
- Primary repo 或 Related repos 的路径、角色、扫描深度、写入策略变化。
- 依赖声明版本、实际解析来源或本地 checkout 发生变化，且会影响代码事实。
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

如果多仓库 scope 存在版本不一致，仍可进入 scan，但必须把不一致标记为风险；需要精确分析实际依赖代码时，优先要求用户提供或切换到实际解析版本，或使用不会改动当前工作树的独立 checkout/worktree。
