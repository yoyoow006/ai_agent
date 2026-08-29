# Design(严格模式·待确认规范阶段的设计要点,细化实现计划见 Design 阶段 plan)

## 关键决策

1. **P1a 放 CI 而非本地 wrapper**:安装器套件 82 用例涉及事务安装与 fixture 复制,本地时长可观;放进 wrapper 会拉长每次 Verify/Archive(与 P2b 目标相反)。CI 独立步骤获得同等拦截力,本地终验清单中的手动条目同时废止。步骤与 validate 并列同一 job,顺序执行,失败语义一致。

2. **P1b 以 core 为唯一权威**:`--print-external-commands` 输出排序去重的命令清单,清单紧邻命令使用处维护;两份测试改为 subprocess 调 core 解析。目标侧资产已随包 core 与 test_validate_workflow.py,自包含成立(memory 2026-08-21 的随包自包含边界不被破坏——test_install_ai_workflow.py 不随包,只在源仓消费 core 清单)。红测先行:先在 core 清单中临时移除 `cat` 断言受限 PATH 用例失败,再恢复(沿用 CQ-1 探针手法)。

3. **P2a 钩子自愿启用**:pre-push 直接 exec core(秒级);通过 `git config core.hooksPath scripts/hooks` 启用,不写 .git/hooks(克隆不携带、不越权)。钩子不进 manifest——安装目标的推送防护由目标维护者自定。README"本地防护"一节给出启用命令与失效条件。

4. **P2b 分层语义**:默认行为零变化,`--fast` 仅是新增旁路;分层规则写死三点(标准 Verify fast、标准 Archive 全量、严格恒 required),并加"治理资产变更的标准变更 Verify 也全量"守卫,防止改技能却只跑秒级校验。mutation 断言既有短语(如 `--require-openspec`、`bash scripts/validate-workflow.sh`)全部保留,新增短语同时更新双侧技能与资产副本。

5. **P2d best-effort 锁**:`command -v flock` 存在则对 `.ai-local/.validate.lock` 取非阻塞排他锁,第二实例 exit 2;不存在则提示降级。锁文件在已忽略目录,不污染工作树。CI/无 flock 环境自动降级,不引入新硬依赖。

6. **P3d 一行仲裁**:入口文档各加一句,资产通用入口同步;不枚举插件名(宿主环境各异),以"职责重叠即仓库优先"表述,避免维护名单。

7. **archive 技能补索引步骤**:上一变更建立的 `openspec/archive/README.md` 索引需要维护入口;在 archive 技能"归档数据"步骤中加一行,双侧+资产同步。规格层面不新增 Requirement(低于规格粒度,由技能正文承载)。

## 替代方案

- **安装器套件纳入 wrapper**:本地门禁时长翻倍,与 P2b 矛盾,否决。
- **白名单独立 JSON 文件**:多一个随包文件与解析层;core 即命令使用处,单一来源更彻底,否决 JSON。
- **分支保护/required check 替代钩子**:需服务端配置,超出仓库文件可达范围;钩子+CI 双层在可达范围内等价覆盖,服务端保护另行建议。
- **强锁(缺 flock 即失败)**:安装目标环境多样,硬依赖 util-linux 会破坏可移植性,best-effort 降级更稳妥。

## 风险与边界

- **mutation 断言脆弱**:改技能正文必须保短语;计划中每步技能编辑后立即跑 core+单测,合同套件在终验全量跑。
- **资产漂移**:所有随包文件(core/wrapper/两技能/两入口/pressure 场景)逐字节同步;安装器套件含资产逐字比较用例,会兜底。
- **CI 时长**:安装器套件时长未知(估 2-5 分钟),CI 总时长可接受;若超长再议拆 job。
- **范围外**:不动安装器事务逻辑;不删 workflow-system 旧规格(另行变更);不做压力场景 CI 行为重放(P3c,已建议不做);不加 memory 模块归属机械校验(候选,另行)。
- **整合策略**:严格默认隔离 worktree;归档后 `--no-ff` 合回 main、合并结果复跑全量、推送。
