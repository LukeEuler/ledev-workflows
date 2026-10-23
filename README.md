# LEDev Workflows

## 中文说明

这个项目用于维护一组平台无关的 AI 开发工作流，并提供 Codex 和 Claude Code skill 适配。目标是把软件项目开发中的重复流程固化下来，辅助完成：

- 项目信息采集、校验和项目文档沉淀
- 编号 task 驱动的代码开发、模块实现和 bug 修复
- 测试、lint、构建验证
- 代码 review
- 开发、测试、review 相关工具生成

### 设计思路

`ledev` 用于标识这组开发工作流。每个 skill 都可以独立运行；`ledev-context` 是用户主动选择的可选项目知识层，不是其他 skill 的基础阶段或默认前置条件。

项目已经存在 `ledev-context` 产物时，其他 skill 可以静默读取相关事实；项目没有这些产物时，必须直接依靠仓库、代码和用户意图完成自身工作，不提示用户初始化 context。

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
- `ledev-review`：以代码审查视角检查 diff，优先关注正确性、回归风险、错误处理、并发、数据一致性和测试缺口。

### 安装

当前提供 Codex 和 Claude Code 适配。通过同一个脚本把 `skills/` 复制同步到已存在的个人 skills 目录。

```sh
./scripts/install-skills.sh
```

脚本会自动识别并同步：

- Codex：优先使用 `$LEDEV_CODEX_HOME`、`$CODEX_HOME`，否则使用 `~/.codex`
- Claude Code：优先使用 `$LEDEV_CLAUDE_CODE_HOME`、`$CLAUDE_CODE_HOME`，否则使用 `~/.claude`
- 只有对应根目录已经存在时才会同步；缺少 Codex 或 Claude Code 的目录时会跳过，不会创建该工具的根目录
- 只复制包含 `SKILL.md` 的 skill 目录，并同时复制内部依赖 `_shared`；`_shared` 不会作为可调用 skill 暴露
- 已由本项目安装的 skill 和旧版软链接会更新；同名但并非由本项目管理的普通目录会跳过，避免覆盖用户内容

升级本项目后，再运行同一条命令即可更新已安装的 Codex 和 Claude Code skills：

```sh
git pull
./scripts/install-skills.sh
```

Claude Code 使用目录名作为 slash command，例如安装后可用 `/ledev-context scope` 或 `/ledev-task new ...`。这些 skill 仍使用同一份 `SKILL.md`；通常不需要为 Claude Code 复制一份 skill 文件，只需要在说明中同时兼容 Codex 的 `$ledev-*` 和 Claude Code 的 `/ledev-*` 调用方式。

### 独立使用方式

- 开发、修复和重构需求直接使用 `ledev-task`。它独立观察项目结构和代码，记录需求、范围、方案、实现与验证结果。
- 审阅已经提交的线性 Git 变更直接使用 `ledev-review`。它独立依据 Git、代码和用户意图完成 review。
- 只有用户主动希望建立或维护长期项目知识时，才显式使用 `ledev-context` 的 `scope`、`scan`、`document` 等 mode。
- 任何 skill 都不得因为项目没有 `ledev-context` 产物而推荐、启动或要求 context 工作流。

项目画像建议放在目标项目的 `.ai/ledev/project-context.md`。如果目标项目不希望写入本地文件，也可以放到用户指定的位置。

多个 AI、多个 skill 或多个阶段协作时，建议使用 `.ai/ledev/state/` 目录记录运行进度。每个 skill 使用独立文件，例如 `.ai/ledev/state/ledev-context.md`、`.ai/ledev/state/ledev-task.md`、`.ai/ledev/state/ledev-test.md`，不要把不同 skill 的进度混在一个文件里。

`ledev-context` 需要保留两个人工校准区域：

- `Human Notes`：人主动补充的项目事实、团队约定、业务规则。
- `Corrections`：当 AI 理解错时，记录纠正内容，避免后续重复犯错。

### Skill 间契约

- `ledev-context` 仅在用户主动调用时产出 `.ai/ledev/scope/scan-scope.md`、`.ai/ledev/facts/`、`.ai/ledev/qa/project-qa.md`、`.ai/ledev/project-context.md` 和 `.ai/ledev/state/ledev-context.md`。其他 skill 只在这些产物已经存在时按需读取。
- `ledev-task` 产出 `.ai/ledev/tasks/T###-*.md`、`.ai/ledev/tasks/index.md` 和 `.ai/ledev/state/ledev-task.md`。其他 skill 读取 task 的目标、范围、方案、实现记录、验证记录和 `Handoff / Next`，用于判断用户意图、验证范围和后续工作。
- `ledev-review` 产出 `.ai/ledev/reviews/` 和 `.ai/ledev/state/ledev-review.md`。review 读取相关 task，并在已有 context facts 时将其作为可选证据；如果发现需要修复的问题，转交给 task 工作流，不直接改代码。
- `.ai/ledev/state/<skill>.md` 只记录运行锚点，不替代长期事实、task、review 报告或 QA 文档。
- 共享协议见 `skills/_shared/references/shared-rules.md`：operation 解析、中文优先、git 检查、`.ai/ledev/` 写入、路径可移植性和多仓库默认边界。

