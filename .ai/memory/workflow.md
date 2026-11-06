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
**解**：属预期数据契约信号而非缺陷——一次性 back-fill README 索引（按各归档 proposal 的标题/模式生成行）即永久消除；已加回归用例锁定（add-installer-legacy-archive-selfcheck-test，2026-09-01 归档）：精确单一 [FAIL] 信号 + back-fill 后复跑 --fast 转绿，双断言入 LegacyLayoutTests
## 2026-09-02 · 来源变更 harmonize-scenario-i-codex-target（场景 I 调和的可达性与守卫边界）
**坑**：①「不输出既有正文」条款只存在于行为契约文件、不在任何决策链文档（CLAUDE/AGENTS/技能/.ai rules/规格全量 grep 零命中）——绿测探针未读契约文件时该规则不可达，双样本 1 过 1 挂，归类规则缺失非压力合理化；②场景 I ⑥「仍是替代方案」为描述性措辞，严格/宽松两种读法判定相反（样本 B ⑥ 双读法自证）；③「I 压力契约」锚串互钉是单向机械：锚串只读场景文件，规格侧单改备份路径门禁不红，仅靠主规格「任一侧修改冲突处置语义 SHALL 独立变更同步」条款在 Verify 流程拦截
**解**：①②按用户裁定路由另立独立变更（届时重审 ④ 是否应为硬条款、⑥ 改行为动词措辞）；③规格侧改动后 Verify 必须人工对照场景 I 条款，不可依赖门禁绿；本变更已重跑记录在 openspec/archive/harmonize-scenario-i-codex-target/scenario-rerun.md
## 2026-09-02 · 来源变更 close-scenario-i-report-reachability-gap（决策链可达性闭合先例＋审查排程序验）
**坑**：①行为契约（压力场景通过条件）里独有的规则对探针不可达——只读根入口＋技能的会话永远看不到，「不输出既有正文」双样本 1 过 1 挂即此；②可达性修复若落在规格 delta 里，验收探针在归档合并前读不到——重跑必须后置到主规格合并之后；③review_manifest 冻结记录文件权限位字段：freeze 之后做 umask 归一 chmod（664→644）会使 manifest STALE，reviewer 在结论前正确停止
**解**：①规则要可达就写进决策链路由终点（本例 codex-target 规格冲突条款，探针路由终点已实证），不要只放契约文件；②可达性验收探针在归档合并态跑，记录追加归档目录独立提交，FAIL 时回退归档状态重走；③**模式归一必须在 freeze 之前**（新 worktree 建好先 chmod 再冻结审查范围）；判定口径类条款必须行为化（动词领起）并写明缺省判法（未提及＝FAIL），否则严格/宽松双读法重现
## 2026-09-02 · 来源变更 validator-fail-closed-backport（bash≤4.3 set -u 空数组致命中止＋移植回归实证法）
**坑**：`set -u` 下 bash ≤4.3 把空数组展开 `"${a[@]}"` 当未绑定变量直接中止（rc=127，bash 4.4 才修复）；从 meta 库回流 `archive_index_ok` 时两个 `for path in "${arr[@]}"` 在空归档/仅 README 归档（恰是安装目标空白基线）会让整个 core 在 `check` 的静默重定向下中途崩死——无 FAIL 行、无 INTERNAL_RESULT，方向 fail-closed 不假绿但 macOS /bin/bash 3.2 目标整体不可用，且测试宿主 /usr/bin/bash 5.1 结构性无法捕获。
**解**：空数组循环一律用仓库既有习语 `${arr[@]+"${arr[@]}"}`（wrapper 早有同款）；验证用 ftp.gnu.org 源码自编译 bash 3.2.0 驱动真实函数三态（空/仅 README/有目录）+ `git archive` 导出骨架端到端核对 INTERNAL_RESULT 出现；**回流移植即使逐字来自已过门禁的上游，仍须按本仓声明的兼容下限独立实证**——meta 库原件至今仍带此潜伏缺陷（其宿主 bash 5.x 永不触发），下次升级目标侧时应一并修复。
## 2026-09-08 · 来源变更 streamline-ai-workflow-overhead
**坑**：本仓库主工作区 `.git`、`/codex`、`/agents` 是 ro 挂载，`.worktrees/`、`/ai/`、`/scripts/`、`/openspec/` 是 rw；这导致严格模式 plan 中"git checkout -b → commit → worktree add → 本地合回 master"在 ro `.git` 下物理不可行，5 SKILL.md 同步任务（plan 任务 2）也因 `.codex` ro 全部阻塞。
**解**：(1) 在 rw 路径上完成"能落盘"的任务（AGENTS.md、review.md、wrapper、tests）并各自跑 plan 自带验证；(2) 对 ro 路径加 skipTest 注记"environment: path is read-only in current mount"，让契约套件保留红灯位作为 finding、不污染主套件绿；(3) `task 7/8`（worktree + commit + 合回 master）作为后续在可写环境（用户开发机或外部克隆）执行的"半成品"，本次不进 goal。(4) 落地后用 tasks.md 显式标 `[x]`/`[BLOCKED-ENV]`/`[PHYSICAL-IMPOSSIBLE]`，与 plan 字段一一对应、可在用户环境回溯。
## 2026-09-08 · 来源变更 streamline-ai-workflow-overhead（标准三件套条件生成）
**坑**：标准模式无差别强制四件套（含 design.md + 独立 plan）会让"补一个字段映射"这种职责清晰的小变更承担架构决策、第二次确认、独立 plan 三重成本；用户体感是 OpenSpec 永远重型化，违反风险分级初衷。
**解**：标准 design 改为"跨模块取舍 / 新依赖 / 状态模型 / 重要替代方案 / 架构决策无法在 proposal/tasks 清晰表达"五项正向触发；其余情况只产 proposal + delta spec + tasks，禁止空壳 design；同步 5 SKILL.md 双套镜像并跑 `mirror_equal` byte-identical 验证。AGENTS.md / open SKILL.md 措辞必须显式"不得制造空壳 design"。
## 2026-09-08 · 来源变更 streamline-ai-workflow-overhead（严格风险触发二次确认）
**坑**：严格模式无差别要求四件套确认后第二次确认独立计划，会让"治理规则文档化（不动业务运行时代码 / 数据 / Schema）"这种工作也吃 plan 确认成本；治理语义变化的 plan 风险与"按已确认规范展开"的风险本不在同一量级。
**解**：第二次确认改为不可逆风险硬触发（权限认证、资金账务、数据库 Schema/迁移、数据删除、破坏性动作、外部副作用，或计划引入规范未覆盖的选择/假设/依赖/范围）；硬集合显式列出关键词；未命中且未引入新选择时 plan 自审后连续 Build，用户明确要求查看计划时仍置`待确认计划`。design SKILL.md / AGENTS.md 双写硬集合 6 项。
## 2026-09-08 · 来源变更 streamline-ai-workflow-overhead（归档轻量门禁与 diff 分类自动升级）
**坑**：Archive 阶段永远跑顶层契约套件（耗时 400s+）会把"机械归档（移目录 + 改索引 + memory 沉淀）"的轻量动作拖成重量级，且机械归档产生的 `openspec/specs/` / `openspec/archive/` 新状态本身已超 Verify 阶段范围——必须重跑校验但不必重跑契约套件。手工口头跳过会埋下治理漂移。
**解**：`scripts/validate-workflow.sh` 新增 `--archive-light` / `--archive-files` 入口 + `WORKFLOW_ARCHIVE_GATE=1` 环境变量；Verify 后仅 `git diff --name-only <base> -- <list>` 非空（工作流可执行文件、助手入口、技能、契约测试、治理规格变更）才改跑契约套件，否则纯轻量门禁；与 `--require-openspec` 互斥（exit 2）。契约套件调用收敛到 `run_contract_suite` 函数（mutation 测试只删一处即可检出）；skip 透明化块抽为 `render_contract_suite_skips`（promoted 与默认路径都调用）；git 不可用且 gate 开启时 fail-closed（[FAIL] + 非零）。
## 2026-09-08 · 来源变更 streamline-ai-workflow-overhead（`.ai-local` 精确清理 + 已归档缓存）
**坑**：`.ai-local` 既是运行时锁（`.validate.lock`）又是 review manifest 缓存；`rm -rf .ai-local` 会清掉活跃锁使并发校验失守；反之永不清理会让 `.ai-local/reviews/` 永远膨胀掩盖活跃 review。
**解**：Archive 阶段在 OpenSpec 归档文件持久最终证据（最终 manifest ID / comparison base / finding 状态 / 未验证范围 / 残余风险）后，仅删 `.ai-local/reviews/<change>/`（精确子路径，不得无子路径）；活跃 review、STALE manifest、未持久化最终证据的目录不得清理；不得把缓存清理当作关闭 finding 的手段。archive SKILL.md + .ai/rules/review.md 双写禁止性条款 + shell 片段。
## 2026-09-12 · 来源变更 speed-up-workflow-gates（--fast 指纹缓存与契约套件并行）
**坑**：`--fast` 23 秒里 21.4 秒来自三组输入未变也重复实际执行的检查（review manifest 14.6s / OpenSpec validate 3.8s / 事实工具 3.0s）；契约套件 200+ 用例每例复制整仓夹具后串行，单模块 >8 分钟。阶段审查还抓到四个缓存边界坑：OpenSpec 指纹漏了 `openspec/changes/**`（`validate --all` 也校验活跃变更）；外部导出的 `WORKFLOW_FAST_CACHE=1` 会被非 fast 门禁继承；实际执行 FAIL 后旧指纹缓存残留，输入回退可掩盖失败；输入缺失被编码成稳定 `<missing>` 指纹仍可命中。阶段 2 另抓到 `--fast` 与 required/archive-light 组合不拦截、并行 runner 把 unexpected success 判绿两个坑。
**解**：缓存只进 `--fast`（wrapper 注入 `WORKFLOW_FAST_CACHE=1`；非 fast 显式置 0；`--fast` 与 `--require-openspec`/`--archive-light` 组合一律 exit 2）。指纹 = 检查命令 + core 自身 + 声明输入文件内容；任一输入缺失 → 无指纹 → 只实际执行不读写；实际执行 FAIL/SKIP → 删除该检查缓存；只缓存 PASS，命中时在检查行内透明标注`指纹/沿用`来源，仍计 PASS 不新增状态。契约套件用 `scripts/tests/run_validate_workflow_parallel.py` fork-per-test 有界并行（默认 `min(CPU,8)`，`WORKFLOW_TEST_JOBS=1` 回退原 unittest 命令），unexpected success 与 unittest 同判非零。实测：fast 暖缓存 1.83s、契约套件 188 用例 146s、required 门禁 170.8s 全绿。测试夹具类不要无上下文继承 `ValidateWorkflowContractTest`——会让 40 个基类用例被整模块重复执行，需复用基建时继承 `ContractFixtureTest`。
## 2026-09-13 · 来源变更 speed-up-ci-validation（GitHub Actions validate 提速）
**坑**：源仓契约套件切到并行 runner 后没有同步随包 wrapper/manifest，安装目标仍串行且重复三份完整套件；wrapper 解析 `--require-openspec` 只做冲突标记却未转发 core，目标缺 OpenSpec CLI 时可错误退出 0；安装器集成测试仅用动态总数守卫时，关键用例被删除或改成 allowed skip 会随总数一起消失。
**解**：runner、wrapper、契约测试进入 shared 资产并保持字节一致；wrapper 把 `--require-openspec` 同时加入 core 参数，成功路径解析并透出 `Ran N tests`，缺失计数 fail-closed。每个 assistant 只跑一份真实完整公共门禁，required 缺 CLI 在复制目标中用一用例 sentinel + 真实 marker 证明套件调用与非零传播；动态加载必须用 exact 模块名 `scripts.tests.test_validate_workflow` 并恢复源仓模块注册，同时显式守护关键 test ID 存在且未 skipped。完整安装器套件由 1109–1375s 降至 297.92s。
## 2026-09-17 · 来源变更 align-workflow-semantics-and-business-context（OpenSpec 活跃/归档同名身份）
**坑**：base 中已存在同名归档目录时又创建活跃 `openspec/changes/<name>/`，状态真源出现 active/archive 双身份；归档移动目标会与既有目录冲突，且 delta 容易把 base 已有 Requirement 再写成 ADDED。
**解**：扩展语义前先检查 `openspec/archive/<name>` 是否已存在，收口/续作使用唯一变更名；delta 先对 base 主规格求 Requirement/Scenario 集合，已有目标用 MODIFIED 且保留非冲突 Scenario，真正不存在的能力才 ADDED。契约测试禁止 active/archive 名称交集。
## 2026-09-17 · 来源变更 align-workflow-semantics-and-business-context（archive-light 升级必须先分类）
**坑**：wrapper 先跑轻量 core，之后发现语义 diff 才追加顶层契约套件，导致 core 没有收到 `--require-openspec`；`git diff ... 2>/dev/null || true` 会把非法 base/pathspec 吞成“无变化”，归档可假绿。
**解**：在调用 core 前完成 archive diff 分类；Git 缺失或 diff 非零立即 exit 2，命中语义变化时把 `--require-openspec` 追加到 forwarded arguments，再执行 core 和顶层契约套件。回归必须同时断言 core 参数、diff fail-closed 和契约套件执行。
## 2026-09-18 · 来源变更 extend-project-context-and-evidence-reuse（随包契约不得假设双助手共存）
**坑**：新增 ProjectContextEvidenceContractTest 直接遍历 `.codex` 与 `.claude` 两侧 verification 技能；便携安装目标按设计只包含单侧适配，Claude-only/Codex-only 目标内该测试因缺失另一侧而失败。
**解**：随包契约测试先枚举当前安装中实际存在的助手技能，至少一侧存在即可继续；只有源仓或双运行时安装才自然检查两侧。新增测试必须在单助手安装目标中跑通，不能把“另一侧不存在”当缺陷。
## 2026-09-18 · 来源变更 extend-project-context-and-evidence-reuse（Git 元数据也必须锁定 workspace 边界）
**坑**：只校验项目根落在 workspace 内还不够；项目根内 `.git` 符号链接或 gitdir 文件可把 `rev-parse` / `ls-files` 引导到外部仓库，`verified_commit=current` 可能来自 workspace 外 HEAD。
**解**：在使用 Git 前校验 `.git` 元数据闭包：符号链接/gitdir/commondir/alternate object store/内部 symlink 的目标必须解析进声明 workspace，越界在输出前 fail-closed；Git 子进程移除外部 `GIT_*` 环境覆盖并固定 worktree。`project-context` 与 `workspace-search` 共用同一边界，并有外部仓库 symlink 与 commondir 回归。
**坑**：即使 gitdir 边界留在 workspace，项目 `.git/config` 仍可通过 include + `core.fsmonitor` 让 `git ls-files` 执行脚本，破坏“只读查询”。
**解**：所有 Git 子进程统一用命令行最高优先级配置禁用 `core.fsmonitor`、hooks、外部 attributes/excludes 和 pager，并把 global/system config 固定为 `/dev/null`；用 include + fsmonitor marker 回归证明脚本未执行。
## 2026-10-13 · 来源变更 merge-standard-small-task-workflow
**坑**：本仓库源工作区 `.git/refs/heads` 对目录创建呈只读，创建嵌套 `feature/*` 分支或 worktree 均在 ref lock 阶段失败，且 `.worktrees` 可能残留空目录。
**解**：先 `git worktree prune` 清理残留，再用 `git bundle --all` 导出只读基线到 `/tmp` 并克隆隔离工作区实施；完成后通过 fetch + `--no-ff` 回收 feature 变更，禁止 chmod 或绕过源 `.git` 挂载权限。
## 2026-10-26 · 来源变更 merge-lc-workflow-improvements
**坑**：安装目标侧回流的技能可能只更新 Codex，且删除源仓已有的小任务豁免/验证说明；只迁移 task_id 而 wrapper 不发 phase 会让阶段汇总为零，累计所有 duration 又会把 summary 重复相加。
**解**：固定来源提交，按能力比较并保留源仓已有保障，同步双助手和安装镜像；wrapper 在末条 summary 前发一条 phase，汇总仅认目标任务的有效 phase，并用真实 CLI 路径验证一次计时。归档发现未跟踪治理文件时直接 required，因为 git diff 不包含它们。
## 2026-10-26 · 来源变更 merge-lc-workflow-improvements（安装回归输入）
**坑**：安装端到端测试包含首次安装与重复安装；测试期间同步源资产说明，会使重复安装因内容变化报冲突。新增工具用例后，安装测试固定工具计数也需同步。
**解**：完整安装回归期间冻结源资产；本次工具计数由 65 更新为 72。修复后固定资产重跑受影响端到端方法，两侧完整契约、缺 CLI required 失败与幂等检查全部通过；不得把源变化造成的冲突误修成允许覆盖。
## 2026-11-05 · 来源变更 workflow-tiers-incremental-cache-context（管道退出码失真）
**坑**：`cmd | tail -n N; echo $?` 捕获的是 tail 的退出码，长门禁真实退出码被吞，证据容易误记。
**解**：门禁证据以 wrapper 自身汇总行（PASS=/FAIL=）为准；确需退出码时先落日志文件再单独读取，或用 PIPESTATUS。
## 2026-11-05 · 来源变更 workflow-tiers-incremental-cache-context（diff --check 与提交区间）
**坑**：`git diff --check <base>..HEAD` 只检查已提交内容；工作树里的修复未提交时复跑仍红，易误判修复无效。
**解**：先提交修复再跑区间 diff-check；echo+cat 拼装文件会在 EOF 引入尾随空行，写完即查尾行（本次终验链实际抓到）。
## 2026-11-05 · 来源变更 workflow-tiers-incremental-cache-context（缓存入口必须排除升级路径）
**坑**：给 --standard 开指纹缓存时未排除 `--archive-files` 升级为 required 的调用，required 语义会读写缓存，违反"required 禁止读写验证缓存"契约（综合审查 F-2）。
**解**：缓存开关条件必须带 `require_openspec_user=0` 守卫；新增任何缓存入口时同步检查 promoted/升级路径，并用夹具测试锁定。
## 2026-11-06 · 来源变更 layered-validation-agent-gating-output-metrics（镜像资产必须登记 byte-sync 映射）
**坑**：源树与 `scripts/ai-workflow-assets/shared/scripts/**` 是双树镜像，但 byte-sync 断言只检查 `test_install_ai_workflow.py` 映射表里登记过的路径；workflow-tiers 给 `new-openspec-change.py` 加 summary 子命令时漏同步镜像，37 行漂移因未登记而长期无人发现（阶段二 CQ-2）。
**解**：改动任何在 `scripts/ai-workflow-assets/shared/scripts/` 有对应副本的源文件时，先 cp 同步镜像，再确认该路径已登记进 byte-sync 映射；新增镜像文件必须同步补映射条目。
## 2026-11-06 · 来源变更 layered-validation-agent-gating-output-metrics（agent_dispatch stdin 非法 UTF-8 崩溃）
**坑**：`json.load(sys.stdin)` 遇非法 UTF-8 字节抛 `UnicodeDecodeError`，它虽是 `ValueError` 子类但不在 `(JSONDecodeError, OSError, TypeError)` 捕获集内，承诺"稳定单行 JSON 输出"的 CLI 直接 traceback 且不记事件（阶段二 CQ-1）。
**解**：stdin 解析的 except 元组显式加 `UnicodeDecodeError`；自定义异常（如 ResultError）同为 ValueError 子类，收宽捕获时必须排在前面。
## 2026-11-06 · 来源变更 layered-validation-agent-gating-output-metrics（sharedRepository 模式断言环境失败）
**坑**：git `core.sharedRepository=true` + umask 0002 使干净检出工作树全为 664/775，`test_manifest_modes_are_exact_and_match_files` 在不含任何改动的 HEAD 上同样失败；全套运行时 `__pycache__` 还会让资产枚举断言瞬态失败。易把环境失败误记为变更引入的回归。
**解**：怀疑环境性失败时用临时干净 worktree（`git worktree add <path> HEAD --detach`）复跑同用例归因；确属环境后在台账记录"预存、与本变更无关"，探针 worktree 用完即删。
