# LEDev Workflows

## 中文说明

这个项目用于维护一组平台无关的 AI 开发工作流，并提供 Codex skill 适配。目标是把软件项目开发中的重复流程固化下来，辅助完成：

- 项目信息采集、校验和项目文档沉淀
- 编号 task 驱动的代码开发、模块实现和 bug 修复
- 测试、lint、构建验证
- 代码 review
- 开发、测试、review 相关工具生成

### 设计思路

`ledev-context` 是基础 skill。`ledev` 是 LukeEuler Development 的缩写，用于标识这组属于 LukeEuler 项目的开发工作流。它负责先全量观察代码和仓库文件，建立 `.ai/facts/` 结构化事实层，再基于事实层建立项目认知，包括项目结构、架构、命令、模块边界、风险区域、人为补充信息和待确认问题。

其他开发类 skill 不应该每次从零理解项目，而应该先读取已有项目上下文，再执行 task 创建、开发、review、测试或 bug 修复。

为了给不同语言留扩展口，语言相关规则放在：

```text
skills/ledev-context/rules/<language>.md
```

当前已包含：

- `rules/go.md`

后续可以继续增加：

- `rules/java.md`
- `rules/python.md`
- `rules/rust.md`
- `rules/javascript.md`

### Workflow / Skill 列表

- `ledev-context`：采集、校验、纠正并沉淀项目上下文，同时可生成 AI 工作上下文和人类项目文档。
- `ledev-task`：用带类型的 `T###` 编号 task 统一管理开发、实现、bug 修复、重构和验证收尾。
- `ledev-test`：选择合适的测试范围，补充或调整测试，诊断测试、lint、构建失败。
- `ledev-review`：以代码审查视角检查 diff，优先关注正确性、回归风险、错误处理、并发、数据一致性和测试缺口。
- `ledev-tool`：为重复性开发任务生成脚本、CLI、代码生成器或辅助工具。

### Codex 安装

当前提供 Codex 适配。通过软链接把 `skills/` 下的 skill 目录链接到 Codex 的公共 skills 目录：

```sh
./scripts/install-symlinks.sh
```

脚本默认行为：

- 如果设置了 `CODEX_HOME`，链接到 `$CODEX_HOME/skills`
- 否则链接到 `~/.codex/skills`
- 会清理旧名字的软链接：`project-context-builder`、`dev-implementation`、`dev-context`、`dev-fix`、`dev-impl`、`ledev-fix`、`ledev-impl`、`dev-review`、`dev-test`、`dev-tool`、`test-validation`、`code-review`、`bugfix-sop`、`tool-generator`
- 如果目标位置已经存在普通目录或文件，脚本会拒绝覆盖
- 如果目标位置已经是软链接，脚本会重新创建链接

### 推荐使用方式

一个完整开发任务可以按阶段执行：

1. 先用 `ledev-context scope` 轻量发现并确认扫描范围，写入 `.ai/scope/scan-scope.md`；再用 `scan` 全量观察代码和仓库文件，建立 `.ai/facts/` 结构化事实层；之后基于事实层收集或刷新项目画像，并通过文件化 QA 环节补齐 AI 无法确认的信息。`md` 生成 `.ai/project-context.md`，`html` 生成重新编排的 `.ai/project-context.html`；裸 `document` 默认依次执行两者。该 skill 面向中文用户，运行产物默认以中文为主，命令、路径、状态值和必要关键词可保留英文。QA 问题默认维护在 `.ai/qa/project-qa.md`，使用 `QA-001` 这类稳定编号；用户可以编辑文件回答，也可以在对话里按编号直接回答。QA 文档是长期项目知识，可作为最终上下文和人类文档的补充。
2. 开发、修复和重构需求用 `ledev-task`。该 skill 会先确认或创建带类型的 `T###` task，记录需求、范围、影响、方案、实现和验证结果；支持 `new` / `新建`、`continue` / `继续`、`restart` / `重启`、`view` / `查看`、`close` / `完成`、`block` / `阻塞`。
3. 测试验证治理用 `ledev-test`。`ledev-task` 内必须记录验证结果，复杂测试策略可交接给 `ledev-test`。
4. 代码审查用 `ledev-review`。
5. 重复性流程需要工具化时，用 `ledev-tool`。

项目画像建议放在目标项目的 `.ai/project-context.md`。如果目标项目不希望写入本地文件，也可以放到用户指定的位置。

多个 AI、多个 skill 或多个阶段协作时，建议使用 `.ai/state/` 目录记录运行进度。每个 skill 使用独立文件，例如 `.ai/state/ledev-context.md`、`.ai/state/ledev-task.md`、`.ai/state/ledev-test.md`，不要把不同 skill 的进度混在一个文件里。

`ledev-context` 需要保留两个人工校准区域：

- `Human Notes`：人主动补充的项目事实、团队约定、业务规则。
- `Corrections`：当 AI 理解错时，记录纠正内容，避免后续重复犯错。

### Skill 间契约

- `ledev-context` 产出 `.ai/scope/scan-scope.md`、`.ai/facts/`、`.ai/qa/project-qa.md`、`.ai/project-context.md` 和 `.ai/state/ledev-context.md`，供 task、review、test 和 tool 优先读取。
- `ledev-task` 产出 `.ai/tasks/T###-*.md`、`.ai/tasks/index.md` 和 `.ai/state/ledev-task.md`。其他 skill 读取 task 的目标、范围、方案、实现记录、验证记录和 `Handoff / Next`，用于判断用户意图、验证范围和后续工作。
- `ledev-review` 产出 `.ai/reviews/` 和 `.ai/state/ledev-review.md`。review 读取 context facts 和相关 task；如果发现需要修复的问题，转交给 task 工作流，不直接改代码。
- `.ai/state/<skill>.md` 只记录运行锚点，不替代长期事实、task、review 报告或 QA 文档。
- 共享协议见 `skills/_shared/references/shared-rules.md`：operation 解析、中文优先、git 检查、`.ai/` 写入、路径可移植性和多仓库默认边界。

