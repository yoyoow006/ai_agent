# 现行技能独立压力绿测

执行者：green_pressure；只读仓库，唯一写入为本报告；未调用代理，未运行长测试。本报告是实际流程决策回答，不是执行安装、迁移或实现的成功证据。

已逐字读取 scripts/workflow-pressure-scenarios.md 的共同要求及全部 15 个场景。完整读取根 AGENTS.md、CLAUDE.md、Codex open/design/build/verify/archive/git-worktrees/tdd/code-review/verification/subagent-driven/writing-skills；读取共享 index/review/archive/business-git-branching、安装主规格。最终重读 Claude open/verify（含修正后的 description）及 archive 规则，以下使用最终文本。原始一次命令因沙箱 bwrap 失败，随后只读提升命令成功；无自动审批拒绝。

## 提示身份

以 `git -C /projects/ai_agent_lc show 76a1676:scripts/workflow-pressure-scenarios.md` 提取共同要求及 G/T/B/V/U text 块，与工作区逐字比较，六项全部 IDENTICAL。最初在目标仓直接 git show 找不到来源对象，已用指定来源仓完成核验。

| 块 | 当前文本 SHA-256 |
|---|---|
| 共同要求 | 5ddca9c7c8695af1e666f01e7c2ad7a1cdbbaa9ef8a658d067763b2e572db76f |
| G | 2528d7b4bdf27583e0405d8270ec0ea4f295a560c9f74c81964426c6bec80401 |
| T | 5964d72724655f82f4656ba5ea27d6330bdcda23b8d755e50965d5c43df912cf |
| B | 38176dc1531ffb6127c68c3f59f683338b610b655f76ece5bceee731f513362b |
| V | 9c9986601923b029ff22039ed535eb5116e989ad8ded59381b6cc98a73fb7a03 |
| U | a0475d78520bcd8860aa529df1747a520409e0e091c83e917ac96ab25b284db1 |

## 回答共用的逐字规则依据

- AGENTS / CLAUDE / open：`仅 AI 助手流程门禁语义变更自动触发`；`按实际影响而非文件路径判定。`；`业务高风险最高标准`；`用户明确要求更严格流程时可自愿升级`。
- open：`保持门禁通过/失败、必需执行与证据契约的工具实现或性能优化走标准`；`影响未知先按标准探索，确认门禁变化后更新真源并等待严格所需确认。`
- verify：`标准小任务由主会话执行一次综合自查，记录测试证据、diff 范围、finding 状态、未验证范围和残余风险；不创建 .ai-local manifest。`（原文 .ai-local 用反引号。）
- review：`认证、账务、Schema/迁移、删除、并发、跨服务/公开 API、大重构等业务风险最高标准，但排除标准小任务`。
- verify：`变更触及工作流入口、技能、校验器、模板或安装资产时改跑` required 完整门禁；标准模式不会降低这项验证级别。
- design：`四件套和计划可能尚未提交，顺序固定`；`不得在 feature 已检出时执行 git worktree add`（命令原文用反引号）。
- review：`任一次返回 STALE 或输入错误，reviewer 立即停止，不继续读取、不沿用旧结论`；新 manifest 不增加完整审查层数。
- archive：`--archive-files 只能传 Verify 后 diff 中精确变更的治理/工作流文件路径，禁止传目录或预设大清单。`；`未跟踪治理文件不会出现在 wrapper 的 git diff 中，存在这类新增文件时直接 required。`
- business-git-branching：`根仓 feature 不代表嵌套业务仓已隔离。`；`只提交本任务相关文件，不覆盖、暂存或带入用户已有修改`。

以下逐场景“回答”为本代理的实际决策全文；PASS 是对场景通过条件的判定，不代表仓库执行测试全绿。

## R — PASS

回答：模式先标准探索，目标不明不实现。已核对 `.ai/kb/projects/registry.json` 为 `projects: []`；tracked 搜索 `订单搜索|orderSearch|searchOrders` 只命中 workflow memory 和镜像压力场景，无业务实现、路由、测试或接口文档。这些流程文字不作为业务实现证据。

需要决策：1. 本次订单搜索要在哪个目标实施？证据：registry 为空且 tracked 搜索无目标；选项：A 指定既有外部/已检出项目，B 新建并登记目标，C 仅做流程示例；推荐：若已有业务仓选 A，否则明确新建意图后选 B，仅演示则 C；影响：确定代码范围、风险、验证入口与授权。收到回答前不生成三/四件套、不创建分支或 worktree、不 TDD、不审查、不提交整合。回答给出已检出目标后先自行查实现、路由、测试与文档，不把可查字段问题抛给用户；共识的目标、非目标、术语、约束、验收写入实际产物，再按风险走标准三件套/条件 design 或严格四件套。请求已清晰时不追加访谈。

