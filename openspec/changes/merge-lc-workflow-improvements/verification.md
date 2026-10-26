# 验证与审查证据

环境：Python 标准库/Bash，OpenSpec 1.3.1（与 CI 固定版本相同，安装于 /tmp/ai-agent-openspec），后续验证设 OPENSPEC_TELEMETRY=0。来源提交 76a1676319eaa7e6dbdd74f2a4b8b72d06f6fc58，比较基线 c33eab2841934574c17f3913e2415d6a0ecc695e（包含已确认规范；原 main 20f3976a32261d0d0cd8be9d9135424dffc95f39）。原始日志在实现工作区 .ai-local/merge-lc/，下面持久记录命令与结果。

## Build

| 命令/验证 | 结果 |
|---|---|
| 基线 `bash scripts/validate-workflow.sh --fast`，补齐固定版本 CLI 后 | PASS=203 FAIL=0 SKIP=0 |
| `python3 -B -m unittest discover -s .ai/tools/tests` | 72 tests，退出 0 |
| `python3 -B -m unittest scripts.tests.test_workflow_events scripts.tests.test_workflow_wrapper scripts.tests.test_openspec_templates` | 16 tests，退出 0；包含真实正常 fast wrapper |
| `python3 -B -m unittest scripts.tests.test_install_ai_workflow.PortableAssetManifestTests` | 4 tests，退出 0 |
| StrictGateRoutingContractTest | 5 tests，退出 0 |
| core 新 registry 调度目标测试 | 先因缺少实际调用失败，加入必需套件后 1 test 退出 0 |
| `openspec validate --all --strict --no-interactive` | 12 passed、0 failed，退出 0 |
| `python3 scripts/new-openspec-change.py check openspec/changes/merge-lc-workflow-improvements` | 四件套结构通过，退出 0 |
| `git diff --check` | 退出 0 |

红绿证据：治理路由先红 4 tests/9 failures，验证层级守卫补红 1 test/1 failure，修改后 5 tests 全绿；事件/模板先红 13 tests 中 2 failures/1 error，finalize 命令缺失先红，登记工具缺失先红；wrapper task_id 及真实 phase 早退路径均先红后绿。安装分发四项新资产先红 1 test/4 failures，加入清单/资产后四个清单测试全绿。压力基线及绿测见 pressure-baseline.md、pressure-green.md，15 个场景行为 PASS，明确保留 N 的既有成功术语歧义而不冒称安装严格验收。

首次完整 required：core PASS，顶层 215 tests（426.783s）出现 6 failures/1 error，最终 PASS=283 FAIL=1 SKIP=0，退出 1。6 failures 均来自三个继承类中两侧 Verify mutation 仍匹配旧 --fast 文案；更新为现行 --standard 后三个目标测试 30.536s、退出 0。另一个 fast wrapper 60s 超时用例单独运行 30.484s、退出 0，未改 timeout/断言。完整门禁必须继续复验，单跑通过不等同并行完整套件通过。

## 任务级独立审查

- reviewer：build_review，按门禁路由、证据/输出保护、安装传播三个不变量聚合。
- 首次 manifest：0a855c233d018f18f599afcdcc97d4444c9b5feb4c463fab253f9e40c177de61，读取前和结论前 VALID，PASS，无 findings。
- 差异复审 manifest：731a96d23f5c0bdf33c50bec82b11100b26ab0a51bdc407a69f171a74f0270dc，读取前和结论前 VALID，PASS；仅审旧 mutation 修复、memory 新事实和清单格式复原，未重做全量审查。
- finding 状态：open=0、resolved=0、not-an-issue=0、accepted-risk=0。

## 后续门禁

安装完整套件：`python3 -B -m unittest scripts.tests.test_install_ai_workflow scripts.tests.test_install_workflow` 初次 98 tests（724.047s），3 个失败均在同一端到端方法：两侧旧工具计数仍为 65（实际 72 全绿）；一次重复安装冲突由主会话在执行中同步知识说明导致源资产变化。固定计数并冻结资产后，精确复跑 `python3 -B -m unittest scripts.tests.test_install_ai_workflow.InstalledWorkflowValidationTests.test_installed_codex_and_claude_validate_without_source_or_openspec`，1 test、561.033s、退出 0。该方法重新覆盖两侧工具 72 项、完整公共契约、required 缺 CLI 必须失败及 sentinel 真执行、Git 身份保护和重复安装幂等；其余 97 项在初次运行通过且受测安装行为未改变。原始输出 install-full.log、install-rerun.log，退出结果 install-rerun.exit=0。

修复后主会话 required、Verify 双阶段、归档与整合复验待记录；当前不声明全变更已完成。

## 未验证范围与残余风险

当前未完成项见后续门禁。新增登记草稿不承诺多文件事务或对抗并发替换父目录；finalize 证明检查时身份，不自动确认 finding 结论。既有安装成功术语差异见压力记录 N，本次不改变安装成功定义。
