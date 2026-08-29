## 2026-08-16 · 来源变更 init-workflow-system
**坑**：仓库目录属主为 root 时 git 报 "dubious ownership" 拒绝操作
**解**：git config --global --add safe.directory <仓库路径>；注意这是机器级配置，换机器要重配

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：本机 git 版本旧，git init -b main 不被支持（exit 129）
**解**：git init 后用 git checkout -b main 兼容；写脚本时避免依赖新 git 特性

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：git 不跟踪空目录，openspec/specs、archive、.claude/skills 等骨架目录在 fresh clone 上消失，结构校验假红
**解**：空骨架目录放 .gitkeep 入库；终审发现的计划缺口，已修复

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：本机 core.fileMode=false 掩盖了脚本以 100644 提交的问题，fresh clone 无执行位
**解**：git update-index --chmod=+x <脚本> 直接改索引模式；校验含执行依赖的文件时留意 fileMode 配置

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：verify 阶段审查通过后未回写 proposal 状态字段（构建中→待验证→待归档两跳均漏），归档时才发现状态滞后
**解**：verify 技能后续版本应把状态回写列为显式收尾步；归档开工前先核对 状态: 待归档

## 2026-08-17 · 来源变更 ignore-root-project-paths
**坑**：多步 shell 命令中的 `patch` 因上下文错字失败后，后续暂存与提交仍会继续，可能把未更新的任务真源提交出去。
**解**：补丁必须使用 `--fuzz=0 --no-backup-if-mismatch` 并立即核对目标文件；新增文件还须核对 hunk 行数、`wc -l` 与文件尾部，避免尾行被截断。包含提交的多步命令应启用失败即停，提交前再次扫描 tasks 未勾选项。

## 2026-08-18 · 来源变更 streamline-risk-tiered-ai-workflow
**坑**：GNU `patch` 在部分 hunk 失败时默认生成 `.orig`，宽泛执行 `git add openspec/` 会把备份误提交；仅看 patch 退出输出不足以保证索引干净。
**解**：调用 `patch` 时始终加 `--fuzz=0 --no-backup-if-mismatch`；提交前用 `git status --short` 与 `rg --files -g '*.orig' -g '*.rej'` 扫描备份和拒绝文件，宽泛暂存后还要用 `git diff --cached --name-status` 复核清单。

## 2026-08-18 · 来源变更 streamline-risk-tiered-ai-workflow（SDD 忽略）
**坑**：`.codex/README.md` 声明 `.codex/sdd/` 是 Git 忽略的本地草稿区，但 `.gitignore` 没有对应规则，压力测试逐字报告会作为未跟踪文件出现并可能被误提交。
**解**：用根锚定规则 `/.codex/sdd/` 忽略整块 SDD 工作区；生成报告后必须运行 `git check-ignore -v <报告>`，结构校验也应断言该目录确实被忽略。

## 2026-08-18 · 来源变更 streamline-risk-tiered-ai-workflow（patch reject）
**坑**：`patch --no-backup-if-mismatch` 只阻止备份，不阻止失败 hunk 生成 `.rej`；把多个手写 hunk 放在同一补丁中时，一个畸形 hunk还会让应用范围难以判断。
**解**：优先用 `apply_patch` 生成完整替换文件；必须用 GNU patch 时每个 hunk 单独成补丁、加`--fuzz=0 --no-backup-if-mismatch`并用失败即停串行执行。失败后立即核对目标 diff并扫描/删除本轮 `.rej`，不得继续提交。

## 2026-08-19 · 来源变更 adopt-shared-ai-workflow-infrastructure（合并 Claude 风险路由记录）
**坑**：把所有变更统一套入完整五阶段，会让纯文档维护产生四件套、独立计划、重复确认和多层审查；按文件后缀直接判低风险又会放过安全规范和工作流治理变更。
**解**：按实际影响选择快速/标准/严格；未知至少升级到标准，治理、权限、资金、迁移、Schema、并发和公开契约保持严格。

## 2026-08-19 · 来源变更 adopt-shared-ai-workflow-infrastructure（合并 Claude 状态校验记录）
**坑**：只检查`状态:`存在会放过非法值和模式—状态错配；只检查正向关键词会让旧统一重流程悄悄回流。
**解**：校验合法模式—状态组合，并用 mutation tests 分别向入口和阶段技能注入文档四件套、标准独立计划和标准双审规则，要求校验返回非零。

