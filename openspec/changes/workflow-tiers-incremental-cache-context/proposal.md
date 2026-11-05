模板版本: 1
模式: 标准
状态: 构建中

# 工作流提速增量缓存上下文优化

## Why

项目已完成两轮提速（指纹缓存进 `--fast`、分层验证、代理门控），但实测 `--fast` 冷跑 25.3s/281 PASS、暖跑 1.9s，契约套件 188 例 146s；新会话续传需重读 `AGENTS/CLAUDE/index/review/archive/memory ≈ 488 行`，`systematic-debugging 283 + writing-skills 280` 占技能总量 31%，`layered-validation…` 严格变更停在待验证、`reviews/` 残留 3 目录 ~144K。在不改变门禁通过/失败与必需执行的前提下，剩余提速在增量粒度与上下文成本。

## What Changes

- `--standard` 复用 `--fast` 指纹缓存模式：仅缓存 PASS，FAIL/SKIP 删除缓存，输入缺失不读写，cache key = 检查命令 + core 自身 + 声明输入内容指纹
- 校验增量裁剪：`WORKFLOW_STANDARD_BASE` 显式基线下按变更文件分类决定契约套件执行（无工作流资产变更则裁剪；git 缺失/diff 失败/未跟踪工作流资产/升级层级一律全量 fail-closed），并新增 `--print-plan` 只读计划输出
- 内存轮转：`memory/workflow.md` 限制最近 30 条，超出移入 `workflow-archive.md`，配套 gitignore 白名单与 README 轮转规则
- 续传摘要命令：`new-openspec-change.py summary` 一行输出状态 + 未勾任务 + 基线 commit + 规则指纹

## Impact

- 构建/验证：`scripts/validate-workflow.sh` wrapper、core 缓存逻辑、技能双树镜像、安装资产
- 风险：缓存失配或分类误裁会假绿；必须用 FAIL 清缓存、缺失 fail-open 拦截、分类外全量回退兜底
- 流程分级：本变更保持门禁通过/失败、必需执行及证据契约不变，属工具实现与性能优化，走标准模式；不触发严格四件套

## Scope

### Included

- `scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 及契约测试增量缓存与裁剪
- `.ai/memory/` 轮转、`.gitignore` 白名单、`scripts/new-openspec-change.py` 摘要命令

### Excluded

- 不修改模式路由、确认条件、状态推进、审查层数、归档门禁等门禁语义
- 技能拆分与 index.md 关键词截断经用户确认放弃（2026-11-05）：技能为触发式加载无主路径收益；关键词列即路由表，截断有路由降级风险
- `layered-validation-agent-gating-output-metrics` 的 Verify 与归档移出范围，随后单独处理
- 不新增输出状态、代理类型、证据口径或业务运行时/公开 API/Schema

## Acceptance

- `--standard` 暖跑命中复用且行内标注指纹来源；FAIL/SKIP 不命中缓存；输入缺失只执行不读写
- 显式基线下无工作流资产变更裁剪契约套件；git 缺失/diff 失败/未跟踪工作流资产/升级层级全量；`--print-plan` 输出可审计分类
- memory 主文件 ≤30 条（实测 30 条/116 行），新会话上下文 <350 行（实测 318 行）
- 摘要命令输出一行可独立解析（change/mode/status/unchecked/head/rules）

## Unverified scope

目标契约测试、fast 已现跑通过；`--standard` 暖跑计数一致、required 门禁与 OpenSpec strict 在终验链现跑后记录。

## Residual risk

缓存指纹遗漏新输入源会导致假命中；裁剪漏分类会漏检。均用 fail-open 缺失拦截、未跟踪资产全量与分类外全量兜底。裁剪仅在调用方显式提供 `WORKFLOW_STANDARD_BASE` 时生效，默认行为不变。
