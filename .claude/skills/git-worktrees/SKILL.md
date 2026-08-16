---
name: git-worktrees
description: 用于功能开发需要与当前工作区隔离、或即将执行实现计划时——优先原生 worktree 工具、git worktree 兜底，确保隔离工作区存在。
---

# 使用 Git Worktree

## 概述

确保工作在隔离的工作区中进行。优先使用所在平台的原生 worktree 工具。仅当没有原生工具可用时，才回退到手动 git worktree。

**核心原则：** 先探测已有隔离。再用原生工具。最后才回退 git。永远不要和执行环境对着干。

**开始时宣告：** "我正在使用 git-worktrees 技能建立隔离工作区。"

## 第 0 步：探测已有隔离

**创建任何东西之前，先检查你是否已身处隔离工作区。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**子模块防护：** 在 git 子模块里 `GIT_DIR != GIT_COMMON` 同样成立。下结论"已在 worktree 中"之前，先确认自己不在子模块里：

```bash
# 若此命令返回了路径，你在子模块里而非 worktree——按普通仓库处理
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**若 `GIT_DIR != GIT_COMMON`（且不是子模块）：** 你已在一个链接 worktree 中。直接跳到第 2 步（项目设置）。不要再建 worktree。

带分支状态汇报：
- 在分支上："已在隔离工作区 `<路径>`，分支 `<名称>`。"
- 游离 HEAD："已在隔离工作区 `<路径>`（游离 HEAD，由外部管理）。收尾时需要建分支。"

**若 `GIT_DIR == GIT_COMMON`（或身处子模块）：** 你在普通仓库检出中。

你的指示里是否已声明 worktree 偏好？若没有，创建 worktree 之前先征求同意：

> "要我建一个隔离的 worktree 吗？它能保护你当前分支不被改动。"

已声明的偏好直接遵循，不必再问。用户不同意时，就地工作并跳到第 2 步。

## 第 1 步：创建隔离工作区

**你有两种机制，按此顺序尝试。**

### 1a. 原生 worktree 工具（优先）

用户已要求隔离工作区（第 0 步已同意）。你手上是否已有创建 worktree 的途径？它可能是名为 `EnterWorktree`、`WorktreeCreate` 的工具，`/worktree` 命令，或 `--worktree` 标志。有就用它，然后跳到第 2 步。

原生工具自动处理目录位置、分支创建与清理。明明有原生工具还去用 `git worktree add`，会制造执行环境看不见也管不了的幽灵状态。

只有确实没有原生 worktree 工具时，才继续 1b。

### 1b. Git Worktree 兜底

**仅当 1a 不适用时使用**——没有任何原生 worktree 工具。用 git 手动创建 worktree。

#### 目录选择

按此优先级执行。用户显式声明的偏好永远压过观察到的文件系统现状。

1. **查你的指示中是否声明了 worktree 目录偏好。** 用户已指定就直接用，不再询问。

2. **查项目内是否已有 worktree 目录：**
   ```bash
   ls -d .worktrees 2>/dev/null     # 优先（隐藏）
   ls -d worktrees 2>/dev/null      # 备选
   ```
   找到就用。两个都存在时，`.worktrees` 胜出。

3. **没有任何其他指引时**，默认用项目根下的 `.worktrees/`。

#### 安全验证（仅针对项目内目录）

**创建 worktree 之前，必须验证目录已被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**若未被忽略：** 加入 .gitignore，提交该变更，然后继续。

**为何致命：** 防止 worktree 的全部内容被误提交进仓库。

#### 创建 worktree

```bash
# 按所选位置决定路径
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**沙箱兜底：** 若 `git worktree add` 因权限错误（沙箱拒绝）失败，告诉用户沙箱阻止了 worktree 创建、你将改在当前目录工作。然后就地执行项目设置与基线测试。

### 1c. 退出与清理：保留还是删除

离开隔离工作区时的决策规则：

- **工作未完成、或后续还需回看：保留**。向用户说明 worktree 路径与分支名，收尾会话可直接重入。
- **已完成且已合并：删除**。有原生工具时，用其退出动作选"删除"；手动路径则 `git worktree remove <路径>` 并删除对应分支。
- **有未提交变更时禁止直接删**：先向用户确认是丢弃、还是先提交/合并。
- 原生工具退出时若询问"保留/删除"，只要还有未合并的变更，必须选保留。

## 第 2 步：项目设置

自动探测并执行相应的设置：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## 第 3 步：验证干净基线

运行测试，确保工作区从干净状态起步：

```bash
# 使用项目对应的命令
npm test / cargo test / pytest / go test ./...
```

**若测试失败：** 汇报失败情况，询问是继续还是先调查。

**若测试通过：** 汇报就绪。

### 汇报

```
Worktree 就绪于 <完整路径>
测试通过（<N> 个测试，0 失败）
可以开始实现 <功能名>
```

## 速查表

| 情形 | 动作 |
|-----------|--------|
| 已在链接 worktree 中 | 跳过创建（第 0 步） |
| 身处子模块 | 按普通仓库处理（第 0 步防护） |
| 有原生 worktree 工具 | 用它（1a） |
| 没有原生工具 | git worktree 兜底（1b） |
| `.worktrees/` 已存在 | 用它（验证已被忽略） |
| `worktrees/` 已存在 | 用它（验证已被忽略） |
| 两个都存在 | 用 `.worktrees/` |
| 都不存在 | 查指示文件，再默认 `.worktrees/` |
| 目录未被忽略 | 加入 .gitignore 并提交 |
| 创建时报权限错误 | 沙箱兜底，就地工作 |
| 基线测试失败 | 汇报失败 + 询问 |
| 没有 package.json/Cargo.toml | 跳过依赖安装 |
| 工作未完成需退出 | 保留 worktree（1c） |
| 已完成且已合并 | 删除 worktree 与分支（1c） |

## 常见自我合理化

| 借口 | 现实 |
|--------|---------|
| "我显然不在 worktree 里——不用查" | 跑第 0 步。执行环境创建的隔离和子模块都会骗过肉眼；探测命令一锤定音。 |
| "`git worktree add` 比找原生工具快" | 原生工具（如 `EnterWorktree`）掌管位置、分支与清理。绕过它是头号错误——它会制造执行环境看不见也管不了的幽灵状态。 |
| "worktree 目录肯定已经被忽略了" | 跑 `git check-ignore`。未被忽略的 worktree 目录会把整棵树提交进仓库。 |
| "随便什么目录名都行" | 显式指示 > 已有的项目内目录 > `.worktrees/` 默认值。 |
| "工作区是全新的——基线测试可以等等" | 脏基线让之后的每次失败都无法归因。现在就跑测试；带着失败继续与否由用户决定。 |
| "退出了留着也无所谓" | 未清理的 worktree 会积累幽灵分支与目录。按 1c 的保留/删除规则处理。 |
