# 工作流优化

## Requirements

### Requirement: 静态规则缓存必须内容寻址且 fail-closed

系统 SHALL 为静态规则/技能/共享规范解析提供带 schema、实现版本、输入清单哈希、生成时间和 PASS 结果的缓存；仅在所有身份字段和输入指纹一致时复用。缓存缺失、损坏、非 PASS、输入/命令/schema/实现变化或读取异常 SHALL 视为未命中并实际执行，缓存不得改变顶层 PASS/FAIL/SKIP 语义。

#### Scenario: 静态规则暖缓存命中

- **WHEN** fast 层的规则输入、解析命令、校验实现和 schema 与最近一次实际 PASS 完全一致
- **THEN** 输出该检查为 PASS，并标注缓存指纹、实际执行时间和沿用来源
- **AND** 不增加第四种检查状态

#### Scenario: 静态规则缓存失效

- **WHEN** 任一规则文件、技能文件、命令、实现版本或 schema 发生变化，或缓存记录不可解析
- **THEN** 系统重新执行检查并按新结果更新或清除缓存
- **AND** 不得使用旧结果声称通过

#### Scenario: required 层绕过缓存

- **WHEN** 执行 `bash scripts/validate-workflow.sh --require-openspec`
- **THEN** 静态规则检查实际执行
- **AND** 不读取或写入规则缓存

### Requirement: 验证层级必须显式、可升级且兼容既有入口

系统 SHALL 明确 fast、standard、required 三层的检查覆盖、缓存规则、允许跳过项和退出语义；现有 `--fast`、默认全量和 `--require-openspec` 入口 SHALL 保持兼容。触及工作流入口、技能、校验器、模板或安装资产的变更 SHALL 自动升级到 required 或输出明确升级提示。

#### Scenario: 标准层执行

- **WHEN** 维护者执行标准验证入口
- **THEN** 运行 core 与变更相关目标/回归测试，并逐项输出 PASS/FAIL/SKIP、层级和退出结果
- **AND** 仅允许契约明确的可选工具 SKIP

#### Scenario: 变更触发升级

- **WHEN** 变更文件命中工作流入口、技能、校验器、模板或安装资产
- **THEN** 验证入口升级到 required 或返回可判定的升级要求
- **AND** 不得仅依赖 fast 缓存完成终验

#### Scenario: 层级参数冲突

- **WHEN** 同时传入语义冲突的层级参数
- **THEN** 命令以退出码 2 失败并说明冲突
- **AND** 不执行部分门禁造成假绿

### Requirement: 标准 OpenSpec 产物必须由统一模板约束

系统 SHALL 提供 proposal、delta spec、tasks 的标准模板，并在存在独立设计决策时提供 design 模板。模板或生成预检 SHALL 要求模式/状态、Why/What/Impact、范围与非范围、至少一个 WHEN/THEN 场景、精确验证命令、预期结果、本地整合策略和未验证范围/残余风险槽位；未替换占位符、空场景、多行命令或缺失必需字段 SHALL 失败。

#### Scenario: 生成标准产物

- **WHEN** 维护者在空目标目录以变更名和模式调用生成入口
- **THEN** 创建三件套及可选 design 模板，文件包含统一字段和可执行占位槽位
- **AND** 不创建分支、提交、worktree 或修改目录外文件

#### Scenario: 模板预检拒绝不完整产物

- **WHEN** 任一产物缺少必需字段、WHEN/THEN 场景、验证命令、本地整合策略或仍含占位符
- **THEN** 预检返回非零并指出文件与缺失项

#### Scenario: 模板语义与双助手一致

- **WHEN** 对 Codex、Claude 入口和随包资产执行镜像/结构校验
- **THEN** 三件套字段、验证层级和缓存禁止项语义一致
- **AND** 仅允许登记的适配差异
