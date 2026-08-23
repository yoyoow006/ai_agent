# Git 基线凭据卫生规范

## Purpose

约束仓库初始提交、知识库正文和本地 Git 历史中的凭据处理，防止敏感值通过 push、clone、pack 传输或备份扩散，并保留外部凭据轮换责任边界。

## Requirements

### Requirement: 知识库正文不得包含字面凭据

仓库 SHALL 不在 tracked 知识库正文中保存已确认的账号或密码字面值；必要安全提示 SHALL 使用脱敏占位符表达。

#### Scenario: 扫描当前知识库

- **WHEN** 用已确认的凭据形态模式扫描 `.ai/kb`
- **THEN** 当前工作树没有匹配
- **AND** 原有“不要外泄、不要复制到对话/提交/PR”的安全语义仍保留

### Requirement: 可达 Git 历史不得包含字面凭据

仓库 SHALL 使所有 reachable commit 的树中都不包含已确认的字面凭据；旧未净化提交 SHALL 不再被分支、tag 或 reflog 引用。

#### Scenario: 扫描全部可达历史

- **WHEN** 遍历 `git rev-list --all` 并在每个提交树中扫描 `.ai/kb`
- **THEN** 没有任何提交包含已确认的凭据形态
- **AND** `git fsck --full` 退出码为 0

### Requirement: 清理不得破坏工作流基线

历史重建 SHALL 保留净化后的当前项目文件、OpenSpec 状态、忽略规则和可执行入口；清理后 SHALL 通过 OpenSpec 与工作流校验。

#### Scenario: 复验仓库

- **WHEN** 历史重建和对象修剪完成
- **THEN** `openspec validate --all --no-interactive` 通过
- **AND** `bash scripts/validate-workflow.sh` 末尾 `FAIL=0`
- **AND** Git 分支仍为 `main` 且未配置 remote

### Requirement: 凭据轮换必须显式留给用户

系统 SHALL NOT 声称本地 Git 清理可证明凭据未泄露或已失效；若凭据可能在仓库外暴露，用户 SHALL 在对应外部系统自行轮换。

#### Scenario: 提示残余风险

- **WHEN** 本地历史清理完成
- **THEN** 汇报明确说明本地清理不替代外部轮换
- **AND** 不访问、修改或测试任何外部凭据提供方
