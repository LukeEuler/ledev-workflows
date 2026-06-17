# 事实层采集规则

`ledev-context scan` 的核心产物是 `.ai/facts/`。这是后续 `summarize`、`qa`、`md`、`html`、`document`、`maintain` 的基准数据源。

## 定位

事实层只做观察和梳理，不做业务推理。

允许写：

- 仓库中真实存在的文件、目录、模块、包、命令、配置、测试、入口、符号、依赖。
- 从源码、配置、README、脚本、CI 中可直接观察到的架构事实。
- 事实之间的可证据化关系，例如“文件 A import 了包 B”“命令 X 出现在 Makefile 中”“路由 Y 在文件 Z 注册”。

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
  evidence-index.md
```

文件用途：

- `manifest.md`：事实层元数据、扫描范围、时间、状态、未扫描原因。
- `repo-structure.md`：目录树、重要目录、文件分布、generated/vendor/third-party 标记。
- `code-inventory.md`：语言、包/模块、入口文件、公开符号、核心类型、接口、配置文件。
- `architecture-facts.md`：可观察架构事实、模块依赖、调用方向、数据流入口/出口、外部边界。
- `commands.md`：build/test/lint/run/format/generate 命令及来源。
- `dependencies.md`：依赖文件、内部依赖、外部依赖、服务/存储/网络依赖。
- `tests.md`：测试文件、测试框架、fixtures、mocks、集成测试、外部依赖。
- `boundaries.md`：模块边界、不要修改的区域、dirty files、敏感文件。
- `evidence-index.md`：重要事实到证据来源的索引。

可以按项目规模合并或拆分，但必须保留 `.ai/facts/manifest.md` 和 `.ai/facts/evidence-index.md`。

## 扫描要求

- 使用 `rg --files` 或等价方式列出全部文件。
- 明确记录扫描范围和排除范围。
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
- `maintain` 发现代码变化时，应先更新 `.ai/facts/`，再更新上下文和文档。
