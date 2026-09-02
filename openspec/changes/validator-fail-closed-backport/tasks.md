# Tasks

- [ ] 1.1 第一次确认四件套范围、非目标与验收标准（当前待确认）。
- [ ] 1.2 Design 阶段产出独立实现计划 `openspec/plan/validator-fail-closed-backport.md`（精确到函数级改动点、测试适配清单与验证命令），第二次确认后才实施。
- [ ] 1.3 wrapper 跳过计数 fail-closed：`contract_skips` 显式读取 grep 退出码（0/1 之外判 FAIL）并校验非负整数，解析失败计 FAIL 且按 0 继续汇总。
- [ ] 1.4 wrapper 明细渲染 fail-closed：跳过明细改用 `sed -n` 单步渲染并检查退出码，失败计 FAIL；顶层 SKIP 计数与正常明细输出不变。
- [ ] 1.5 core `retired_tool_names_absent`：grep 退出码三态 case（0 命中判失败、1 无匹配继续、其余判失败）。
- [ ] 1.6 core `archive_index_ok`：glob 枚举（dotglob/nullglob 保存恢复）+ 符号链接拒绝 + mktemp 中转与 printf/sort/sed/awk/cmp 逐步退出码检查；空归档 vacuous 通过语义保持。
- [ ] 1.7 移植适配 6 个 fail-closed 回归测试：非 GNU find、归档目录符号链接（真实/隐藏/仓内/外部/dangling）、sort 错误、跳过计数 grep 错误、明细渲染 sed 错误、废弃名扫描错误。
- [ ] 1.8 资产模板同步：`scripts/ai-workflow-assets/shared/scripts/` 下 core、wrapper、tests 三份镜像与运行副本逐字节一致。
- [ ] 1.9 全量验证：`python3 -B -m unittest scripts.tests.test_validate_workflow` 全绿；`bash scripts/validate-workflow.sh` 全量门禁无新增 FAIL；涉及资产树的安装器套件通过（注意 `_run_target` 超时基线，见 memory）。
- [ ] 1.10 Verify 双阶段独立审查（manifest freeze + `review_manifest.py verify`）。
- [ ] 1.11 Archive：合并 delta 到 `shared-ai-workflow-infrastructure` 主规格、更新归档索引、回流结论沉淀 `.ai/memory/workflow.md`。
