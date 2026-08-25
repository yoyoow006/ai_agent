# 任务

## 1. 红阶段：记录现有 Open 技能的需求理解失败

- [x] 在 `.codex/sdd/improve-open-requirement-discovery/` 创建至少三个压力场景记录：
   - 模糊目标：用户只给出方向，观察是否先查事实、编号提问、给推荐并等待。
   - 事实与决策混淆：观察是否把仓库可回答的问题推给用户。
   - 术语过载：观察是否引用来源请求确定 canonical term。
- [x] 用全新上下文代理按同一提示分别运行基线，逐字保存回答、判定和合理化分类。
- [x] 预期：当前技能缺少稳定的问题形状、事实优先边界和回答落盘契约，至少两个场景判 FAIL。

## 2. 绿阶段：实现双侧技能与结构门禁

- [ ] 修改 `.codex/skills/open/SKILL.md` 与 `.claude/skills/open/SKILL.md`，新增需求理解与追问契约。
- [ ] 同步 `scripts/ai-workflow-assets/codex/.codex/skills/open/SKILL.md` 与 `scripts/ai-workflow-assets/claude/.claude/skills/open/SKILL.md`。
- [ ] 修改活动与资产中的 `scripts/lib/validate-workflow-core.sh`，为双侧 Open 技能检查权威事实优先、编号问题、推荐答案、等待回答和 OpenSpec 落盘契约。
- [ ] 修改活动与资产中的 `scripts/workflow-pressure-scenarios.md`，新增模糊需求场景及通过条件。
- [ ] 复验同一组代理压力场景；预期全部按新契约 PASS，并保存逐字记录。

## 3. 结构与资产验证

- [ ] 运行 `bash scripts/validate-workflow.sh`，预期 `FAIL=0`。
- [ ] 运行 `openspec validate improve-open-requirement-discovery --strict --no-interactive`，预期通过。
- [ ] 运行 `python3 -B -m unittest scripts.tests.test_install_ai_workflow.PortableAssetContentTests.test_reusable_assets_are_byte_synchronized_with_active_sources`，预期通过。
- [ ] 运行 `python3 -B -m unittest scripts.tests.test_validate_workflow`，预期全部通过。
- [ ] 核对完整 diff、四份技能字节一致、没有新增 `CONTEXT.md` 或 ADR 平行状态。

## 4. 严格审查与终验

- [ ] 完成任务级独立审查，记录 finding、处置、未验证范围和残余风险。
- [ ] 完成规格符合性与代码/流程质量两个独立关注面的 Verify 审查。
- [ ] 运行 `bash scripts/validate-workflow.sh --require-openspec`，预期 `FAIL=0` 且 OpenSpec 不 SKIP。
- [ ] 归档 delta 到 `openspec/specs/risk-tiered-ai-workflow/spec.md`，沉淀必要 memory/kb 事实，状态置为`已归档`。
