## 2026-08-16 · 来源变更 add-workflow-installer
**坑**：`cp -p 文件 已存在目录` 不报错而是静默成功（把文件复制进目录内部，exit 0）——`set -e` 与返回码检查都抓不住，安装器因此出现过"目标同名路径是目录 → 假绿 exit 0"
**解**：复制前前置拒绝：`[ ! -d "$dst" ] || { 报错; exit 1; }`；审查推理不可替代实测（本坑由红测揭穿，两方独立实测确认）

## 2026-08-16 · 来源变更 add-workflow-installer
**坑**：`TARGET="$(cd "$TARGET" && pwd)" || die "...$TARGET"` 失败时赋值已生效、TARGET 已被置空——报错信息丢失路径；更严重变体是静默空串导致后续以 `/` 为根写入
**解**：命令替换赋值用临时变量承接：`norm="$(cd -- "$p" && pwd)" || die "...$p"`；对安装/删除类脚本显式拒绝根目录 `/`；危险路径的"先红"实测若会触发真实破坏（写 /），以代码差异+安全绿测替代并记录 TDD 偏差

## 2026-08-16 · 来源变更 工作流端到端验证（临时项目 add-greeting）
**坑**：迁移 .codex 工作流后只改了校验器未同步改安装器，install-workflow.sh 仍只装 .claude 资产，装后自检因 .codex 缺失整片判红
**解**：校验器与安装器是结构不变量的两面，必须同步演进；安装器已补 AGENTS.md + .codex/（README/skills/ai-kb/sdd）+ .gitignore 草稿区规则

## 2026-08-16 · 来源变更 工作流端到端验证（临时项目 add-greeting）
**坑**：openspec CLI 严格校验要求 Requirement 正文含英文 SHALL/MUST，纯中文"应"判错；且 validate --all 还会校验主 specs（缺 ## Purpose 即红）
**解**：Requirement 用"系统 SHALL …"中英混排；archive 新建主规格先写完整骨架（# 标题 + ## Purpose + ## Requirements）再并入 delta；终验跑 openspec validate --all