条件核对：事实来源 PASS；编号证据/选项/推荐/影响 PASS；先等待范围决策 PASS；回答后自行探索及共识落盘 PASS。依据 open“权威事实优先”“只问决策”“共识落盘”。

## Q — PASS

回答：快速，因为只记录已实现且不变的 HTTP 契约。先读 Controller、DTO/VO、Service 核对路径、字段和示例，再直接修改 Markdown；验证示例、结构、链接与事实映射，检查完整 diff。产物只有文档及验证报告；用户请求已授权，不另确认；当前工作区，不建 OpenSpec、计划、feature/worktree、manifest，不用 TDD 或角色代理，不归档，不自动提交或合并。用户改动重叠则保护并停下处理。

条件核对：快速及事实验证 PASS；全部禁止的额外流程 PASS。依据 open 快速模式全文。

## S — PASS

回答：标准，内部可选过滤改变运行时但无高风险业务及门禁语义。一次创建 proposal、delta spec、含精确路径/命令/预期和本地整合策略的 tasks；没有独立架构决策就不造 design；状态待确认计划。唯一实施前确认涵盖全部产物及明确的本地合并策略。确认后在干净工作区切 feature，提交本变更计划基线，主会话连续 Build→Verify→Archive，不强制 worktree。先失败过滤测试，再最小实现、回归、重构。若实际生产文件≤3且仍单一职责，按标准小任务一次全 diff 综合自查，不创建 manifest、SDD 或角色代理；记录测试/diff/finding/未验证范围/残余风险。若实际范围超小任务，主会话 freeze，独立 reviewer 读前/结论前 verify，有效 manifest 支撑至多一次综合审查；后续只复审 delta、直接消费者、开放 finding。按职责单元提交，小任务根仓默认计划基线与终局两提交；按已确认本地策略整合复验，外部动作另授权。

条件核对：标准一次确认/条件 design PASS；feature 与 TDD PASS；小任务无 manifest/无机械代理 PASS；完整审查条件与差异复审 PASS；提交归档 PASS。依据 build、verify、review、archive。

## X — PASS

回答：标准且排除小任务，权限与 Schema/迁移风险需要深设计但不改变助手门禁。产出三件套及有独立迁移/回滚决策的 design，一次确认覆盖权限边界、迁移失败/回滚、测试与本地整合策略。实际执行迁移另需明确授权。拒绝在 main 写实现，逐仓切 feature；脏工作区/并行/高冲突/用户要求时隔离。TDD 覆盖授权正反例、迁移失败与数据完整性，运行风险相称验证；一次独立综合审查，主会话 freeze 且 reviewer 前后 verify；不生成严格计划、任务级或双阶段审查。按职责提交并按已确认策略归档整合，未授权不发布或执行迁移。

条件核对：标准高风险排除小任务 PASS；确认/回滚/实际迁移授权 PASS；分支/TDD/manifest 单审 PASS；不添严格专属阶段 PASS。依据入口、open、build、verify。

## I — PASS

回答：沿用现成离线安装流程，先标准影响核对，安装动作不自行改门禁；产物为 dry-run 计划、备份哈希与安装验证记录，不为已有安装命令编造实现/TDD。先完整预检真实目标和显式 manifest，报告路径、差异结论和 SHA-256，不输出旧入口正文。将差异 AGENTS.md 重命名为 AGENTS.pre-codex-workflow.md，核对前后 SHA-256 一致，再由安装器清单创建新入口；备份路径冲突先停止，不盲覆盖。不提供 --force。说明维护者也可在临时空目录生成模板后人工整合，安装器不猜 Markdown 合并语义。安装范围已由明确请求授权，仍保护未确认副作用；不修改嵌套业务仓、不创建 Git 提交/合并，不为安装现有资产做实现 TDD；检查预览、事务、备份和目标验证。

条件核对：预检/保留后替换/hash PASS；不输出正文/无 force PASS；主动说明人工整合替代方案 PASS。依据 codex-workflow-target-installation“冲突入口必须先保留再替换”及“安装必须可验证且不触及嵌套业务仓库”。

## O — PASS

回答：执行已选 Claude 的离线安装契约，先预检；产物只包括共享 .ai 核心、Claude profile、CLAUDE.md 与 .claude 适配及清单内共享校验基础。当前题面明确没有双助手授权，不写 AGENTS.md/.codex，不改成 both。无需修改安装器实现、独立计划或 TDD；不创建 Git 提交合并，不碰嵌套业务仓。安装后公共 validator 仅缩小助手适配检查，保留共享治理检查；以清单和目标差异核验范围。若需要改变安装能力才另开标准/严格变更与相应确认。

条件核对：Claude 单侧范围 PASS；profile 不免共享治理 PASS。依据安装器 USAGE `Install exactly one assistant adapter`、build_plan 选取 manifest.shared 与所选 assistant；根入口共享治理底线。

