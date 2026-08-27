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

## 2026-08-20 · 来源变更 install-portable-ai-workflow（资产读取边界）
**坑**：只对资产叶文件使用 `O_NOFOLLOW` 会放过资产根或父目录 symlink；只比较 dev/ino/type 还会接受同 inode 读取期间产生的混合字节。
**解**：从可信根目录 fd 逐组件以 `O_DIRECTORY|O_NOFOLLOW` 打开，叶文件相对已绑定 fd 读取；完成后重开父路径核对绑定，并比较 dev/ino/type/size/mtime/ctime 后才接受内容。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（计划输出注入）
**坑**：把 manifest path 或 resolved target 原样写入逐行协议时，换行、回车和终端控制字符可伪造动作或 RESULT 行。
**解**：在 manifest path 与 target 输入源头拒绝 Unicode `Cc` 控制字符，错误固定走单行 stderr 且 stdout 为空；正常路径的稳定输出契约保持不变。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（安装测试数据源）
**坑**：CLI 测试运行仓库生产资产时复用了临时最小 fixture 的硬编码字节，事务安装正确复制真实资产仍会被误报内容错误。
**解**：临时 source 的行为测试断言 fixture 字节；调用仓库 wrapper 的集成断言必须逐字比较对应生产资产，避免混淆两套数据源。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（原子交换身份校验）
**坑**：`renameat2(RENAME_EXCHANGE)` 会更新交换对象的 ctime；交换后继续比较计划前完整 stat version 会把合法 `.gitignore` 更新误判为竞态替换。
**解**：交换前验证完整 version，交换后安全重读并比较 dev/ino/type、size、mode 与原 bytes；journal 使用交换后的 version 跟踪备份身份，避免忽略真实替换或接受自身 ctime 变化。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（事务 journal 时序）
**坑**：先创建资源再等后续 open 成功才记 journal，会在中间失败时留下目录；在 `finally` 静默吞掉原子换回失败还会把不可恢复状态误报成普通主错误。
**解**：资源一获得可核验身份就立即记 journal，再做后续操作；局部恢复失败必须保留交换对象并显式升级为“主错误与回滚失败”，由外层继续回滚此前 journal。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（事务发布与提交窗口）
**坑**：目录 fd 只证明曾经的父目录身份，hard-link 后再准备 journal 会让 rename replacement 和 stat/unlink/dup 故障留下移走目录中的文件；销毁唯一备份后继续 fsync 还会报告无法回滚的失败。
**解**：publication 前后及 commit 前从 root fd 重开父路径核对 held fd；文件预置 journal 后原子武装，目录先在随机名下取得身份与 journal 资源再 `RENAME_NOREPLACE`，唯一 backup unlink 作为最后可失败步骤且成功后不再执行失败出口。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（故障注入匹配重构）
**坑**：目录创建从最终名改为 staged 随机名后，仍按 `.ai` 匹配 `os.open` 的旧故障测试会静默不再注入，测试显示绿色却没有覆盖原错误窗口。
**解**：故障测试应匹配稳定语义特征而非旧实现名，并断言注入确实发生；生产清理同时保留 stat 或 nofollow-open 任一独立取得的 inode 身份，无法取得身份时升级 cleanup failure，禁止盲删路径当前对象。


## 2026-08-20 · 来源变更 install-portable-ai-workflow（非普通 profile 的失败边界）
**坑**：校验器虽先把 FIFO profile 判为非法，若仍继续递归扫描共享 `.ai`，`grep -R` 会打开该 FIFO 并永久等待，导致 fail-closed 退化为挂起。
**解**：profile 类型或内容校验失败后先输出内部计数并立即结束 core；公共 wrapper 仍独立运行顶层 contract。解析普通文件时同时使用 `O_NOFOLLOW` 与 `fstat`，错误输出不得回显 profile 内容。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（单助手忽略契约）
**坑**：validator 无条件检查两侧 SDD ignore probe，会拒绝真实安装器只声明所选助手 `/.<assistant>/sdd/` 的合法 `.gitignore`，源仓双侧 ignore 会掩盖该问题。
**解**：助手专属 ignore probe 必须与 `assistant_required` 使用同一集合；测试从真实安装器取得 profile 与 managed `.gitignore`，并彻底移除未选侧后分别验证 core 和公共入口。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（配置决策重校验）
**坑**：只在开头解析 profile 的 assistant，随后文件被替换、删除或换成 symlink 时，validator 仍会按旧决定成功结束，安全决策与最终文件状态脱节。
**解**：无跟随读取时捕获 dev/ino/type/size/mtime/ctime 与内容 SHA-256；所有检查结束、汇总前重新安全读取并比较完整 token，把该处作为线性化点，变化只输出固定错误而不泄露内容。

