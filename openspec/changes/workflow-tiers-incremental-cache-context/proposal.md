模板版本: 1
模式: 标准
状态: 待确认计划

# 工作流提速增量缓存上下文优化

## Why

项目已完成两轮提速（指纹缓存进 `--fast`、分层验证、代理门控），但实测 `--fast` 冷跑 25.3s/281 PASS、暖跑 1.9s，契约套件 188 例 146s；新会话续传需重读 `AGENTS/CLAUDE/index/review/archive/memory ≈ 488 行`，`systematic-debugging 283 + writing-skills 280` 占技能总量 31%，`layered-validation…` 严格变更停在待验证、`reviews/` 残留 3 目录 ~144K。在不改变门禁通过/失败与必需执行的前提下，剩余提速在增量粒度与上下文成本。

## What Changes

- `--standard` 复用 `--fast` 指纹缓存模式：仅缓存 PASS，FAIL/SKIP 删除缓存，输入缺失不读写，cache key = 检查命令 + core 自身 + 声明输入内容指纹
- 校验增量裁剪：按变更文件分类决定检查子集（文档变更跳过契约树复制；core 脚本变更跑对应单测子集），分类外仍全量
- 巨型技能拆分：`systematic-debugging`、`writing-skills` 拆为核心 80 行 + 按需附录，决策链默认只读核心
- 内存/索引瘦身：`memory/workflow.md` 轮转至最近 30 条分模块文件；`.ai/rules/index.md` 关键词截断，完整表放附录
- 续传摘要命令：扩展 `new-openspec-change.py check` 同风新增摘要（一行输出状态 + 未勾任务 + 基线 commit + 规则指纹）
- 收尾卡点：归档 `layered-validation-agent-gating-output-metrics` 待验证变更（确认其 manifest 已持久化后精确清理 `reviews/<change>/` 子路径）

## Impact

- 构建/验证：`scripts/validate-workflow.sh` wrapper、core 缓存逻辑、技能双树镜像、安装资产
- 风险：缓存失配或分类误裁会假绿；必须用 FAIL 清缓存、缺失 fail-open 拦截、分类外全量回退兜底
- 流程分级：本变更保持门禁通过/失败、必需执行及证据契约不变，属工具实现与性能优化，走标准模式；不触发严格四件套

## Scope

### Included

- `scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 及契约测试增量缓存与裁剪
- `.claude/skills/systematic-debugging/`、`.claude/skills/writing-skills/` + `.codex/skills/` 镜像拆分
- `.ai/memory/` 轮转、`.ai/rules/index.md` 瘦身、`scripts/new-openspec-change.py` 摘要命令
- `openspec/changes/layered-validation-agent-gating-output-metrics/` 归档收尾

### Excluded

- 不修改模式路由、确认条件、状态推进、审查层数、归档门禁等门禁语义
- 不新增输出状态、代理类型、证据口径或业务运行时/公开 API/Schema

## Acceptance

- `--standard` 暖跑命中复用且行内标注指纹来源；FAIL/SKIP 不命中缓存；输入缺失只执行不读写
- 文档-only 变更裁剪跳过契约树复制；core 变更跑对应子集；分类外全量；裁剪规则命中全覆盖
- 两技能核心 ≤80 行，附录按需加载；双树镜像 byte-identical
- 新会话上下文 <350 行；摘要命令输出一行可独立解析
- 归档变更 `layered-validation-agent-gating-output-metrics` 已归档，`reviews/` 残留清理

## Unverified scope

目标契约测试、fast/standard/required、OpenSpec strict、diff 校验待 Build 后现跑记录。

## Residual risk

缓存指纹遗漏新输入源会导致假命中；裁剪漏分类会漏检。均用 fail-open 缺失拦截与分类外全量兜底。
