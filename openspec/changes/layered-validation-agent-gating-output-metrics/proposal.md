模式: 严格
状态: 待验证

# 验证分层、代理门控、输出协议与轻量度量

## Why

上一项变更已落地缓存、fast/standard/required 入口和 OpenSpec 模板，但验证仍主要由 wrapper 顺序编排，代理使用边界散落在技能文字中，输出缺少稳定机器协议，运行效果也没有统一的低成本指标。维护者难以回答“这一轮到底跑了什么、为什么派代理、结果是否改善”。

## What Changes

- 将验证入口改为显式分层执行计划；失败时停止后续依赖层。
- 收紧代理调用条件：仅独立边界、角色匹配、可执行验收且无共享写入冲突时允许派发。
- 增加兼容的人类汇总与可选 JSON Lines 诊断输出。
- 增加可丢弃的本地轻量度量，不将指标作为门禁或状态真源。

## Impact

- 构建/验证：验证计划、代理契约、输出事件和指标记录器需要契约测试与镜像同步。
- 风险：宿主实际代理调用仍由外部调度能力控制，仓库保证入口门控与记录协议。

## Scope

### Included

- `scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 与契约测试。
- `.ai/prompts/agents/`、`.codex/agents/`、相关技能和共享规格。
- `.ai-local/metrics/` 本地指标记录器及 schema 校验。

### Excluded

- 不修改业务运行时、公开 API/Schema、数据库、外部发布或远程操作。
- 不自动派发代理、不上传指标、不输出凭据或源码正文。

## Acceptance

- 分层顺序、升级原因和失败停止均有测试；代理四条件门控拒绝不合格调用。
- 人类输出末行为 `PASS=... FAIL=... SKIP=...`，JSONL 每行可独立解析。
- 指标含 schema、run_id、耗时、结果及代理/缓存计数；写入失败不影响验证。
- 相关契约、OpenSpec strict、镜像检查和 `git diff --check` 通过。

## Unverified scope

目标测试、fast、required、OpenSpec strict 和 diff 校验已运行；完整标准层因 required 升级路径等价由 required 覆盖。

## Residual risk

指标受机器负载影响，仅用于趋势观察；宿主可绕过仓库外部调用入口。