---

## English

This project maintains platform-neutral AI development workflows and provides a Codex skill adapter. The workflows help with:

- project context collection, validation, correction, and documentation
- task-driven implementation work and bug fixing
- test, lint, and build validation
- code review
- development, testing, and review helper/tool generation

### Design

`ledev-context` is the foundation skill. `ledev` stands for LukeEuler Development and identifies this set of LukeEuler project workflows. It first observes code and repository files to build a structured `.ai/facts/` fact layer, then uses that fact layer to build reusable project knowledge: repository structure, architecture, commands, module boundaries, risk areas, human notes, and open questions.

Other development skills should read the existing project context before task creation, implementation, review, testing, or bug fixing instead of rediscovering the project from scratch.

Language-specific rules live under:

```text
skills/ledev-context/rules/<language>.md
```

Currently included:

- `rules/go.md`

Future rules can be added for:

- `rules/java.md`
- `rules/python.md`
- `rules/rust.md`
- `rules/javascript.md`

### Workflows / Skills

- `ledev-context`: Collects, validates, corrects, and documents project context. Produces AI working context and optional human-readable project docs.
- `ledev-task`: Tracks implementation, bug fixes, refactors, and validation closure through typed numbered `T###` tasks.
- `ledev-test`: Selects the right validation scope, adds or adjusts tests, and diagnoses test, lint, or build failures.
- `ledev-review`: Reviews diffs with a focus on correctness, regressions, error handling, concurrency, data consistency, and missing tests.
- `ledev-tool`: Creates scripts, CLIs, code generators, or helper tools for repeated development workflows.

### Codex Install

The current adapter supports Codex. Symlink the skill directories into the Codex shared skills directory:

```sh
./scripts/install-symlinks.sh
```

Script behavior:

- Uses `$CODEX_HOME/skills` when `CODEX_HOME` is set
- Otherwise uses `~/.codex/skills`
- Removes legacy symlinks: `project-context-builder`, `dev-implementation`, `dev-context`, `dev-fix`, `dev-impl`, `ledev-fix`, `ledev-impl`, `dev-review`, `dev-test`, `dev-tool`, `test-validation`, `code-review`, `bugfix-sop`, `tool-generator`
- Refuses to overwrite existing non-symlink files or directories
- Recreates existing symlinks

### Suggested Usage

A complete development workflow can be split into phases:

1. Use `ledev-context scope` to lightly discover and confirm scan scope in `.ai/scope/scan-scope.md`; then use `scan` to fully observe code and repository files and build a structured `.ai/facts/` fact layer. Then collect or refresh project context from that fact layer and use file-first QA to fill in facts AI cannot confirm. `md` writes `.ai/project-context.md`, `html` writes a reorganized `.ai/project-context.html`, and bare `document` runs both by default. QA questions are maintained in `.ai/qa/project-qa.md` by default with stable IDs such as `QA-001`; users can answer by editing the file or replying inline with the ID. The QA document is long-lived project knowledge and can supplement final context and human docs.
2. Use `ledev-task` for implementation, bug fixes, and refactors. It creates or continues a typed numbered `T###` task and records requirements, scope, impact, decisions, implementation notes, and validation results.
3. Use `ledev-test` for testing and verification governance. `ledev-task` must still record validation results and can hand complex validation work to `ledev-test`.
4. Use `ledev-review` for review tasks.
5. Use `ledev-tool` when a repeated workflow should become a tool.

The project context summary is usually stored at `.ai/project-context.md` inside the target project. If the target project should not be modified, store it in a user-specified location instead.

When multiple AI agents, skills, or phases collaborate, use the `.ai/state/` directory for runtime progress. Each skill should use its own file, such as `.ai/state/ledev-context.md`, `.ai/state/ledev-task.md`, or `.ai/state/ledev-test.md`; do not mix multiple skills' progress into one file.

`ledev-context` should preserve two human calibration sections:

- `Human Notes`: user-provided project facts, team conventions, and business rules.
- `Corrections`: explicit corrections when AI misunderstood the project, so future work does not repeat the same mistake.

### Cross-Skill Contracts

- `ledev-context` writes `.ai/scope/scan-scope.md`, `.ai/facts/`, `.ai/qa/project-qa.md`, `.ai/project-context.md`, and `.ai/state/ledev-context.md` for task, review, test, and tool workflows to read first.
- `ledev-task` writes `.ai/tasks/T###-*.md`, `.ai/tasks/index.md`, and `.ai/state/ledev-task.md`. Other skills read task goals, scope, selected plan, implementation log, validation log, and `Handoff / Next` to understand intent and follow-up work.
- `ledev-review` writes `.ai/reviews/` and `.ai/state/ledev-review.md`. Review reads context facts and related tasks; when fixes are needed, it hands them to the task workflow instead of editing code directly.
- `.ai/state/<skill>.md` stores runtime anchors only; it does not replace long-lived facts, tasks, review reports, or QA documents.
- Shared protocol lives in `skills/_shared/references/shared-rules.md`: operation parsing, Chinese-first output, git checks, `.ai/` writes, path portability, and multi-repo boundaries.
