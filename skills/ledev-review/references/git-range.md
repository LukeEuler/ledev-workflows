# Git 范围

## 原则

只审查已经 commit 的、线性的、无 merge commit 的代码变更。任何复杂 Git 状态都应在 review 前简化；本 skill 不整理分支、不推断复杂比较关系、不审查工作区未提交内容。

## 支持模式

### committed-linear-range

用户输入：

```text
review A..B
review from A to B
review branch base to branch head
```

语义：

```sh
git diff A..B
git log --reverse --oneline A..B
```

`A` 是 base，`B` 是 head。审查 `A` 之后到 `B` 的提交，不包含 `A` 本身。

### single-commit

用户输入：

```text
review commit B
```

语义：

```sh
git diff B^..B
git log --reverse --oneline B^..B
```

要求 `B` 有且只有一个 parent，不是 root commit，不是 merge commit。

## 必要检查

在 review 前优先运行 skill 脚本：

```sh
scripts/preflight.sh --range A B
scripts/preflight.sh --commit B
```

脚本会检查工作区干净、revision 可解析、正向线性、范围非空、无 merge commit，并输出报告范围元数据和 diff stat。脚本不可用时，手工运行只读检查：

```sh
git rev-parse --is-inside-work-tree
git status --porcelain
git rev-parse --verify A^{commit}
git rev-parse --verify B^{commit}
git merge-base --is-ancestor A B
git log --reverse --oneline A..B
git rev-list --merges A..B
git diff --stat A..B
git diff A..B
```

单 commit：

```sh
git rev-parse --verify B^{commit}
git rev-list --parents -n 1 B
git diff B^..B
git log --reverse --oneline B^..B
```

## 合法性规则

- `git status --porcelain` 必须为空。未提交变更会污染本地文件读取结果。
- base 和 head 必须能解析为 commit。
- range 模式中，base 必须是 head 的祖先：`git merge-base --is-ancestor A B`。
- range 模式中，`git log --reverse --oneline A..B` 必须非空。
- range 模式中，`git rev-list --merges A..B` 必须为空。
- single commit 模式中，目标 commit 的 parent 数量必须等于 1。
- 不自动调换反向范围；要求用户重新指定。

## 拒绝提示

工作区不干净：

```text
当前工作区存在未提交变更。ledev-review 只审查已 commit 的代码。
请先 commit、stash 或清理工作区后重新执行 review。
```

非线性或反向范围：

```text
给定范围不是线性正向范围：base 不是 head 的祖先。
ledev-review 只审查线性提交序列。

如果你想审查 feature 相对 main 的变更，请先整理分支历史，例如：

git checkout feature
git fetch origin
git rebase origin/main

然后重新执行：

review main..feature
```

存在 merge commit：

```text
审查范围内存在 merge commit。ledev-review 只审查无 merge commit 的线性历史。
请先 rebase 或拆分变更，使审查范围成为简单提交序列。
```

空范围：

```text
给定范围没有待审提交，无需 review。
```

单 commit 不合法：

```text
目标 commit 不是可审查的单提交。ledev-review 的单 commit review 要求该提交不是 root commit、不是 merge commit，并且只有一个 parent。
```

## 报告元数据

每次 review 必须记录，优先直接引用 `scripts/preflight.sh` 输出：

```text
审查范围:
- 模式（Mode）: committed-linear-range | single-commit
- Base ref:
- Base commit:
- Head ref:
- Head commit:
- Diff expression:
- 提交数量:
- 提交列表:
- 工作区干净: yes
- 包含 merge commit: no
```
