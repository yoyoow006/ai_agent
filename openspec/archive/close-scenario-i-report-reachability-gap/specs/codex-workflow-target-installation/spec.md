# Delta Spec: 闭合场景 I 上报规则可达性缺口

## MODIFIED Requirements

### Requirement: 冲突入口必须先保留再替换

当目标 `AGENTS.md` 与安装清单内容不同时，系统 SHALL 在调用安装器前将其重命名为明确的备份路径，并验证备份内容与重命名前一致；系统 SHALL NOT 覆盖、合并或丢弃旧入口内容。冲突的发现与上报 SHALL 仅按事实要素：入口路径、与安装清单内容的差异结论、既有文件 SHA-256；系统 SHALL NOT 向对话输出既有入口正文，正文比对由维护者经由备份文件或临时空目录生成的模板自行完成。为校验备份而进行的内部哈希计算不属向对话输出。

#### Scenario: 目标已有差异 AGENTS.md

- **WHEN** 目标 `AGENTS.md` SHA-256 为 `74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc`
- **THEN** 系统先将其重命名为 `AGENTS.pre-codex-workflow.md`
- **AND** 备份 SHA-256 保持不变
- **AND** 新 `AGENTS.md` 只能由安装器从显式清单创建

#### Scenario: 用户索取冲突正文

- **WHEN** 用户要求把冲突的既有 `AGENTS.md` 正文打印到对话以确认
- **THEN** 系统按事实要素上报（路径、与清单内容的差异结论、SHA-256）
- **AND** 说明正文可经由备份文件或临时空目录生成的模板由维护者自行比对
- **AND** 不向对话输出既有入口正文
