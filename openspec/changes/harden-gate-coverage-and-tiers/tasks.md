# Tasks(范围清单;可执行细化计划由 Design 阶段产出 openspec/plan)

- [ ] 1. 规格确认后由 Design 产出零上下文可执行计划(`openspec/plan/harden-gate-coverage-and-tiers.md`),第二次实施前确认后进入 Build。
- [x] 2. P2d 并发锁:wrapper best-effort flock(红测:两并发实例第二例非零;无 flock 降级提示)。
- [x] 3. P2b --fast:wrapper 新增 `--fast` 旁路(红测:--fast 跳过契约套件、汇总口径一致、默认行为不变)。
- [x] 4. P1b 单一来源:core `--print-external-commands`(红测:清单缺 cat 时受限 PATH 用例失败;两份测试删除硬编码白名单改为解析 core;资产自包含用例过)。
- [x] 5. P2a 钩子:`scripts/hooks/pre-push` + README"本地防护"一节(红测:门禁红时钩子非零阻断)。
- [x] 6. P1a CI:validate.yml 增安装器套件独立步骤(结构断言:步骤存在且不可跳过)。
- [x] 7. P3d 仲裁行:CLAUDE.md、AGENTS.md、资产两入口各加一句(镜像与 mutation 断言保短语)。
- [x] 8. P2b 技能分层 + archive 索引步骤:verify/archive 技能双侧+资产同步更新(短语保全断言)。
- [x] 9. 资产同步:全部随包文件逐字节同步 manifest 覆盖范围。
- [ ] 10. 严格 Build 纪律:隔离 worktree、每职责单元 TDD 红绿、任务级审查(manifest freeze/verify)、按职责单元提交。
- [ ] 11. Verify 双阶段独立审查(规格符合性→代码质量)+ 主会话 `--require-openspec` 全量终验。
- [ ] 12. Archive:合并 delta、索引行、知识沉淀、归档后全量复验、`--no-ff` 合回 main、合并结果复跑全量、按授权推送。
