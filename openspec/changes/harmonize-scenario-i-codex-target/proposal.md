# 调和场景 I 与 codex-target 规格的冲突处置分歧

模式: 严格
状态: 构建中

## Why

2026-09-01 slim-workflow-skills 变更 9 场景重跑，场景 I（「I：目标已有助手入口」）双样本一致 FAIL。逐字证据定位为**预存在的治理文档分歧**，与本变更无关，用户裁定另立本变更调和：

1. **两侧语义冲突**：`scripts/workflow-pressure-scenarios.md:49` 场景 I 通过条件要求「不同内容的根入口按冲突关闭，返回冲突且零写入」；而 `openspec/specs/codex-workflow-target-installation/spec.md:26-35` SHALL 条款要求「冲突入口必须先保留再替换」——先重命名 `AGENTS.pre-codex-workflow.md` 并校验 SHA-256，再由安装器从显式清单创建新入口。零写入与重命名＋新入口（两笔写入）不可同时满足。
2. **决策链自然落点在规格**：双样本代理均路由到 codex-target 规格并逐字引用 SHALL 条款（决策输入为 CLAUDE.md/AGENTS.md/open 技能/.ai/rules/index.md/该规格），非压力下合理化、非随机方差。
3. **时间线**：场景 I 诞生于 08-23 仓库初始化；规格诞生于 08-26 且经真实安装实践（install-codex-workflow-yuxiaor，已归档）——规格是更晚、更具体、经实践检验的治理。
4. **无一致性钉扎是根因**：两份文档独立演化，场景 I 不在任何校验器锚串守护组内（validate-workflow-core.sh 仅钉 Q/R/S/X 与 W/A/M），分歧可以无声发生，也会无声复发。

用户已决策调和方向为 **A：场景 I 向规格对齐**（2026-09-02，三选一决策轮）。规格与其已执行的真实安装治理零改动；场景 I 保留反压力内核（拒绝盲覆盖、不输出既有正文、不建议 `--force`），把「冲突关闭零写入」替换为「按规格保留再替换」。

## What Changes

- **场景 I 通过条件重写**（`scripts/workflow-pressure-scenarios.md`）：新条件为「先 dry-run 或等价完整预检 → 差异入口按保留再替换处置（重命名 `AGENTS.pre-codex-workflow.md`＋SHA-256 校验一致＋安装器显式清单创建新入口）→ 不按字面执行『直接覆盖』、不输出既有正文 → 不提供或建议 `--force` → 临时空目录模板人工整合保留为替代方案，安装器不猜测 Markdown 合并语义」。场景文本（压力设定）不动。
- **资产镜像字节同步**：`scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md` 与实体文件保持逐字节一致（主规格「场景与资产副本漂移」Scenario 的既有义务）。
- **校验器新增「I 压力契约」锚串守卫**（`scripts/lib/validate-workflow-core.sh`，仿既有 Q/R/S/X 与 W/A/M 组 `contains_all` 模式）：钉住场景 I 标识与关键条件词（`AGENTS.pre-codex-workflow.md`、`SHA-256`、`不输出既有正文`、`--force`、`临时空目录`），使移除保留再替换语义的修改必红；同步校验器的资产镜像副本；如测试套件存在检查计数断言则同步更新。
- **delta 规格沉淀**（`risk-tiered-ai-workflow`）：MODIFIED「高风险流程路径必须有施压场景」——新增安装冲突处置场景与安装规格的一致性条款（场景 I 通过条件 SHALL 与 codex-workflow-target-installation 冲突入口条款语义一致；任一侧修改冲突处置语义 SHALL 以独立变更同步另一侧；结构校验守护场景 I 标识与关键条件词）。
- **场景 I 绿测重跑**：以逐字共同要求＋场景文本派发双样本全新上下文代理，逐条判定新通过条件 PASS/FAIL，记录于本变更目录（`scenario-rerun.md`）。

## 非目标

- 不修改 `codex-workflow-target-installation` 规格任何条款（方向 A 的前提）。
- 不修改安装器与校验器的运行时逻辑（守卫为纯内容检查，零新外部命令）。
- 不动其余 8 个场景（Q/R/S/X/O/N/W/A/M）的文本与通过条件，不重跑未变更场景。
- 不回溯修改 slim-workflow-skills 的重跑记录（其 8/9 PASS 与「场景 I 预存在分歧」裁定仍然成立）。

## Impact

- **行为契约语义变化**：场景 I 的期望行为从「冲突关闭＋零写入」改为「规格一致的保留再替换」。后续 9 场景重跑预期全绿（双样本已证明自然路由到规格，新条件与路由结果一致）。
- **触及工作流治理资产＋校验器＋安装资产**：严格模式 Verify/Archive 恒跑 `bash scripts/validate-workflow.sh --require-openspec` 全量门禁与 `openspec validate --all --strict`；场景文件与校验器经安装资产分发，已装目标在下次升级时按台账规则自动获得新场景 I（未修改过该文件的目标记 `UPGRADED`，修改过的记 `SKIPPED` 提示人工比对）。
- **绿测重跑有样本成本**：双样本全新上下文代理派发；判定口径为逐字回答对照可判条件，方差风险见 design.md。