## 2026-08-20 · 来源变更 install-portable-ai-workflow（测试解释器分流）
**坑**：基础 contract fixture 把所有 `python3` 调用都 stub 成空成功；有效 profile 会得到空 assistant 而失败，只有额外启用真实 parser 的子类能通过，安装目标的无条件 base contract 因此假失败。
**解**：基础 fixture 仅把 `python3 -B -c` profile parser 分流到真实解释器，其余 unittest/tool 调用继续 stub；单侧公共 wrapper 测试必须完全移除另一侧并断言唯一 summary。

## 2026-08-21 · 来源变更 install-portable-ai-workflow（随包契约自包含）
**坑**：随资产分发的 contract tests 若调用源仓安装器、读取某个历史 change，或让 recording stub 吞掉 profile parser，会在安装目标中把缺少生产者依赖误报为产品失败，也可能让 mutation 因输入不存在而假绿。
**解**：安装器存在时覆盖双助手；缺失时从严格 canonical profile 只验证当前侧并明确 skip 另一侧。配置解析调用由 stub 精确分流到真实解释器，mutation probe 自建并先验收合法基线，所有 fixture 的 profile、入口和替换目标都从当前助手派生。

## 2026-08-21 · 来源变更 install-portable-ai-workflow（异步异常与备份销毁窗口）
**坑**：原子 syscall 已成功但 Python 状态赋值前收到 `KeyboardInterrupt` 时，依赖事后布尔会误删承载原文的交换路径；最终 binding 校验与唯一 backup unlink 之间仍可发生目标替换。
**解**：事务边界捕获 `BaseException`，回滚成功后原样重抛取消；未 journal 的 exchange 依据两个路径的 nofollow inode 现态判定并恢复。销毁唯一 backup 前再次核验已安装 target binding，异常时保留外部替换和原始 backup，不泄漏正文。

## 2026-08-21 · 来源变更 install-portable-ai-workflow（syscall 后线性化）
**坑**：仅在 `link`/`exchange`/`unlink` 返回后更新 Python 布尔或只做操作前检查，会被 syscall 已生效后的异步异常穿透；已有异常期间吞掉 cleanup failure 还会把残留误报为成功取消。
**解**：发布失败按两个 nofollow 路径的 inode 现态判定所有权，只有绑定匹配才删除并 fsync；cleanup 失败升级为 rollback-failed。销毁唯一 backup 前先安全捕获原 bytes/mode，unlink 后再校验 target 作为提交线性化点，失败或取消时重建唯一 recovery backup 并更新 journal 后再回滚。


## 2026-08-21 · 来源变更 install-portable-ai-workflow（validator fixture 边界）
**坑**：顶层 contract fixture 从仓库根递归复制除 `.git` 和缓存外的一切；在多项目根运行时会把无关业务目录和敏感文件复制到每个测试临时目录，造成数量级磁盘写放大，并越过 validator 实际输入边界。
**解**：fixture 只按固定顶层白名单复制 `.ai`、存在的单侧或双侧助手目录、`openspec`、`scripts` 和三个入口/忽略文件；测试同时放入无关目录与敏感文件 sentinel，断言它们绝不进入 fixture。不要用 Git tracked 清单，因为安装后的工作流资产本身可以尚未跟踪。