## 2026-08-19 · 来源变更 adopt-shared-ai-workflow-infrastructure（合并 Claude worktree 记录）
**坑**：先在当前工作区检出 feature，再直接执行 `git worktree add` 会因分支已被检出而失败；标准模式若只写“默认 feature”而无执行步骤，可能在 main 实现。
**解**：先只提交流程产物到 feature；需要 worktree 时切回基线，再挂载未检出的既有 feature。所有实现前显式核对当前分支。

## 2026-08-19 · 来源变更 adopt-shared-ai-workflow-infrastructure（补丁多余空行）
**坑**：手写补丁新增或替换文件时，hunk 行数与上下文中的空行不一致会悄悄引入额外空白行，内容看似正确但格式校验失败。
**解**：应用补丁后立即检查目标段落边界，运行尾随空白扫描和 `git diff --check`；不要仅凭补丁成功输出判断格式正确。

## 2026-08-26 · 来源变更 improve-open-requirement-discovery（压力场景权威事实）
**坑**：压力场景假设仓库已有订单搜索实现，但项目 registry 为空且 tracked 搜索没有业务目标；把 ignored SDD 夹具当作仓库事实会制造假绿色前提。
**解**：压力场景必须与 registry/tracked 权威事实一致。真实无目标时应先引用边界并询问外部既有代码、新建/登记还是仅示例；用户下一轮给出已检出目标后，再自行核对实现、路由、测试和文档。用户明示输入可作为证据来源，但不得伪造成路径。


## 2026-08-20 · 来源变更 adopt-shared-ai-workflow-infrastructure（OpenSpec strict）
**坑**：required 校验只证明 CLI 与非严格 validate 已执行；CLI 长期缺失还会掩盖既有主规格 Purpose 过短等 strict 警告，直到严格终验才集中失败。
**解**：严格 Verify/Archive 同时现跑 required 门禁与 `openspec validate --all --strict --no-interactive`；Purpose 补充必须由既有 Requirements 支撑。需要本地 CLI 时安装到已忽略的 `.ai-local` 并临时扩展 `PATH`，不要运行会重写工作流的 init/update。

## 2026-08-20 · 来源变更 adopt-shared-ai-workflow-infrastructure（脏主树终验）
**坑**：顶层契约测试用 `shutil.copytree` 复制仓库 fixture；在主工作区存在被忽略的外部项目符号链接时会跟随链接复制业务仓，导致 required 终验异常缓慢并越过预期验证范围。
**解**：脏主树合并后不要移动用户目录来加速；以 main 当前提交创建临时 detached worktree，在干净 Git tree 中通过项目内 OpenSpec PATH 现跑 required 与 strict，验证后仅移除该临时 worktree。后续应让 fixture 明确排除 ignored/外部符号链接。

## 2026-08-23 · 来源变更 sanitize-git-baseline-secrets
**坑**：先把包含知识库正文的工作树写入 Git root commit，再执行敏感内容审查，会把字面凭据固化到对象历史；此后仅修改当前文件无法阻止 clone、push 或备份恢复旧值。
**解**：创建或重置 Git root 前先扫描待入库内容；若提交后才发现凭据，在无 remote 且获得明确授权时同时净化当前树、重建 root、删除旧引用、 expire reflog 并 prune 不可达对象。本地清理不能替代外部凭据轮换。

## 2026-08-23 · 来源变更 add-test-login-project
**坑**：严格模式运行时行为把测试与实现放进同一提交后，审查者无法从 Git 历史独立复现 TDD 红阶段；隔离 worktree 还不会自动 materialize 被忽略的 SDD 占位目录。
**解**：运行时实现先提交 test-only 状态或保留可复核的临时红输出，再提交实现；隔离 worktree 需按本地忽略规则补齐 SDD 占位目录后运行完整门禁。安全契约测试应覆盖实际算法、随机源、默认参数和错误路径，而不只断言内部结果非空。

## 2026-08-23 · 来源变更 add-origin-remote
**坑**：标准 Verify 阶段的 OpenSpec 四件套尚未提交时，把 `git status` 笼统断言为 clean 会与实际未跟踪流程产物冲突。
**解**：远程或本地配置类变更应精确断言分支、tracked/staged 差异和允许的未跟踪流程文件清单；添加 remote 只写 `.git/config`，fetch、pull、push 仍必须另行授权。

