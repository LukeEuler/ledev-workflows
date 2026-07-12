# 事实层采集规则

`ledev-context scan` 的核心产物是 `.ai/facts/`。这是后续 `summarize`、`qa`、`md`、`html`、`document`、`maintain` 的基准数据源。

## 定位

事实层只做观察和梳理，不做业务推理。

允许写：

- 仓库中真实存在的文件、目录、模块、包、命令、配置、测试、入口、符号、依赖。
- 从源码、配置、README、脚本、CI 中可直接观察到的架构事实。
- 事实之间的可证据化关系，例如“文件 A import 了包 B”“命令 X 出现在 Makefile 中”“路由 Y 在文件 Z 注册”。
- 多仓库关系事实：Primary repo、Related repos、关联角色、扫描深度、写入策略、声明依赖版本、实际解析来源、本地 checkout、版本是否一致。

不要写：

- “这个项目的业务目标是……”这类没有人工确认或文档证据的推理。
- “核心模块”“推荐参考实现”“主要风险”这类判断，除非有明确证据或在后续摘要层标为推断。
- 代码质量评价、修复建议、重构建议。

## 推荐目录

```text
.ai/facts/
  manifest.md
  repo-structure.md
  code-inventory.md
  architecture-facts.md
  commands.md
  dependencies.md
  tests.md
  boundaries.md
  related-repos.md
  evidence-index.md
```

文件用途：

- `manifest.md`：事实层元数据、扫描范围、时间、状态、源码快照摘要、stale 判断和未扫描原因。
- `repo-structure.md`：目录树、重要目录、文件分布、generated/vendor/third-party 标记。
- `code-inventory.md`：语言、包/模块、入口文件、公开符号、核心类型、接口、配置文件。
- `architecture-facts.md`：可观察架构事实、模块依赖、调用方向、数据流入口/出口、外部边界。
- `commands.md`：build/test/lint/run/format/generate 命令及来源。
- `dependencies.md`：依赖文件、内部依赖、外部依赖、服务/存储/网络依赖。
- `tests.md`：测试文件、测试框架、fixtures、mocks、集成测试、外部依赖。
- `boundaries.md`：模块边界、不要修改的区域、dirty files、敏感文件。
- `related-repos.md`：多仓库上下文、关联仓库角色、版本关系、只读/可写边界、跨仓证据索引。
- `evidence-index.md`：重要事实到证据来源的索引。

可以按项目规模合并或拆分，但必须保留 `.ai/facts/manifest.md` 和 `.ai/facts/evidence-index.md`。

## 扫描要求

- 使用 `rg --files` 或等价方式列出全部文件。
- 明确记录扫描范围和排除范围。
- 在 `manifest.md` 记录本次事实层对应的源码快照摘要：`git_head`、`git_status_short`、纳入扫描的文件数量、文件清单 hash、关键内容 hash、scope hash、Related repo 快照和当前 stale 级别。
- 多仓库扫描时，分别记录每个仓库的扫描范围、排除范围、git 状态、版本信息和未扫描原因。
- 对 `Related repos` 默认只读扫描；不要在关联仓库写 `.ai/` 事实文件。
- 写入事实层前必须把路径标准化为可移植路径：主仓库内路径相对 `Primary repo` 根目录；关联仓库路径相对 `Primary repo`，或写成 `related:<repo-name>:<repo-relative-path>`。
- 本机绝对路径只能进入 `.ai/drafts/local-paths.md` 这类临时映射文件，不进入 `.ai/facts/`。
- 观察所有源码目录、配置文件、脚本、CI、README、docs、测试文件。
- 对大型 generated/vendor/third-party 目录可以只记录目录、规模和来源，不逐文件深入。
- 对二进制、大文件或不可读文件，记录路径和未读取原因。
- 如果仓库很大，按目录分批扫描；不要只看 README 或少量入口文件就写总结。

## 事实写法

每条重要事实建议使用这个结构：

```md
- Fact:
  - Type:
  - Evidence:
  - Notes:
```

