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

## 2026-08-30 · 来源变更 harden-gate-coverage-and-tiers（exec 重定向持久化）
**坑**：bash 中 `exec 9>>file 2>/dev/null` 在 exec 无命令时，行内全部重定向（含 2>/dev/null）会**持久作用到当前 shell**，后续所有 >&2 输出被静默吞掉——锁冲突消息凭空消失、退出码却正常。
**解**：exec 行只保留要持久的 fd 重定向，临时静默用编组限定：`{ exec 9>>file; } 2>/dev/null`；改完必须现跑"锁冲突消息可见"的用例验证，不能只看退出码。

## 2026-08-30 · 来源变更 harden-gate-coverage-and-tiers（grep 前导连字符模式）
**坑**：core 的 contains_all 用 `grep -Fq "$term" "$file"`，断言短语以 `--` 开头（如 `--fast`）时被 grep 解析为长选项而报错，结构断言假红。
**解**：断言类 grep 一律 `grep -Fq -e "$term" -- "$file"`；新增以连字符开头的断言短语前先想到该坑。

## 2026-08-30 · 来源变更 harden-gate-coverage-and-tiers（套件运行期间提交）
**坑**：全量安装器套件运行约 20 分钟，期间任何提交都会让先后执行的用例读到不同树，产生"CONFLICT/失同步"类时序伪影失败（本变更踩两次）。
**解**：终验链（全量门禁+安装器套件）一旦启动，仓库零编辑；需要修复先停套件、改完重启。多轮修复期的中间套件结果只作参考，最终证据只认最终树上的一次完整现跑。

## 2026-08-30 · 来源变更 harden-gate-coverage-and-tiers（目标内与源仓的测试环境差异）
**坑**：同一份契约测试在源仓与安装目标内运行环境不同：目标受限 PATH 无 flock、无 .github、单助手只有一侧入口/技能——硬编码两侧路径或依赖 flock 的用例在目标内报 FileNotFoundError/假失败。
**解**：随包用例必须按环境自适应：文件存在性 continue、flock 缺失 skipTest（理由登记进目标侧白名单）、源仓特有断言以 install_ai_workflow.py 存在为源仓标志；目标侧 skip 断言用"已知理由集合"而非精确计数（类继承会放大同类 skip）。

## 2026-08-31 · 来源变更 harden-gate-honesty-and-coverage（校验器自扫描）
**坑**：新增"废弃工具名零残留"扫描覆盖 scripts/ai-workflow-assets 时，资产树里的校验器自身副本含 token 清单字面量——检查扫到自己必红（自引用）
**解**：扫描限定 --include='*.md'/'*.toml'（契约对象是指导正文非可执行源码），天然排除 .sh；新增内容扫描类检查先想"扫描器自己的源码在不在范围内"

## 2026-08-31 · 来源变更 harden-gate-honesty-and-coverage（shell 检查函数返回值）
**坑**：retired_tool_names_absent 以 for 循环内 grep -q 收尾，无命中时末条 grep 退出码 1 直接成为函数返回值——检查恒 FAIL，注入类测试照样绿（有命中也 return 1），只有干净环境用例才暴露
**解**：check 用的 shell 函数必须显式收尾 return 0；"注入必红"用例必须配"干净必绿"用例成对写，否则拦不住恒 FAIL 型假检查

## 2026-08-31 · 来源变更 harden-gate-honesty-and-coverage（随包用例不得假设源仓结构）
**坑**：test_rejects_archive_index_drift 初版直接读 fixture 的 openspec/archive/README.md——源仓有该文件，但安装目标按设计是空白基线（只有 .gitkeep），目标内套件 FileNotFoundError 连带 contract/public/required 三变体失败
**解**：随包契约用例对仓库结构的任何假设都要自包含构造（备份/恢复整个目录 + 合成受控状态），不依赖"源仓恰好有"；新增用例必须在安装器套件（目标环境）里过一遍才算绿

## 2026-08-31 · 来源变更 harden-gate-honesty-and-coverage（跳过理由白名单登记）
**坑**：新增条件 skipTest（"codex assistant is not present in this fixture"）在 claude-only 安装目标触发，被 test_install_ai_workflow 的 allowed_skip_reasons 白名单拦截（"出现新理由即失败"是防用例静默消失的守卫，设计如此）
**解**：随包套件每新增一个 skipTest 理由，必须同步登记进该白名单——这是显式登记机制而非障碍；子代理修此类失败时先看差异集是否恰为未登记理由

## 2026-09-01 · 来源变更 fix-installer-suite-pycache-self-contamination（终验套件编排）
**坑**：两个 20 分钟级安装器全量套件（带/不带 -B）并行跑，CPU 争抢使目标内 `bash scripts/validate-workflow.sh --require-openspec` 超过 `_run_target` 的 240s 超时——TimeoutExpired 假错误，单跑即绿
**解**：安装器全量套件只串行跑（双模式需求用命令链一次后台执行）；超时类失败先查是否资源争抢再查代码

## 2026-09-01 · 来源变更 fix-installer-suite-pycache-self-contamination（git 物质化重置权限）
**坑**：umask-002 机器上 git merge/checkout 重写工作树文件后，资产树可执行文件回到 0775（git 只跟踪执行位，写入按当前 umask）——昨天 chmod 过的规范权限被今天的 merge 冲掉，安装器套件 mode 断言再度失败
**解**：umask-002 检出环境在每次 merge/checkout 后、跑安装器套件前重跑权限规范化（dirs/files 644、两个可执行 755）；根治需测试放宽 group-write 位或统一 022 检出，属范围外环境事项

## 2026-09-01 · 来源变更 harden-gate-honesty-and-coverage（存量目标命中归档索引检查）
**坑**：新增"归档索引与目录 1:1"在存量安装目标上报 FAIL——目标里有历史归档目录但从未建 README 索引（旧技能版归档时无此步骤，安装器也不分发 README）；fresh 目标 vacuous PASS（套件已验证），但升级/重装到有历史归档的目标时装后自检 --fast 变红，用户易误判为安装损坏
**解**：属预期数据契约信号而非缺陷——一次性 back-fill README 索引（按各归档 proposal 的标题/模式生成行）即永久消除；安装器升级路径测试缺"legacy 归档无索引"用例（fresh-only 覆盖），补不补待用户裁定
