# Delta Spec: workflow-installer

## MODIFIED Requirements

### Requirement: 装后自检

安装脚本 SHALL 在复制完成后于目标路径运行 `./scripts/validate-workflow.sh --fast`（秒级 core 结构校验），全绿才算安装成功；有红项则报告并以非零退出码结束。完整契约套件与便携安装器套件 SHALL 保持为源仓 CI 职责（随包契约套件的目标模型为"单侧+profile"，双运行时目标内运行全量校验会有源仓专属用例不适用）。目标带有历史归档目录而缺少 `openspec/archive/README.md` 索引时，装后自检 SHALL 以精确的单一 `[FAIL] 归档索引与目录 1:1` 报告（不混入其他红项、不误报为安装损坏）；补齐索引行后复跑自检 SHALL 全绿。

#### Scenario: 安装完成即验证

- **WHEN** 资产复制完成
- **THEN** 目标项目 `./scripts/validate-workflow.sh --fast` 全绿（退出码 0），安装整体耗时为秒级

#### Scenario: 目标带历史归档缺索引

- **WHEN** 安装到 `openspec/archive/` 已有变更目录但从未建立 README 索引的目标
- **THEN** 装后自检报告恰好一个红项 `[FAIL] 归档索引与目录 1:1`，安装器以退出码 1 结束
- **AND** 在目标内补齐与目录 1:1 的索引行后复跑 `./scripts/validate-workflow.sh --fast` 全绿