## 2026-08-26 · 来源变更 initialize-git-repository（历史基线归档）
**坑**：归档长期停留的初始化变更时，实施时的初始提交哈希与“无 remote”状态可能已被后续授权的历史净化和远程配置变更取代；直接照搬旧证据会与现行主规格冲突。
**解**：用当前 parentless root、clean 状态和 ignore/OpenSpec 基线重新验收；delta 明确“初始化本身不添加 remote/不推送”与后续独立授权远程配置的边界，并记录旧证据到新历史的演进关系。归档前必须先提交审查产生的 OpenSpec 修正并复跑 required 门禁。

## 2026-08-27 · 来源变更 add-cancel-state-ci-mirror（基线修复）
**坑**：`validate-workflow-core.sh` 用 `test -d .codex/sdd` 断言目录存在，但 `/.codex/sdd/` 被 gitignore 忽略且 `.gitkeep` 从未提交；主工作区靠磁盘遗留空目录通过，新鲜 worktree/clone/CI 检出中该检查失败，并级联击垮依赖实体树拷贝的 38 个契约 fixture 测试。
**解**：用 `git add -f` 跟踪 `.codex/sdd/.gitkeep` 与 `.claude/sdd/.gitkeep`（与安装资产 manifest 既有条目一致）；占位符被跟踪后 SDD 草稿正文仍被忽略。新增「目录存在」类断言时，必须保证其占位符能被新鲜检出处物化。

## 2026-08-27 · 来源变更 add-cancel-state-ci-mirror（沙箱白名单）
**坑**：validate-workflow-core.sh 的 mirror_equal 改用 `| cat -s` 后，契约测试沙箱的 PATH 白名单（test_validate_workflow.py 的 VALIDATOR_COMMANDS）不含 cat：管道失败、重定向先建空临时文件、cmp 比较两个空文件相等——沙箱内全部镜像检查空转假绿；真实 PATH 下一切正常，假绿仅出现在契约沙箱。
**解**：core 新增任何外部命令（cat、sort、tr 等）必须同步 VALIDATOR_COMMANDS 白名单并重跑契约套件；保真度可用「白名单独占 PATH + 注入技能漂移」探针验证镜像检查非零。

## 2026-08-28 · 来源变更 add-cancel-state-ci-mirror（整合修复）
**坑**：`openspec/changes/.gitkeep` 从未被跟踪（archive/plan/specs 三个都有，唯独 changes 漏了）；主工作区与实现 worktree 靠磁盘残留目录通过「目录存在」断言，`--no-ff` 合并后 git 清除无跟踪文件目录，主分支校验 FAIL=2（目录断言＋契约 fixture 级联），新鲜 clone/CI 同样会挂。
**解**：补提交 `openspec/changes/.gitkeep` 并复跑 required 门禁。教训：「目录存在」类断言的每个目录都必须有已跟踪占位符；审计 diff 时勿用 head 截断输出（本次与资产规格滞后同为截断漏报）。

## 2026-08-29 · 来源变更 fix-merged-legacy-ai-kb-regression（审计发现）
**坑**：手工合并 `Merge remote-tracking branch 'origin/main'`（45e8ed1）把本地线迁移前的 `.claude|codex/ai-kb/{kb,rules,memory}` 平行正文带回 main 并推送；core `旧 ai-kb 不含平行正文` FAIL，契约套件因 fixture 忠实复制现行文件而级联 40/82 假设绿基线的失败。另：两个 validate-workflow 实例并发时 mutation 测试互踩，会产生大额度假失败；契约套件单跑约 5 分钟，120 秒 timeout 不足以作终验证据。
**解**：合并到 main 属于治理边界，必须走 Archive 确认的整合策略并在推送前本地现跑完整门禁（--no-ff 合并后同样）。诊断契约套件失败先看是否单一根因级联（一个 core FAIL 可放大为几十个 contract 失败）；校验器只能串行单实例运行，长跑用后台任务而非加 timeout。删除复活旧正文前必须**逐侧计数**核对 memory 条目是否已迁移——双侧同名文件不必然同内容，本次 codex 侧比 claude 侧多 3 条独有条目（`grep -c '^## '` 逐文件计数），合计 10 条 2026-08-16 条目未迁移；首轮只迁 claude 侧 7 条即删构成知识丢失，由独立审查 VQ-C01 纠正后补迁。
