# Go 项目规则

用于 `ledev-context` 处理 Go 项目。运行产物以中文为主；Go 命令、包路径、文件名、配置项和必要关键词保留英文。

本规则分为四类：

- 事实层规则：指导 `scan` 如何观察和记录 Go 项目事实。
- 代码规范：参考 Effective Go、Go Code Review Comments、gofmt/go vet 和 golangci-lint 生态中的通用约定。
- 代码缺陷审查：指导 review、bugfix、test 阶段优先检查高风险缺陷。
- 可维护性规范：指导实现和审查时关注包边界、依赖方向、测试结构和长期演进成本。

不要把代码规范、缺陷审查或可维护性判断写成无证据的项目事实。事实层只记录可观察事实；规范判断用于后续实现、review、测试和修复阶段。

## 事实层要求

Go 项目的 `scan` 必须把代码事实写入 `.ai/ledev/facts/`，不能只写项目摘要。

重点事实文件建议：

- `.ai/ledev/facts/code-inventory.md`：记录 module path、Go version、package 列表、入口、导出类型/接口/函数、重要配置文件。
- `.ai/ledev/facts/architecture-facts.md`：记录 package import 关系、`cmd/` 初始化关系、handler/router 注册、service/repository/client 等可观察调用边界。
- `.ai/ledev/facts/dependencies.md`：记录 `go.mod` 依赖、内部包依赖、外部服务 client、数据库/消息/网络依赖。
- `.ai/ledev/facts/tests.md`：记录 `_test.go`、table-driven tests、fixtures、mocks、integration scripts 和外部依赖。

只记录可观察事实。例如“`internal/foo` import 了 `pkg/bar`”可以写；“`internal/foo` 是核心业务模块”除非有文档或人工确认，否则不要写进事实层。

## 需要重点读取的文件

常见 Go 项目需要先检查：

- `go.mod`
- `go.work`
- `Makefile`
- `.golangci.yml` 或 `.golangci.yaml`
- README 和已有文档
- CI 配置
- `cmd/`
- `internal/`
- `pkg/`
- `service/`
- `common/`
- `model/`
- `plugin/`
- `scripts/`
- `tools/`
- `hack/`
- `_test.go`
- generated、vendor、third_party、protobuf、mock、codegen 相关目录

不是每个项目都有这些目录。实际总结时只记录真实存在、对项目有意义的部分。

## 需要采集的事实

Go 项目画像里建议记录：

- module path
- `go.mod` 中声明的 Go 版本
- README 或本地环境里提到的 Go 版本；如果和 `go.mod` 不一致，需要标注
- build tags
- 测试命令
- lint 命令
- 格式化命令
- 运行命令
- 代码生成命令
- 包边界
- 程序入口
- 核心接口和核心数据结构
- 成熟参考包或参考插件
- 外部依赖服务
- `replace`、`go.work`、workspace、vendor 和 module cache 对依赖解析的影响。
- 多仓库上下文中的声明 module 版本、实际解析来源和本地关联仓库 checkout。

## Go 多仓库版本规则

Go 项目中不要只凭本地兄弟目录判断实际依赖代码。必须按证据区分：

- `go.mod require` 声明的 module path 和版本。
- `replace` 是否把 module 指向本地路径或另一个版本。
- `go.work` 是否把多个本地 module 纳入同一个 workspace。
- `vendor/` 是否存在且构建命令使用 vendor 模式。
- 可用时用 `go list -m -json all` 或等价命令确认实际解析版本和替换路径；命令失败时记录失败原因，不臆测。

如果 A 的 `go.mod` 声明 B 为 `v1.0.1`，而本地 `../B` 是 `v1.0.2`：

- 没有 `replace ../B`、`go.work` 或 vendor 证据时，A 的 confirmed dependency version 是 `v1.0.1`；`../B@v1.0.2` 只能作为 related repo reference。
- 有 `replace ../B` 或 `go.work` 证据时，A 的实际解析来源是本地 `../B` 当前 checkout；同时记录它与声明版本 `v1.0.1` 的不一致。
- 精确分析 `v1.0.1` 源码时，优先使用独立 worktree/clone 或 module cache，不要求用户破坏当前 `../B` 工作区；如果必须切换当前仓库版本，先向用户确认。

## 代码规范

这些规则用于实现、review 和测试建议。项目已有规范、CI、`.golangci.yml`、README 或团队约定优先于通用规则；没有项目规则时，按 Go 社区主流实践处理。

### 基础风格

- 使用 `gofmt` 或项目指定格式化命令，不手写格式风格。
- 优先使用清晰、短小、符合上下文的标识符；避免无意义缩写，也避免过长的机械命名。
- package 名称使用小写短名，避免 `util`、`common` 这类过宽泛命名，除非项目已有稳定约定。
- exported 标识符应有有用注释，注释以标识符名称开头；不要写空泛注释。
- 控制流优先 early return，减少不必要的嵌套。
- 避免滥用全局可变状态；必要时说明生命周期、并发访问和初始化顺序。
- 不引入无用 abstraction。先匹配项目现有模式，再决定是否抽取接口、helper 或 shared package。

### 错误处理