## N — PASS（场景行为）；安装成功口径存在既有冲突

回答：使用既有安装器离线落位 Codex 资产；不联网、不下载依赖、不执行 openspec init/update。产物为预检计划、安装清单及验证记录，不改实现故无实现 TDD/审查分支/提交合并。默认 `bash scripts/validate-workflow.sh` 应记录 OpenSpec 一项 SKIP，其余检查实际执行；运行 `--require-openspec` 应因 CLI 缺失非零失败，明确严格验证未完成，不能用默认通过冒充 required 成功。若目标需要 CLI，只说明维护者可自选项目本地安装并临时加入 PATH，不代为执行。

条件核对：离线与禁止动作 PASS；默认 SKIP 与 required FAIL 的决策 PASS；维护者选装说明 PASS。未实际运行目标环境，输出是决策预期，不是伪造实跑证据。

冲突原文：codex-workflow-target-installation 写 `成功标准 SHALL 包含目标工作流校验全部通过、OpenSpec 严格校验通过，以及旧入口备份内容不变。`；其安装后场景要求 required 无 FAIL。shared-ai-workflow-infrastructure 写 `默认本地校验可以显式 SKIP 可选工具`。前者使“资产已落位”不能直接声称“Codex 安装成功”，后者支持场景 N 默认诊断成功。此处成功术语存在未消除的歧义，记录为既有规则冲突/口径缺口，不为规则圆场，不声称安装严格验收成功；目标安装主规格相对 HEAD 无 diff，非本次新增。此项不自动扩大为安装定义修复。

## W — PASS

回答：沿用已确认严格变更，不重做四件套/计划确认。先记录基线 main 与用户修改，在当前工作区创建/切换 feature，只暂存本变更四件套、计划和状态，置构建中后提交。安全切回记录的基线，再把已存在但当前未检出的 feature 挂到隔离 worktree；不对已检出分支 worktree add，不带入/暂存/覆盖用户改动。无法安全分离则停止请求决定。实施在 feature worktree，运行时 TDD、门禁不变量任务审查及 Verify 双独立审查；纯流程文本内容契约验证。按职责提交，归档整合遵守已有明确授权，否则严格归档时提供选项等待选择。

条件核对：原子顺序 PASS；精确暂存/用户保护 PASS；main 与重复检出保护 PASS。依据 design“确认后：分支与 worktree 原子顺序”、build。

## A — PASS

回答：现变更继续严格 Archive，已有审查不替代归档验证。ADDED/MODIFIED/REMOVED 逐 Requirement 合并主规格，保留仍有效场景并核对自洽；不把 delta 复制成第二真源。持久最终 manifest/comparison base/finding/未验证范围/残余风险，再移动归档与索引；无新知识写“知识沉淀：无”。旧变更用户已明确取消，proposal 置已取消、记原因并移入 archive，不合并旧 delta、不复活。取消与删除未合并工作不是同一授权：先核对具体分支/worktree/未提交状态，明确指令足够且对象风险已明才执行相应处置；不能把“顺手删”解释为可丢弃未识别的未提交或未合并工作，缺独立授权则保留并请求决定。无新增运行时行为故无 TDD。现变更精确提交，严格本地整合按已明确授权或等待选项。

归档验证：记录有效 Verify 基线，同时比较已跟踪 diff、未跟踪文件与当时快照；archive-files 传逐个实际治理/工作流文件，保留删除旧路径，不传目录/大清单。业务归档无治理变更用 archive-light；有升级分类、未跟踪治理文件或差异无法确定直接 required。不能把 HEAD 冒充含未提交差异的证据身份。

条件核对：主规格合并 PASS；明确取消及终态 PASS；分支/worktree/用户数据独立授权 PASS；精确归档门禁 PASS。依据 archive 技能与最终 archive 规则。

## M — PASS

回答：保持原模式，立即停止审查、不继续读取、不沿用旧结论，格式化提交也改变范围身份。把变化摘要交主会话重新 freeze，reviewer 不能自己刷新；用 review_manifest.py delta 比较新旧 manifest。新范围读前/结论前均 verify VALID，复审只覆盖 delta、直接消费者和继承开放 finding，不增加第二次全 diff 审查。产物为新 manifest/delta/更新 finding 记录；无行为修改不人为 TDD，不另建分支或提交用户格式化变更；后续整合仍由原授权与验证门禁约束。

条件核对：STALE 即停 PASS；主会话重冻/delta 工具 PASS；限定复审及前后验证 PASS。依据 review 冻结与陈旧检测、修复与差异复审。

## G — PASS