示例：

```md
- Fact: `cmd/server/main.go` 是一个 Go 程序入口文件。
  - Type: entrypoint
  - Evidence: `cmd/server/main.go`
  - Notes: 仅说明入口存在，不推断业务职责。
```

证据要求：

- 文件事实：写路径。
- 符号事实：写路径和符号名；能定位行号时写 `path:line`。
- 命令事实：写来源文件和命令文本。
- 架构关系：写产生关系的 import、调用、路由注册、配置引用或脚本引用。
- 人工确认：写 QA 编号或 Human Notes 来源。
- 多仓库事实：写 `related:<repo-name>:<repo-relative-path>` 或相对 `Primary repo` 的路径，例如 `../funnel:internal/log/parser.go`，并标明该证据来自 `Primary repo` 还是某个 `Related repo`。

## 路径可移植性

长期事实层禁止写本机绝对路径。常见禁止示例包括：

- `/Users/name/project/...`
- `/home/name/project/...`
- `C:\Users\name\project\...`
- `/private/tmp/...`

允许写入：

- `cmd/server/main.go`
- `internal/foo/bar.go:42`
- `../funnel:pkg/log/event.go`
- `related:funnel:pkg/log/event.go`
- `module-cache:github.com/org/pkg@v1.2.3/file.go`，仅当事实来自不可避免的 module cache，并且不记录本机 cache 根目录。

如果命令输出只提供绝对路径，应在记录事实时转换为相对路径；无法可靠转换时，把原始输出放入 `.ai/drafts/local-paths.md`，事实层写“路径无法稳定相对化，详见临时草稿”。

## 版本关系事实

多仓库分析必须区分三个版本概念：

- `declared_version`：主仓库依赖声明中的版本，例如 `go.mod`、lockfile、配置或文档声明。
- `resolved_source`：当前构建/测试实际会使用的来源，例如 `replace ../B`、`go.work`、vendor、module cache、workspace 或远端模块版本。
- `local_checkout`：本地关联仓库当前检出的 branch、tag、commit 和 dirty 状态。

如果 A 声明依赖 B 的 `101`，但本地 B checkout 是 `102`：

- 若没有 `replace`、`go.work`、workspace、vendor 或其他配置把 A 解析到本地 B，则 A 的实际依赖应按 `101` 记录，本地 B `102` 只能作为参考，不能作为 confirmed dependency code。
- 若 A 的构建配置明确解析到本地 B，则实际分析对象是本地 B 当前 checkout，同时必须记录它和声明版本 `101` 的差异。
- 如果需要精确分析 `101` 的源码，优先建议用户把 B 切到 `101`，或使用独立 worktree/clone/module cache 读取 `101`，避免污染 B 当前工作树。

## 架构事实边界

架构事实不是架构解释。只写可观察关系：

- 模块 A import/调用模块 B。
- 入口 E 初始化组件 C。
- 路由 R 绑定 handler H。
- 配置 K 被文件 F 读取。
- 测试 T 使用 fixture/mock M。
- CI job J 执行命令 C。

如果需要解释“为什么这样设计”，放到 `summarize` 的推断区或 `qa` 提问，不写入事实层。

## 后续使用

- `summarize` 必须先读取 `.ai/facts/manifest.md` 和相关事实文件。
- `qa` 应优先针对事实缺口、事实冲突、人工无法从代码确认的信息提问。
- `md` 和 `html` 只能把事实层中有证据的内容提升为 confirmed 内容；`html` 可以重新编排信息，但不能改变事实确定性。
- `status` 必须读取 `.ai/facts/manifest.md` 中的源码快照摘要，并和当前仓库快照比较后输出 stale 级别。
- `refresh` 发现事实层 stale 时，应先更新 `.ai/facts/` 和 `manifest.md` 的快照摘要，再刷新或标记下游上下文和文档。
- `maintain` 发现代码变化时，应先更新 `.ai/facts/`，再更新上下文和文档。
