# Tasks(范围清单;零上下文细化计划由 Design 阶段产出)

- [ ] 1. 规格确认后由 Design 产出 `openspec/plan/remove-stale-workflow-system-spec.md`,第二次实施前确认后进入 Build。
- [ ] 2. 严格原子落点:feature 分支提交四件套+计划(状态:构建中)→ 切回 main → 挂隔离 worktree → 补 SDD 占位。
- [ ] 3. 删除前证据固化:记录 `openspec validate --all --strict` 现状(12 规格)与全仓引用扫描输出为零。
- [ ] 4. 删除 `openspec/specs/workflow-system/spec.md` 及目录;现跑 `openspec validate <变更名> --strict` 与 `--all --strict`(11 规格)通过。
- [ ] 5. 门禁:`bash scripts/validate-workflow.sh --fast` 秒级核对 + required 全量现跑全绿(治理资产变更,Verify 不降层)。
- [ ] 6. 任务级审查:freeze manifest + 独立 reviewer 核对逐条映射与零引用。
- [ ] 7. Verify 双阶段(规格符合性→代码质量)+ finding 闭环 + `--require-openspec` 终验。
- [ ] 8. Archive:REMOVED 落地(主规格文件删除)、memory 新坑沉淀(如有)、索引行、归档后 required 门禁、`--no-ff` 合回 main、合并结果复跑、按授权推送。
