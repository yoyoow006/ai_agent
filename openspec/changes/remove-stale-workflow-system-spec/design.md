# Design

## 逐条承接映射(REMOVED 的 10 条 → 现行位置)

| 旧 Requirement | 现行承接 | 判定 |
|---|---|---|
| 五阶段工作流 | risk-tiered「工作流必须先按风险分流」+ 标准单确认/严格 8 态 | 已取代且矛盾,删 |
| 硬门禁 | risk-tiered 模式门禁 Q1/S1/G1–G4 | 已取代,删 |
| 状态真源与断点续传 | risk-tiered「状态真源」+ openspec/AGENTS.md 约定 + 取消路径 | 已取代,删 |
| 原生技能库(13 技能) | 技能树本身 + risk-tiered「Codex 与 Claude 必须一致」镜像要求 + core 技能存在性断言 | 枚举性描述,可由树推导且镜像/存在性已有强制,删 |
| ai-kb 知识库 | shared-ai-workflow「唯一共享真源」+「memory 按模块」+ 校验器禁平行正文 | 已取代且直接矛盾,删 |
| TDD 硬规则 | risk-tiered「TDD 按风险启用」(仅运行时行为;文档用内容校验) | 已取代且矛盾(旧文无条件强制),删 |
| 两阶段审查 | risk-tiered 分层审查(标准单审/严格双阶段)+ shared-infra finding 台账 | 已取代且矛盾,删 |
| 归档六步 | archive 技能(双侧)+ risk-tiered 取消/整合路径 + 索引行步骤 | 已取代,删 |
| openspec CLI 兼容 | openspec/AGENTS.md 工件约定 + shared-infra required 门禁(CLI 缺失语义:默认 SKIP 提示/严格非零) | 语义已覆盖,删 |
| 零插件依赖 | risk-tiered「仓库技能优先于宿主插件技能」+ 安装器随包自包含契约(portable-installer 规格) | 精神由"仓库优先+插件仅补空缺"与自包含安装承接;绝对化表述与现实(宿主插件存在)不符,删 |

结论:无一条含未被承接的活要求;三条与现行正面矛盾。

## 关键决策

1. **整能力 REMOVED 而非改写**:改写成"现行系统描述"会与 risk-tiered/shared-infra 形成第三份重叠正文,加重镜像维护;治理正文单一真源原则优先。
2. **归档时删除规格文件与目录**:REMOVED 全部 Requirement 后保留空壳目录只会复活"目录存在类断言"问题;openspec/AGENTS.md 的目录约定以 .gitkeep 维持的四个目录(changes/plan/specs/archive)不含能力子目录。
3. **不动任何代码/技能/入口**:本变更纯规格层;core、契约套件、资产 manifest 零触碰(全仓 grep 证实零引用)。

## 替代方案

- **保留但加"已废弃"横幅**:制造一个读者需要每次解释的僵尸文件,否决。
- **改写为现行系统总述**:与两份现行规格重叠,违反单一真源,否决。
- **只删矛盾三条保留七条**:剩余七条全部已被承接,保留即冗余,否决。

## 风险与边界

- **误删活要求**:以逐条映射表 + 独立双阶段审查核对;openspec validate --strict 在删除后复跑。
- **历史考古**:旧正文在 git 历史(45e8ed1 及更早)与归档 delta 双重可查。
- **范围外**:不清理 memory 中"来源变更 init-workflow-system"字样(历史事实);不动 workflow-installer 等其他规格;不做 memory 模块归属机械校验(独立候选)。