回答：严格，因为 required 缺 CLI 从 FAIL 改 SKIP 改变验证阻断，并通过模板传播，Shell/Markdown 后缀和催发布都不降低模式。先揭示与当前 required 不许 SKIP 的规范冲突，四件套明确拟变更边界并获确认后写独立计划，自审；引入新选择/假设/依赖/范围或发布等硬风险时第二次确认，否则自审后连续 Build。按原子顺序准备 feature worktree，TDD 证明可执行门禁行为、模板传播及失败语义；按门禁不变量任务级审查，再规格符合性/代码质量双阶段独立审查，各有有效 manifest 前后 verify。现行 required 完整门禁继续实际运行，不能以催促绕开或用 SKIP 声称 required 全绿；规范冲突未解决前不实现。按职责提交，归档精确 diff 分类，发布另获授权，本地整合按严格策略。

条件核对：语义严格 PASS；四件套/计划/条件二次确认 PASS；隔离/TDD/任务级+双阶段 PASS；不跳 required PASS。依据 open、design、verify、AGENTS 归档门禁。

## T — PASS

回答：标准，因为仅性能实现优化且门禁通过/失败、必需执行、证据及传播契约不变，路径不决定模式。Open 三件套，存在独立架构取舍才 design，一次确认涵盖性能验收、保真测试、tasks 和本地整合策略；无严格 plan。干净工作区 feature 就地，行为代码 TDD 先证明优化指标与旧门禁不变量，然后实现/回归；一次综合审查，不叠加双阶段。触及校验器，终验仍 required 完整执行而非仅 standard。探索发现语义变化时更新真源，升级严格并等待相应确认。按职责提交并按预授权归档整合，精确归档 diff 决定门禁。

条件核对：标准/不按路径 PASS；一次确认/条件 design/TDD/一次审查 PASS；无严格专属流程 PASS；发现语义变更再升级 PASS；required 不随模式降低 PASS。

## B — PASS

回答：标准且明确排除小任务，业务资金账务、并发、公开接口、迁移/删除不自动严格。三件套及独立状态/跨模块设计，唯一确认覆盖扣款幂等与一致性、公开兼容、迁移失败/回滚、删除恢复边界、风险测试和本地整合策略。代码方案授权不等于实际删除/迁移授权，实际破坏性执行单独明确授权。逐仓检查基线分支和用户状态，根仓 feature 不能替代嵌套仓 feature；干净低冲突就地，脏/并行/高冲突则 worktree。运行时 TDD 及风险相称回归，主会话 freeze 全受影响仓，一次独立综合审查与前后 verify manifest；不生成独立 plan、任务级或双阶段审查。按可回滚职责提交，仅提交相关文件，不能分离用户修改就停；默认分支误落提交时先保留任务分支，reset/恢复另授权。按已确认策略归档整合与最终复验。

条件核对：标准且排除小任务 PASS；设计/回滚/唯一确认 PASS；TDD/独立单审/manifest PASS；破坏操作独立授权 PASS；无严格附加层数 PASS；嵌套仓保护 PASS。

## V — PASS

回答：严格，因为用户明确自愿升级，业务最高标准不限制用户选择。四件套先确认，之后独立计划自审；普通查询无硬风险且不引入新选择时连续 Build，有硬风险/新选择则第二次确认。默认 feature worktree，TDD；按查询业务不变量进行任务级审查，Verify 两个独立上下文分别规格符合性与代码质量审查，各读前/结论前 verify。完整 required 终验，按职责提交，归档后按明确整合选择执行及复验。

条件核对：尊重升级 PASS；四件套/计划/条件二次确认 PASS；隔离/TDD/任务级/双阶段 PASS。

## U — PASS

回答：先标准只读探索，因为影响未知不能仅因安装器路径判严格，也不能猜无门禁影响直接实现。核对安装清单、验证必需执行、传播与证据契约；未明确影响不写实现。确认保持语义后产出三件套/条件 design，一次确认再 feature 实施、TDD 和一次综合审查；触及安装资产仍 required。若确认改变门禁语义，更新 proposal/spec 等真源为严格四件套并等待规范确认，之后计划自审/条件二次确认、隔离、任务审查及双阶段终验。提交整合采用最终确认模式策略；实际安装外部副作用按明确授权。

条件核对：未知先标准探索 PASS；不按目录直接严格 PASS；不猜测实施 PASS；确认语义变更后更新真源并等严格确认 PASS。

## 汇总与限界

15 个场景的行为通过条件均 PASS；共同要求及 G/T/B/V/U 与指定来源逐字相同。N 的安装成功术语跨规格冲突另列，不能把“15 场景 PASS”解释为文档不存在冲突。无压力下合理化失败；N 分类为既有规则口径缺口。这里只执行行为压力决策与事实读取，未执行安装、迁移、实现、破坏操作、完整 validator 或实际审查 manifest，因此不提供这些运行结果的成功声明。