---

## English

This project maintains platform-neutral AI development workflows and provides Codex and Claude Code skill adapters. The workflows help with:

- project context collection, validation, correction, and documentation
- task-driven implementation work and bug fixing
- test, lint, and build validation
- code review
- development, testing, and review helper/tool generation

### Design

`ledev` identifies this set of development workflows. Every skill runs independently. `ledev-context` is an optional project knowledge layer chosen explicitly by the user, not a foundation stage or prerequisite for other skills.

When context artifacts already exist, another skill may read relevant facts silently. When they do not exist, the skill must rely on the repository, code, and user intent without suggesting context initialization.

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
- `ledev-review`: Reviews diffs with a focus on correctness, regressions, error handling, concurrency, data consistency, and missing tests.

### Install

The adapters support Codex and Claude Code. One script copies and syncs skills to the personal skills directories that already exist.

```sh
./scripts/install-skills.sh
```

The script automatically detects and syncs:

- Codex: `$LEDEV_CODEX_HOME`, then `$CODEX_HOME`, otherwise `~/.codex`
- Claude Code: `$LEDEV_CLAUDE_CODE_HOME`, then `$CLAUDE_CODE_HOME`, otherwise `~/.claude`
- It syncs only when that tool's root directory already exists. A missing Codex or Claude Code root is skipped; it is not created.
- It copies skill directories containing `SKILL.md` plus the internal `_shared` dependency. `_shared` is not exposed as a callable skill.
- Skills previously installed by this project and legacy symlinks are updated. Unmanaged ordinary directories with the same name are skipped to avoid overwriting user content.

After upgrading this project, run the same command to update installed Codex and Claude Code skills:

```sh
git pull
./scripts/install-skills.sh
```

Claude Code uses the directory name as the slash command, for example `/ledev-context scope` or `/ledev-task new ...`. The same `SKILL.md` files are used for both adapters; a separate Claude Code copy is usually unnecessary.

### Independent Usage

- Use `ledev-task` directly for implementation, bug fixes, and refactors. It inspects the repository and code independently and records requirements, scope, decisions, implementation notes, and validation results.
- Use `ledev-review` directly for committed linear Git reviews. It works from Git, code, and user intent independently.
- Use `ledev-context` modes only when the user explicitly chooses to build or maintain long-lived project knowledge.
- No skill may recommend, start, or require a context workflow merely because context artifacts are absent.

The project context summary is usually stored at `.ai/ledev/project-context.md` inside the target project. If the target project should not be modified, store it in a user-specified location instead.

When multiple AI agents, skills, or phases collaborate, use the `.ai/ledev/state/` directory for runtime progress. Each skill should use its own file, such as `.ai/ledev/state/ledev-context.md`, `.ai/ledev/state/ledev-task.md`, or `.ai/ledev/state/ledev-test.md`; do not mix multiple skills' progress into one file.

`ledev-context` should preserve two human calibration sections:

- `Human Notes`: user-provided project facts, team conventions, and business rules.
- `Corrections`: explicit corrections when AI misunderstood the project, so future work does not repeat the same mistake.

### Cross-Skill Contracts

- `ledev-context` writes `.ai/ledev/scope/scan-scope.md`, `.ai/ledev/facts/`, `.ai/ledev/qa/project-qa.md`, `.ai/ledev/project-context.md`, and `.ai/ledev/state/ledev-context.md` only when explicitly invoked. Other skills read them only when they already exist.
- `ledev-task` writes `.ai/ledev/tasks/T###-*.md`, `.ai/ledev/tasks/index.md`, and `.ai/ledev/state/ledev-task.md`. Other skills read task goals, scope, selected plan, implementation log, validation log, and `Handoff / Next` to understand intent and follow-up work.
- `ledev-review` writes `.ai/ledev/reviews/` and `.ai/ledev/state/ledev-review.md`. Review reads related tasks and treats existing context facts as optional evidence; when fixes are needed, it hands them to the task workflow instead of editing code directly.
- `.ai/ledev/state/<skill>.md` stores runtime anchors only; it does not replace long-lived facts, tasks, review reports, or QA documents.
- Shared protocol lives in `skills/_shared/references/shared-rules.md`: operation parsing, Chinese-first output, git checks, `.ai/ledev/` writes, path portability, and multi-repo boundaries.
