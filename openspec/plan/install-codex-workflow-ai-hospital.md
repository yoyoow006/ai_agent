# 严格实施计划：安装 Codex AI 工作流到 ai_hospital

## 目标与全局约束

- 源工作区：`/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital`，分支 `feature/install-codex-workflow-ai-hospital`。
- 写入目标：`/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital`。不得把包含符号链接的 `/home/yoyoo/wksoft/...` 路径传给安装器。
- 只安装 Codex 单侧适配；不安装 `.claude/` 或 `CLAUDE.md`。
- 不初始化 Git、不创建目标提交、不推送、不联网、不安装依赖、不执行 `openspec init/update`。
- 不读取或修改 `docs/好实用合作协议I51.2.doc` 正文；只允许 `stat` 与 `sha256sum` 元数据/哈希校验。
- 不修改目标中任何嵌套业务仓库；预检发现 `.git` 时停止。
- 本任务是离线内容安装，不修改运行时代码，不使用 TDD；验证采用清单预览、结构校验、哈希不变量、幂等性和 OpenSpec 严格校验。
- 任何预检、安装、验证或审查失败均停止；不得手工修补安装器事务结果，不得删除成功写入的工作流文件来回滚。

## 任务 1：源流程状态固化和写入前预检

### Create/Modify

- Modify: `openspec/changes/install-codex-workflow-ai-hospital/proposal.md`
- Modify: `openspec/changes/install-codex-workflow-ai-hospital/tasks.md`
- 不修改目标目录。

### 步骤

1. 用户第二次确认后，将 proposal 状态改为`构建中`，只提交四件套、本计划和状态更新。
2. 解析并核对目标真实路径：

   ```bash
   /usr/bin/readlink -e /home/yoyoo/wksoft/sources/gitdemo/ai_hospital
   ```

   预期输出精确为：

   ```text
   /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital
   ```

3. 确认目标根不是 Git 仓库且没有嵌套 `.git`：

   ```bash
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.git
   /usr/bin/find /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital -name .git -print
   ```

   预期第一条退出码为 0，第二条无输出。

4. 确认工作流入口和 Claude 适配仍不存在：

   ```bash
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/AGENTS.md
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.codex
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.ai
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/openspec
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/CLAUDE.md
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.claude
   ```

   预期全部退出码为 0。

5. 记录用户文档不变量：

   ```bash
   /usr/bin/stat -c '%n|%s|%y|%A|%U:%G' '/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/docs/好实用合作协议I51.2.doc'
   /usr/bin/sha256sum '/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/docs/好实用合作协议I51.2.doc'
   ```

   预期 SHA-256 精确为：

   ```text
   9a76ae560637818368ddbbaa298409747210a066c0c061224c257b798b25787f
   ```

6. 紧邻写入重新预览：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital
   /usr/bin/bash scripts/install-ai-workflow.sh      --target /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital      --assistant codex      --dry-run
   ```

   预期退出码 0，末行包含：

   ```text
   created=55 updated=0 unchanged=0 dry_run=1
   ```

### 失败路径

- 真实路径、Git 状态、入口状态、用户文档哈希或 dry-run 汇总任一不匹配：停止，不执行任务 2，向用户报告事实并等待决定。
- 目标出现新的非清单文件：不删除、不覆盖；仅当其成为安装清单冲突时停止。

## 任务 2：执行离线事务安装

### Create/Modify

- 目标侧创建 55 个 manifest 文件：`.ai/` 20 个、`.codex/` 19 个、根入口 2 个、OpenSpec 基线 8 个、校验套件 6 个。
- 源侧只更新 `openspec/changes/install-codex-workflow-ai-hospital/tasks.md` 的任务 3、4 勾选与证据。

### 步骤

1. 从源 worktree 执行唯一写入命令：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital
   /usr/bin/bash scripts/install-ai-workflow.sh      --target /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital      --assistant codex
   ```

   预期退出码 0，末行包含：

   ```text
   created=55 updated=0 unchanged=0 dry_run=0
   ```

2. 核对关键入口存在且为普通文件/目录：

   ```bash
   /usr/bin/test -f /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/AGENTS.md
   /usr/bin/test -d /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.codex
   /usr/bin/test -d /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.ai
   /usr/bin/test -d /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/openspec
   /usr/bin/test -f /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/scripts/validate-workflow.sh
   /usr/bin/test -f /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.ai/installer-ledger.json
   ```

3. 核对禁止项不存在：

   ```bash
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.git
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/CLAUDE.md
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.claude
   ```

4. 解析目标台账 JSON：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital
   /usr/bin/python3 -m json.tool .ai/installer-ledger.json
   ```

   预期退出码 0，且输出包含 Codex 安装清单内容，不要求在对话中展开全部正文。

### 失败路径

- 安装器退出码非 0：停止，保留完整输出；若安装器报告 rollback failed，不得手工猜测修复，立即向用户报告并请求决定。
- 关键入口缺失或禁止项存在：停止，不运行归档；先核对安装器输出与台账。

## 任务 3：目标完整验证与不变量复核

### Create/Modify

- 不修改目标工作流资产。
- 允许目标校验器创建其声明的本地校验缓存；不得创建 `.git`、`.claude/`、`CLAUDE.md` 或业务文件。
- 源侧更新 `tasks.md` 的任务 5 勾选与验证证据。

### 步骤

1. 复核安装幂等性：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital
   /usr/bin/bash scripts/install-ai-workflow.sh      --target /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital      --assistant codex      --dry-run
   ```

   预期退出码 0，末行包含：

   ```text
   created=0 updated=0 unchanged=55 dry_run=1
   ```

