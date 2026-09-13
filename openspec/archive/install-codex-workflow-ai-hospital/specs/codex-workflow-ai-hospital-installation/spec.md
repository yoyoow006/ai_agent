# AI Hospital Codex 工作流安装增量

## ADDED Requirements

### Requirement: ai_hospital 必须获得可验证的 Codex 单侧工作流

系统 SHALL 通过既有离线 manifest 安装器把共享 AI 工作流安装到真实目标 `/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital`，并 SHALL 在写入前后保护目标中不属于安装清单的用户文件。

#### Scenario: 从当前空白工作流目标安装

- **WHEN** 目标没有 `AGENTS.md`、`.codex/`、`.ai/`、`openspec/`、`.claude/` 或 `CLAUDE.md`
- **AND** 安装器以真实目标路径和 `--assistant codex` 执行
- **THEN** 目标获得 55 个清单内工作流文件
- **AND** 目标不获得 `.claude/`、`CLAUDE.md`、`.git`、源仓库业务项目知识或源仓库 Git 历史

#### Scenario: 保护既有用户文档

- **WHEN** 目标存在 `docs/好实用合作协议I51.2.doc`
- **AND** 其写入前 SHA-256 为 `9a76ae560637818368ddbbaa298409747210a066c0c061224c257b798b25787f`
- **THEN** 安装和验证过程不读取、修改或删除该文档
- **AND** 写入后 SHA-256 保持不变

#### Scenario: 安装后完整验证

- **WHEN** Codex 工作流安装完成
- **THEN** 幂等 dry-run 显示 55 个清单资产均 unchanged
- **AND** 目标根目录 `bash scripts/validate-workflow.sh --require-openspec` 无 FAIL
- **AND** 目标根目录 `openspec validate --all --strict --no-interactive` 通过
- **AND** 目标根目录没有因安装产生的 `.git`、`.claude/` 或 `CLAUDE.md`
