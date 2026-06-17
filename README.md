# LEDev Workflows

## 中文说明

这个项目用于维护一组平台无关的 AI 开发工作流，并提供 Codex skill 适配。目标是把软件项目开发中的重复流程固化下来，辅助完成：

- 项目信息采集、校验和项目文档沉淀
- 代码开发和模块实现
- 测试、lint、构建验证
- 代码 review
- bug 复现、定位、修复和回归验证
- 开发、测试、review 相关工具生成

### 设计思路

`ledev-context` 是基础 skill。`ledev` 是 LukeEuler Development 的缩写，用于标识这组属于 LukeEuler 项目的开发工作流。它负责先全量观察代码和仓库文件，建立 `.ai/facts/` 结构化事实层，再基于事实层建立项目认知，包括项目结构、架构、命令、模块边界、风险区域、人为补充信息和待确认问题。

其他开发类 skill 不应该每次从零理解项目，而应该先读取已有项目上下文，再执行开发、review、测试或 bug 修复。

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
- `ledev-impl`：实现代码改动时，优先复用项目已有模式，控制改动范围，并执行格式化和验证。
- `ledev-test`：选择合适的测试范围，补充或调整测试，诊断测试、lint、构建失败。
- `ledev-review`：以代码审查视角检查 diff，优先关注正确性、回归风险、错误处理、并发、数据一致性和测试缺口。
- `ledev-fix`：按复现、定位、解释根因、窄范围修复、验证的顺序处理 bug。
- `ledev-tool`：为重复性开发任务生成脚本、CLI、代码生成器或辅助工具。

### Codex 安装

当前提供 Codex 适配。通过软链接把 `skills/` 下的 skill 目录链接到 Codex 的公共 skills 目录：

```sh
./scripts/install-symlinks.sh
```

脚本默认行为：

- 如果设置了 `CODEX_HOME`，链接到 `$CODEX_HOME/skills`
- 否则链接到 `~/.codex/skills`
- 会清理旧名字的软链接：`project-context-builder`、`dev-implementation`、`dev-context`、`dev-fix`、`dev-impl`、`dev-review`、`dev-test`、`dev-tool`、`test-validation`、`code-review`、`bugfix-sop`、`tool-generator`
- 如果目标位置已经存在普通目录或文件，脚本会拒绝覆盖
- 如果目标位置已经是软链接，脚本会重新创建链接

### 推荐使用方式

一个完整开发任务可以按阶段执行：

1. 先用 `ledev-context scope` 轻量发现并确认扫描范围，写入 `.ai/scope/scan-scope.md`；再用 `scan` 全量观察代码和仓库文件，建立 `.ai/facts/` 结构化事实层；之后基于事实层收集或刷新项目画像，并通过文件化 QA 环节补齐 AI 无法确认的信息。`md` 生成 `.ai/project-context.md`，`html` 生成重新编排的 `.ai/project-context.html`；裸 `document` 默认依次执行两者。该 skill 面向中文用户，运行产物默认以中文为主，命令、路径、状态值和必要关键词可保留英文。QA 问题默认维护在 `.ai/qa/project-qa.md`，使用 `QA-001` 这类稳定编号；用户可以编辑文件回答，也可以在对话里按编号直接回答。QA 文档是长期项目知识，可作为最终上下文和人类文档的补充。
2. 开发需求用 `ledev-impl`。
3. 测试验证用 `ledev-test`。
4. 代码审查用 `ledev-review`。
5. bug 修复用 `ledev-fix`。
6. 重复性流程需要工具化时，用 `ledev-tool`。

项目画像建议放在目标项目的 `.ai/project-context.md`。如果目标项目不希望写入本地文件，也可以放到用户指定的位置。

多个 AI、多个 skill 或多个阶段协作时，建议使用 `.ai/state/` 目录记录运行进度。每个 skill 使用独立文件，例如 `.ai/state/ledev-context.md`、`.ai/state/ledev-impl.md`、`.ai/state/ledev-test.md`，不要把不同 skill 的进度混在一个文件里。

