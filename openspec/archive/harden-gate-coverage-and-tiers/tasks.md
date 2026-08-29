# Tasks(范围清单;可执行细化计划由 Design 阶段产出 openspec/plan)

- [x] 1. 规格确认后由 Design 产出零上下文可执行计划(`openspec/plan/harden-gate-coverage-and-tiers.md`),第二次实施前确认后进入 Build。(两阶段确认均已获;阶段1审查 VQ-F3 补记状态迁移)
- [x] 2. P2d 并发锁:wrapper best-effort flock(红测:两并发实例第二例非零;无 flock 降级提示)。
- [x] 3. P2b --fast:wrapper 新增 `--fast` 旁路(红测:--fast 跳过契约套件、汇总口径一致、默认行为不变)。
- [x] 4. P1b 单一来源:core `--print-external-commands`(红测:清单缺 cat 时受限 PATH 用例失败;两份测试删除硬编码白名单改为解析 core;资产自包含用例过)。
- [x] 5. P2a 钩子:`scripts/hooks/pre-push` + README"本地防护"一节(红测:门禁红时钩子非零阻断)。
- [x] 6. P1a CI:validate.yml 增安装器套件独立步骤(结构断言:步骤存在且不可跳过)。
- [x] 7. P3d 仲裁行:CLAUDE.md、AGENTS.md、资产两入口各加一句(镜像与 mutation 断言保短语)。
- [x] 8. P2b 技能分层 + archive 索引步骤:verify/archive 技能双侧+资产同步更新(短语保全断言)。
- [x] 9. 资产同步:全部随包文件逐字节同步 manifest 覆盖范围。(初版漏同步随包契约测试副本,任务级审查 F1 揭穿;同步后 F2 揭示目标侧计数断言与锁用例需适配,F1-F3/F5 均已修复:钩子去参数透传+索引 100755+带参用例、锁用例 flock skip、目标侧 Ran N 动态统计、README 措辞限定;3aa3879 注记中"仅 1 个环境性失败"系指 main 诊断,worktree 首跑实为 2 失败,以本注记更正)
- [x] 10. 严格 Build 纪律:隔离 worktree、每职责单元 TDD 红绿、任务级审查(manifest freeze/verify)、按职责单元提交。(偏差注记:任务级审查按四职责单元合并为两轮——首轮 f50c710c 中止留 F1-F5,处置后 d8719f82 差异复审全 resolved;T1/T6/T7 的 core 改动同居一文件合并提交)
- [x] 11. Verify 双阶段独立审查(规格符合性→代码质量)+ 主会话 `--require-openspec` 全量终验。(阶段1 PASS@ee79c827、阶段2 PASS@24f2e091,12 finding 全处置见 review-findings.md;终验链 required 门禁 PASS=191 FAIL=0 EXIT=0,完整安装器套件 82 用例仅 1 环境性失败零 error)
- [x] 12. Archive:合并 delta、索引行、知识沉淀、归档后全量复验、`--no-ff` 合回 main、合并结果复跑全量、按授权推送。(delta 已并入两主规格,含 VQ-F1 场景保全;memory 4 新坑+1 处更正、rules/kb/索引行已沉淀;归档后与合并后门禁结果见提交信息)
