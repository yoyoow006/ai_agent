## ADDED Requirements

### Requirement: 仓库必须拥有可用 Git 基线

仓库 SHALL 拥有名为 `main` 的初始分支和至少一个本地提交，使 `git status`、分支切换、review manifest freeze 和后续变更提交可执行。

#### Scenario: 查询仓库状态

- **WHEN** 在仓库根目录运行 `git status --short --branch`
- **THEN** Git 识别当前分支为 `main`
- **AND** 未忽略文件不残留未提交状态

#### Scenario: 查询初始基线

- **WHEN** 用 `git rev-list --max-parents=0 HEAD` 查询根提交
- **THEN** Git 输出至少一个本地初始基线提交
- **AND** 初始化变更本身不添加 remote、不抓取、不推送
- **AND** 后续远程配置由独立授权变更管理

### Requirement: 本地工作区内容不得进入版本控制

根 `.gitignore` SHALL 忽略本地 review 数据、助手 SDD 草稿、worktree 挂载点、Python 缓存和 Claude 本地权限配置。

#### Scenario: 检查本地路径忽略规则

- **WHEN** 对 `.ai-local/probe`、`.codex/sdd/probe`、`.claude/sdd/probe`、`.worktrees/probe` 或 `__pycache__/probe.pyc` 运行 `git check-ignore`
- **THEN** 路径被根 `.gitignore` 匹配
- **AND** 这些路径不出现在普通 `git status --short` 中

### Requirement: OpenSpec 基线必须可校验

仓库 SHALL 保留 OpenSpec 的项目说明、artifact 约定、空基线目录和共享工作流主规格，同时不覆盖既有活跃变更。

#### Scenario: 运行本地工作流校验

- **WHEN** OpenSpec CLI 未安装时运行 `bash scripts/validate-workflow.sh`
- **THEN** OpenSpec 精确检查显式记录 SKIP
- **THEN** 仓库结构、忽略规则、必需测试和其他工作流检查通过
- **AND** 末尾汇总为 `FAIL=0`

#### Scenario: OpenSpec CLI 可用

- **WHEN** OpenSpec CLI 已安装时运行工作流 required 校验
- **THEN** OpenSpec 精确检查实际执行且不得 SKIP
- **AND** 末尾汇总为 `FAIL=0`