## 2026-08-21 · 来源变更 install-portable-ai-workflow（fixture nofollow）
**坑**：只校验白名单顶层不是 symlink，随后调用默认 `copytree`，仍会跟随嵌套目录/文件 symlink 复制外部内容；断链 symlink 会被 `exists()` 当作缺失跳过，预检后替换还存在检查—复制窗口，特殊文件异常可能泄漏源路径。
**解**：以绑定源根的 directory fd 两阶段扫描和复制：所有组件用 `lstat` 语义、`O_NOFOLLOW`、类型与完整 stat token 校验，只接受目录和普通文件；复制前后重验 token，任何变化或特殊类型统一返回固定脱敏错误并删除未完成 fixture。真正不存在的未选助手目录和入口仍可跳过。

## 2026-08-23 · 来源变更 fix-installer-python-38
**坑**：`from __future__ import annotations` 只延迟普通注解求值，不延迟类型别名赋值；安装器在 Python 3.8 因 `JournalEntry = A | B | C` 模块加载失败，继续执行后又命中 Python 3.9 的 `Path.is_relative_to`，测试文件里的括号多 context manager 也依赖 Python 3.10 语法。
**解**：运行时类型别名使用 `typing.Union`；路径包含判断用 `Path.relative_to()` 捕获 `ValueError` 的私有 helper 等价实现；多 context manager 测试改写为逗号列表。完整回归还需同步随包契约测试的实际总数，避免活动资产与硬编码计数脱节。

## 2026-08-23 · 来源变更 sanitize-git-baseline-secrets
**坑**：先把包含知识库正文的工作树写入 Git root commit，再执行敏感内容审查，会把字面凭据固化到对象历史；此后仅修改当前文件无法阻止 clone、push 或备份恢复旧值。
**解**：创建或重置 Git root 前先扫描待入库内容；若提交后才发现凭据，在无 remote 且获得明确授权时同时净化当前树、重建 root、删除旧引用、 expire reflog 并 prune 不可达对象。本地清理不能替代外部凭据轮换。

## 2026-08-23 · 来源变更 remove-installer-business-knowledge
**坑**：安装工具源仓库混入目标项目卡、契约、业务 memory 和 workspace 配置后，仓库职责变得模糊，后续 push 或备份会扩散目标项目知识。
**解**：安装工具源仓库只保留空白 registry、通用项目登记契约和共享工作流；目标项目知识由目标工作区维护。源仓库用根锚定 ignore 防回流，并验证安装器资产仍不携带源项目业务状态。

## 2026-08-23 · 来源变更 add-test-login-project
**坑**：严格模式运行时行为把测试与实现放进同一提交后，审查者无法从 Git 历史独立复现 TDD 红阶段；隔离 worktree 还不会自动 materialize 被忽略的 SDD 占位目录。
**解**：运行时实现先提交 test-only 状态或保留可复核的临时红输出，再提交实现；隔离 worktree 需按本地忽略规则补齐 SDD 占位目录后运行完整门禁。安全契约测试应覆盖实际算法、随机源、默认参数和错误路径，而不只断言内部结果非空。

## 2026-08-23 · 来源变更 add-origin-remote
**坑**：标准 Verify 阶段的 OpenSpec 四件套尚未提交时，把 `git status` 笼统断言为 clean 会与实际未跟踪流程产物冲突。
**解**：远程或本地配置类变更应精确断言分支、tracked/staged 差异和允许的未跟踪流程文件清单；添加 remote 只写 `.git/config`，fetch、pull、push 仍必须另行授权。

## 2026-08-26 · 来源变更 initialize-git-repository（历史基线归档）
**坑**：归档长期停留的初始化变更时，实施时的初始提交哈希与“无 remote”状态可能已被后续授权的历史净化和远程配置变更取代；直接照搬旧证据会与现行主规格冲突。
**解**：用当前 parentless root、clean 状态和 ignore/OpenSpec 基线重新验收；delta 明确“初始化本身不添加 remote/不推送”与后续独立授权远程配置的边界，并记录旧证据到新历史的演进关系。归档前必须先提交审查产生的 OpenSpec 修正并复跑 required 门禁。

## 2026-08-26 · 来源变更 install-codex-workflow-yuxiaor（外部目标预检身份漂移）
**坑**：跨目录安装的计划确认后，目标根 `.gitignore` 被外部新增 `http-client.http`，固定 SHA-256 预检失败；若无 fail-fast，可能继续生成误导性 PASS 摘要。
**解**：预检命令在所有检查和证据写入前启用 `set -euo pipefail`；身份漂移时保留现场、记录新旧哈希和时间戳，向用户确认新基线后只更新受影响身份与预测值，再完整重跑预检。