`ledev-context` 需要保留两个人工校准区域：

- `Human Notes`：人主动补充的项目事实、团队约定、业务规则。
- `Corrections`：当 AI 理解错时，记录纠正内容，避免后续重复犯错。

---

## English

This project maintains platform-neutral AI development workflows and provides a Codex skill adapter. The workflows help with:

- project context collection, validation, correction, and documentation
- implementation work
- test, lint, and build validation
- code review
- bug reproduction, localization, fixing, and regression validation
- development, testing, and review helper/tool generation

### Design

`ledev-context` is the foundation skill. `ledev` stands for LukeEuler Development and identifies this set of LukeEuler project workflows. It first observes code and repository files to build a structured `.ai/facts/` fact layer, then uses that fact layer to build reusable project knowledge: repository structure, architecture, commands, module boundaries, risk areas, human notes, and open questions.

Other development skills should read the existing project context before implementation, review, testing, or bug fixing instead of rediscovering the project from scratch.

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
- `ledev-impl`: Guides implementation work by following existing project patterns, keeping edits narrow, and running formatting and validation.
- `ledev-test`: Selects the right validation scope, adds or adjusts tests, and diagnoses test, lint, or build failures.
- `ledev-review`: Reviews diffs with a focus on correctness, regressions, error handling, concurrency, data consistency, and missing tests.
- `ledev-fix`: Handles bugs through reproduce, localize, explain root cause, patch narrowly, and verify.
- `ledev-tool`: Creates scripts, CLIs, code generators, or helper tools for repeated development workflows.

### Codex Install

The current adapter supports Codex. Symlink the skill directories into the Codex shared skills directory:

```sh
./scripts/install-symlinks.sh
```

Script behavior:

- Uses `$CODEX_HOME/skills` when `CODEX_HOME` is set
- Otherwise uses `~/.codex/skills`
- Removes legacy symlinks: `project-context-builder`, `dev-implementation`, `dev-context`, `dev-fix`, `dev-impl`, `dev-review`, `dev-test`, `dev-tool`, `test-validation`, `code-review`, `bugfix-sop`, `tool-generator`
- Refuses to overwrite existing non-symlink files or directories
- Recreates existing symlinks

### Suggested Usage

A complete development workflow can be split into phases:

1. Use `ledev-context scope` to lightly discover and confirm scan scope in `.ai/scope/scan-scope.md`; then use `scan` to fully observe code and repository files and build a structured `.ai/facts/` fact layer. Then collect or refresh project context from that fact layer and use file-first QA to fill in facts AI cannot confirm. `md` writes `.ai/project-context.md`, `html` writes a reorganized `.ai/project-context.html`, and bare `document` runs both by default. QA questions are maintained in `.ai/qa/project-qa.md` by default with stable IDs such as `QA-001`; users can answer by editing the file or replying inline with the ID. The QA document is long-lived project knowledge and can supplement final context and human docs.
2. Use `ledev-impl` for implementation tasks.
3. Use `ledev-test` for testing and verification.
4. Use `ledev-review` for review tasks.
5. Use `ledev-fix` for bug fixes.
6. Use `ledev-tool` when a repeated workflow should become a tool.

The project context summary is usually stored at `.ai/project-context.md` inside the target project. If the target project should not be modified, store it in a user-specified location instead.

When multiple AI agents, skills, or phases collaborate, use the `.ai/state/` directory for runtime progress. Each skill should use its own file, such as `.ai/state/ledev-context.md`, `.ai/state/ledev-impl.md`, or `.ai/state/ledev-test.md`; do not mix multiple skills' progress into one file.

`ledev-context` should preserve two human calibration sections:

- `Human Notes`: user-provided project facts, team conventions, and business rules.
- `Corrections`: explicit corrections when AI misunderstood the project, so future work does not repeat the same mistake.