## 2026-08-16 · 来源变更 工作流端到端验证（临时项目 add-greeting）
**坑**：python unittest 的 __pycache__/*.pyc 被 git add -A 误跟踪，规格审查判越界；安装器不管理目标 .gitignore，.codex/sdd 草稿区裸奔为未跟踪文件
**解**：项目初始化即写 .gitignore（__pycache__/、*.pyc）；安装器幂等追加 .codex/sdd 忽略规则；实现提交后 git ls-files | grep pyc 自查

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

## 2026-08-23 · 来源变更 remove-installer-business-knowledge
**坑**：安装工具源仓库混入目标项目卡、契约、业务 memory 和 workspace 配置后，仓库职责变得模糊，后续 push 或备份会扩散目标项目知识。
**解**：安装工具源仓库只保留空白 registry、通用项目登记契约和共享工作流；目标项目知识由目标工作区维护。源仓库用根锚定 ignore 防回流，并验证安装器资产仍不携带源项目业务状态。

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

## 2026-08-28 · 来源变更 add-installer-upgrade-path（白名单双份坑）
**坑**：校验器外部命令白名单存在**两份**——`test_validate_workflow.py` 的 `VALIDATOR_COMMANDS`（fixture 沙箱）与 `test_install_ai_workflow.py` 的 `PORTABLE_VALIDATOR_COMMANDS`（安装目标受限 PATH）。CQ-1 修 cat 时只同步了前者，后者遗漏导致 `InstalledWorkflowValidationTests` 6 个子测试死在目标内契约测试的 setUp（`missing test prerequisite: cat`），且该套件不在 validate-workflow.sh 门禁内、CI 不跑，静默挂了两个版本。
**解**：core 新增外部命令时必须同步**两份**白名单并各跑一次对应套件；更稳妥的做法是让两份白名单单一来源化（列为后续候选）。安装器套件（`python3 -m unittest scripts.tests.test_install_ai_workflow`）应纳入手动终验清单。

## 2026-08-28 · 来源变更 add-installer-upgrade-path（事务窗口同形恢复）
**坑**：`_publish_removed_file` 在 rename(name→backup) 与 `journal.append(_RemovedFile(...))` 之间没有 try/except 兜底，rename 成功而 journal 失败时目标文件已不翼而飞；同类窗口在 `_publish_created_file`（清理未武装）与 `_publish_updated_file`（`_restore_unjournaled_update`）都已覆盖，remove 路径漏了。
**解**：每个 publish 路径都要有同形恢复 helper（rename 后 stat/identity/journal 任一失败 → 还原原文件），recovery helper 必须处理「同次 publish 重复触发恢复」的幂等性；新增路径必须补 fault-window 测试（与 create/update 同款 `test_*_journal_fault_windows_leave_no_published_artifacts`）。

## 2026-08-28 · 来源变更 add-installer-upgrade-path（提交前全量预读）
**坑**：`_commit_journal` 顺序销毁每个备份后才发现下一个 entry 的备份 stat/read 失败——已销毁的备份再也无法回滚，半升级状态：磁盘是 v2、内容哈希是 v1，下一次升级永远 SKIPPED。
**解**：在销毁**任何**备份之前，先一次性预读所有 update/remove 条目的备份内容＋模式到内存列表；通用 dispatcher（`_ensure_recovery_backup` 按 entry 类型路由到 `_ensure_update_recovery_backup` / `_ensure_removed_recovery_backup`）在 destroy 循环失败时对每个已销毁条目重建恢复备份，并**无条件**包含当前 entry（KeyboardInterrupt 在 unlink 成功之后才抛，flag-based 检测会漏）。

## 2026-08-28 · 来源变更 add-installer-upgrade-path（InputError 重新打包陷阱）
**坑**：`InputError` 继承自 `ValueError`，`except (UnicodeDecodeError, ValueError)` 会把 parser 内部抛的 `InputError`（如 `_unique_json_object` 的 duplicate-key 诊断）一并吞掉，重新打包成泛化的"is not valid JSON"，退出码不变但运维诊断全丢；`load_manifest` 用 `except InputError: raise` 显式穿透是正确的范式。
**解**：项目内自定义异常类必须**先**于其继承的内建异常被 `except` 透传：`except InputError: raise` 放在 `except (UnicodeDecodeError, ValueError)` 之前；review 时重点扫描 parser/validator 的 except 链是否吞掉自定义诊断。fail-closed 存在性检查用 `os.lstat` 不用 `os.path.exists`（后者跟符号链接，dangle 也返回 False）。JSON 严格解析用 `object_pairs_hook=_unique_json_object` 检重键 + 白名单 key-set + `type(x) is int` 拒绝 `True == 1` 假版本号。

## 2026-08-30 · 来源变更 harden-gate-coverage-and-tiers（importlib 动态加载随包测试）
**坑**：importlib 按路径加载测试模块若不先 `sys.modules[spec.name] = module`，随包文件里的 @dataclass 在字段解析时取 `sys.modules.get(cls.__module__)` 得 None 直接 AttributeError；且不带 -B 运行会把 __pycache__ 写进资产目录，被"manifest 精确枚举物理资产"用例逮住。
**解**：与仓库既有 load_installer_module 同款写法——先注册 sys.modules 再 exec_module；动态统计资产测试一律 PYTHONDONTWRITEBYTECODE=1/-B 调用；资产目录出现 __pycache__ 立即删除并排查调用方。

## 2026-08-31 · 来源变更 fix-install-workflow-legacy-ai-kb
**坑**：知识层迁移到 .ai/ 并删除 .claude/.codex/ai-kb 平行正文（943d914）后，install-workflow.sh 仍手工枚举旧路径 cp，安装必然中途退出码 1 且目标残留半成品；该脚本零测试覆盖，迁移门禁未拦截。连带四处：目标完全缺 .ai 层；校验套件只装单文件（缺 lib/validate-workflow-core.sh 与 tests/ 依赖，装后自检必红）；project.md 占位文案仍是五阶段旧措辞；随包契约套件要求无便携安装器脚本的目标必须携带 .ai/assistant-profile.json（缺失时 WorkflowProfileTests 两个 selected-only 用例失败，因为 _install_selected_metadata 的降级断言要求 profile 存在）。
**解**：资产源改为 scripts/ai-workflow-assets/{shared,claude,codex} 三树整体复制（与便携安装器共用单一来源，字节一致性由 test_install_ai_workflow 背书），悬空源路径结构性不可能；随包契约套件的目标模型是"单侧+profile"，双运行时目标生成 profile 会把 2 例失败放大为 10 例（非选中侧门禁突变不被拒），随装便携安装器三件也不行——scripts/lib/install_ai_workflow.py 是套件的"源仓标记"，随附即被要求成为完整源仓（git 已提交钩子+CI 配置）；终解（用户选定）：双装目标不生成 profile、不随附安装器文件，装后自检降层跑 validate-workflow.sh --fast（秒级），完整套件归源仓 CI；另：迁移前旧布局残留 ai-kb/{kb,rules,memory} 正文会让目标校验器 legacy_ai_kb_body_absent 必红，安装器须检测并要求 --force 整目录备份 ai-kb.bak/ 后清除；.gitignore 改写带标记幂等块（须含 __pycache__/，core 有"Python 缓存路径已忽略"检查）；新增 scripts/tests/test_install_workflow.py 端到端契约测试补零覆盖，空装用例即布局漂移回归捕获器。