2. 运行目标 required 工作流门禁。显式加入已存在的 OpenSpec CLI 目录，不联网安装：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital
   PATH=/home/yoyoo/.nvm/versions/node/v20.19.4/bin:$PATH      /usr/bin/bash scripts/validate-workflow.sh --require-openspec
   ```

   预期退出码 0，输出 `FAIL=0` 且 `SKIP=0`。

3. 运行目标 OpenSpec 严格校验：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital
   /home/yoyoo/.nvm/versions/node/v20.19.4/bin/openspec validate --all --strict --no-interactive
   ```

   预期退出码 0，`failed=0`。

4. 复核用户文档不变量：

   ```bash
   /usr/bin/stat -c '%n|%s|%y|%A|%U:%G' '/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/docs/好实用合作协议I51.2.doc'
   /usr/bin/sha256sum '/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/docs/好实用合作协议I51.2.doc'
   ```

   预期 SHA-256 仍为：

   ```text
   9a76ae560637818368ddbbaa298409747210a066c0c061224c257b798b25787f
   ```

5. 复核目标根只新增计划内顶层入口，且没有 Git/Claude 禁止项：

   ```bash
   /bin/ls -la /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital
   /usr/bin/find /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital -name .git -print
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/CLAUDE.md
   /usr/bin/test ! -e /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital/.claude
   ```

### 失败路径

- 幂等预览不是 55 个 unchanged：停止，报告具体差异。
- required 门禁或 OpenSpec 校验失败：停止，保留输出；不得通过删除或改写校验器来达成绿灯。
- 用户文档哈希变化：停止并报告；不尝试恢复该用户文件。
- 禁止项出现：停止，不归档。

## 任务 4：高风险不变量任务级审查

### 审查单元

- 合并为一个不变量：`external-target-install-safety`。
- 覆盖：真实路径、无符号链接写入、非计划用户文件保全、Codex-only 边界、非 Git 目标、事务安装结果与验证证据。

### 步骤

1. 在源 worktree 冻结审查范围：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital
   /usr/bin/python3 .ai/tools/review_manifest.py freeze      --change install-codex-workflow-ai-hospital      --workspace "$PWD"      --repo-spec "$PWD::main"      --output .ai-local/reviews/install-codex-workflow-ai-hospital/task-1.json
   ```

2. 独立 reviewer 在读取审查材料前和形成结论前分别执行：

   ```bash
   /usr/bin/python3 .ai/tools/review_manifest.py verify      --manifest .ai-local/reviews/install-codex-workflow-ai-hospital/task-1.json
   ```

   两次都必须输出 `VALID <manifest-id>`。任一 `STALE` 立即停止。

3. reviewer 只读核对 proposal、delta spec、tasks、本计划、安装器契约、dry-run/实际安装输出、目标验证输出、用户文档哈希和目标顶层结构。
4. finding 使用 `.ai/rules/review.md` 固定字段记录；Critical/Important 未 resolved、not-an-issue 或用户 accepted-risk 时不得进入 Verify。

## 任务 5：Verify 双阶段独立审查

### 关注面 A：规格符合性

- 独立 reviewer 核对 delta spec 每条 Requirement/Scenario、任务清单、用户确认边界和全部验证证据。
- 重新执行或核对幂等 dry-run、目标 required 门禁、OpenSpec 严格校验、用户文档哈希、禁止项检查。

### 关注面 B：代码与操作质量

- 独立 reviewer 核对未手工零散复制、未绕过安装器事务、未扩大安装范围、失败路径可停止、源 worktree diff 只包含治理产物。
- 检查源侧 `proposal.md`、`tasks.md`、delta spec、`design.md` 与本计划无占位符、无互相矛盾状态、无计划外目标写入。

### 门禁

- 两个关注面均需独立 manifest verify 前后有效。
- Critical/Important finding 全部处置后方可进入 Archive。

## 任务 6：源侧收尾与归档前置验证

### 步骤

1. 汇总 finding、未验证范围与残余风险到 proposal 或独立审查台账，并持久化最终 manifest ID 与 comparison base。
2. proposal 状态置为`待验证`，Verify 全部通过后置为`待归档`。
3. 运行源侧验证：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital
   /home/yoyoo/.nvm/versions/node/v20.19.4/bin/openspec validate --all --strict --no-interactive
   /usr/bin/bash scripts/validate-workflow.sh --require-openspec
   ```

4. 运行归档轻量门禁：

   ```bash
   cd /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_agent/.worktrees/install-codex-workflow-ai-hospital
   /usr/bin/bash scripts/validate-workflow.sh --archive-light
   ```

5. 若 Verify 后发生工作流可执行文件、助手入口、技能语义、契约测试或治理规格变化，改跑：

   ```bash
   /usr/bin/bash scripts/validate-workflow.sh --require-openspec
   ```

6. 不自动合并、推送或清理 worktree；整合与清理等待用户明确授权。

## 回滚与中断策略

- 写入前失败：目标保持原状，无需回滚。
- 安装器事务失败：依赖安装器自动回滚；报告是否回滚成功，不手工修补。
- 安装成功但验证失败：保留现场并停止；未经用户明确授权不删除 55 个已安装文件。
- 源侧 OpenSpec/worktree 变更通过 Git 分支隔离；未获授权不重置、不删除分支或 worktree。