## 2026-08-26 · 来源变更 install-codex-workflow-yuxiaor（嵌套仓快照隐私）
**坑**：嵌套仓状态快照虽然只打算落盘哈希，但输出格式写成了 `digest  repo.name`，业务仓目录名仍会进入待提交 evidence，违反“不保存文件名”的边界。
**解**：把仓目录名、HEAD 和 status 一起作为每仓 SHA-256 输入，只输出排序后的摘要行；安装前后使用完全相同格式逐字节比对，既能发现仓与状态映射变化，也不泄露目录名。

## 2026-08-26 · 来源变更 install-codex-workflow-yuxiaor（外部嵌套仓并发漂移）
**坑**：安装器只写目标根，但两个嵌套业务仓在安装后验证前发生外部状态漂移，导致安装前快照失效；初次记录只识别出一个仓，单次 `cmp` 后未启用 fail-fast 还可能打印误导性 PASS。
**解**：根工作流产物与嵌套仓边界分开验收；保留旧快照作历史证据，用 `GIT_OPTIONAL_LOCKS=0` 连续两次采样相同的隐私安全摘要，稳定后经用户确认全部漂移仓再作为验证基线。对比 before/verified 的对称差确认变化仓数，不落盘仓名或状态正文；所有诊断命令先 `set -euo pipefail`。

## 2026-08-26 · 来源变更 install-codex-workflow-yuxiaor（非 Git 根校验）
**坑**：便携工作流可安装到已存在的非 Git 目录，但校验器把 `git check-ignore` 直接当作忽略规则检查；目标根无 `.git` 时即使 `.gitignore` 正确也返回 128。
**解**：先写非 Git 根失败测试；校验时若已在 Git worktree 就直接探测，否则在 `/tmp` 创建临时 Git metadata、以当前目录为 work-tree 执行 `git check-ignore`，退出时清理临时 metadata。不要为通过校验在目标根初始化 Git。

## 2026-08-26 · 来源变更 install-codex-workflow-yuxiaor（单助手测试继承）
**坑**：新增测试在双助手源仓库直接通过，但同一测试会被 installed fixture 的单助手 profile 变体继承；硬编码 Codex+Claude 双断言使合法 Codex-only 目标失败。
**解**：测试断言先用 `_assistant_required_in_fixture` 判断当前 profile，只要求选中助手的存在项，并明确断言未选助手的存在项不出现；同步修改源测试与安装资产测试。

## 2026-08-27 · 来源变更 add-cancel-state-ci-mirror（基线修复）
**坑**：`validate-workflow-core.sh` 用 `test -d .codex/sdd` 断言目录存在，但 `/.codex/sdd/` 被 gitignore 忽略且 `.gitkeep` 从未提交；主工作区靠磁盘遗留空目录通过，新鲜 worktree/clone/CI 检出中该检查失败，并级联击垮依赖实体树拷贝的 38 个契约 fixture 测试。
**解**：用 `git add -f` 跟踪 `.codex/sdd/.gitkeep` 与 `.claude/sdd/.gitkeep`（与安装资产 manifest 既有条目一致）；占位符被跟踪后 SDD 草稿正文仍被忽略。新增「目录存在」类断言时，必须保证其占位符能被新鲜检出处物化。

## 2026-08-27 · 来源变更 add-cancel-state-ci-mirror（沙箱白名单）
**坑**：validate-workflow-core.sh 的 mirror_equal 改用 `| cat -s` 后，契约测试沙箱的 PATH 白名单（test_validate_workflow.py 的 VALIDATOR_COMMANDS）不含 cat：管道失败、重定向先建空临时文件、cmp 比较两个空文件相等——沙箱内全部镜像检查空转假绿；真实 PATH 下一切正常，假绿仅出现在契约沙箱。
**解**：core 新增任何外部命令（cat、sort、tr 等）必须同步 VALIDATOR_COMMANDS 白名单并重跑契约套件；保真度可用「白名单独占 PATH + 注入技能漂移」探针验证镜像检查非零。