- 不忽略 error；确实可忽略时需要有局部理由或符合项目风格。
- 错误包装应保留上下文，使用项目既有方式；没有约定时优先保留原始错误链。
- 日志和错误不要重复报告同一个失败，避免既在底层 log 又在上层 log 造成噪音。
- 用户可见错误、API 错误和内部诊断错误要区分，不把敏感信息直接暴露到外部响应。

### 类型、接口和 API

- 接口应由消费者侧定义，除非项目已有明确反向约定。
- 避免为单个实现提前创建接口；接口应服务测试、替换、边界隔离或稳定 API。
- 函数签名保持聚焦；参数过多时优先检查是否缺少领域对象或配置对象。
- 对外 API、持久化结构、配置项和 wire format 变更要关注兼容性。
- 指针和值语义应和 mutability、性能、nil 表达能力保持一致。

### 并发和资源

- goroutine 必须有清晰生命周期，通常需要 context、关闭条件或 owner。
- channel 的发送、接收、关闭责任要明确；不要从多个 owner 关闭同一个 channel。
- 共享可变状态需要同步策略；用 `go test -race` 或项目等价命令验证高风险改动。
- I/O、RPC、DB、消息队列调用应有 timeout、cancellation 或上层可控的生命周期。
- 文件、连接、锁、事务等资源要成对释放；注意 defer 在循环中的语义和成本。

### 工具和 lint

- 优先使用项目定义的 `make lint`、`make test`、CI 脚本或 `golangci-lint` 配置。
- 没有项目配置时，常见基础检查包括 `gofmt`、`go vet`、`go test` 和适用的 `golangci-lint run`。
- lint 发现的问题不要机械压制；需要 `//nolint` 时应尽量局部、具体，并说明原因。

## 代码缺陷审查

在 Go 项目中，review、bugfix 或 test 前应该特别关注以下缺陷类型。

### 正确性

- 错误是否被忽略、覆盖或错误分类。
- nil、空 slice、空 map、零值和默认配置是否处理正确。
- 边界条件是否覆盖：空输入、单元素、大输入、分页尾页、重复请求、乱序数据。
- 数字精度、整数溢出、时间单位、时区和 duration 转换是否正确。
- 配置默认值、环境变量、feature flag 和向后兼容是否合理。
- 序列化、反序列化、字段重命名和 schema 变更是否破坏现有数据。

### 并发和生命周期

- goroutine 是否可能泄漏。
- channel 是否可能阻塞、重复关闭或永不关闭。
- shared mutable state 是否有竞态或可见性问题。
- context 是否被正确传递、取消和尊重。
- retry、backoff、timeout 是否会放大故障或造成请求风暴。

### 数据一致性和外部边界

- DB 写入是否幂等，事务边界是否足够。
- 分页、游标、排序和过滤条件是否稳定。
- cache、DB、消息、RPC 之间是否存在可观察的不一致窗口。
- 外部服务失败、限流、部分成功和重复投递是否有处理策略。
- 日志、metric、trace 是否足以定位失败，但不泄漏敏感信息。

### 测试缺口

- 新逻辑是否有 table-driven tests 或项目等价测试。
- bugfix 是否有能失败再通过的回归用例。
- mock、fixture 和 fake 是否忠实覆盖边界行为，而不是只复刻实现。
- 高风险并发改动是否需要 race test、压力测试或集成测试。

## 可维护性规范

可维护性判断应结合项目事实，不要只套通用规则。优先观察同类包、成熟模块和 CI 约定。

### 包边界

- 尊重 Go 的包边界，尤其是 `internal/` 的可见性限制。
- 公共能力优先看项目已有 shared package。
- 不要为了单个需求随意新增跨层依赖。
- 避免 package 之间形成循环认知或循环依赖；新增依赖前先检查现有 import 方向。
- `cmd/` 负责组合和启动，业务逻辑通常应留在可测试的内部包中，除非项目已有不同结构。

### 模块演进

- 新增代码应放在现有 ownership 边界内，除非需求本身要求新边界。
- 不因为一次性需求创建过宽泛的 `utils`、`helpers`、`common` 能力。
- 共享 helper 应有明确调用方和稳定语义，避免把业务规则藏进通用包。
- 配置、client、repository、service、handler 等层次要匹配项目已有命名和调用方向。
- 对生成代码、协议文件、DB migration、API schema 的修改要同步记录生成或迁移流程。

### 生成代码和第三方代码

通常不要编辑：

- generated code
- vendor
- third_party
- protobuf 生成文件
- 自动生成的 mock

除非用户明确要求，或者项目已有明确生成流程。

### 测试风格

需要观察项目是否使用：

- table-driven tests
- fixtures
- mocks
- 集成测试脚本
- 外部数据库、消息队列、RPC 服务或节点服务

不要假设 `go test ./...` 一定能在本地无依赖通过。

## 常用命令

只有在项目适用时才使用这些命令：

```sh
go test ./...
go test ./path/to/package
go test -run TestName ./path/to/package
go test -cover ./...
gofmt
go vet ./...
golangci-lint run
golangci-lint fmt
go list ./...
```

如果项目提供了 `make test`、`make format`、`make lint`、CI 脚本或其他本地约定，应优先使用项目定义的命令。
