模式: 严格
状态: 待验证

# 优化静态规则缓存、分层验证与标准产物模板

## Why

当前工作流校验器已经有 `--fast` 输入指纹缓存、默认全量门禁和
`--require-openspec` 强制门禁，但缓存范围、失效规则和输出契约分散在
shell 实现中；验证层级也主要依赖组合参数，维护者不易判断某次变更应该
跑哪一层。OpenSpec 变更产物则由各次手工编写，容易遗漏模式/状态、范围、
场景、命令证据和本地整合策略。

用户要求先优化三项：静态规则缓存、分层验证策略、标准产物模板化。该变更
会调整工作流治理、校验器行为和 OpenSpec 入口，按严格模式处理。

## What Changes

- 建立只读、内容寻址的静态规则快照缓存，用于复用规则/技能/共享规范的
  解析结果；缓存记录包含 schema、输入清单哈希、实现版本、生成时间和
  PASS 来源，缺失、损坏、输入漂移、命令漂移或非 PASS 一律重新计算，
  不影响 `--require-openspec` 的强制实际执行。
- 将验证入口明确为可判定的 fast、standard、required 三层，保留现有
  参数兼容；每层声明覆盖范围、允许的 SKIP、缓存使用规则和升级条件，
  统一输出层级/来源/汇总，避免把缓存命中误作第四种状态。
- 提供标准 OpenSpec 产物模板和只读生成/预检入口，覆盖
  `proposal.md`、delta `spec.md`、`tasks.md`，并为有独立设计决策时的
  `design.md` 提供条件模板；生成结果带必需字段、WHEN/THEN 场景、精确
  命令和本地整合策略槽位，校验器拒绝未替换占位符和缺失结构。
- 将上述缓存、验证层级和模板契约加入自动化回归；同步双助手入口、共享
  规则索引、随包资产和 OpenSpec 规格，保持唯一状态真源和镜像语义。

## Scope

### Included

- `scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh`及
  其契约测试中的缓存与验证层级实现。
- 新增模板/生成或预检工具、模板契约测试及必要的随包资产登记。
- `AGENTS.md`、`.codex/README.md`、`.codex/skills/`、共享规则/知识和
  `openspec/specs/` 中与三项能力直接相关的语义同步。

### Excluded

- 不改变业务服务运行时、API/Schema、数据库、外部发布或远程操作。
- 不把本地缓存、manifest 或生成日志作为 OpenSpec 状态真源。
- 不自动迁移或改写现有历史变更产物；仅提供兼容模板和新入口。

## Assumptions requiring confirmation

1. 静态规则缓存默认写入 `.ai-local/rules-cache/`，继续由 `.gitignore`
   忽略；`--require-openspec` 和默认全量门禁不读取该缓存。
2. 三层入口采用 `--fast`、默认 `standard`、`--require-openspec` 的兼容
   语义，并新增显式诊断/预检能力，而不删除现有参数。
3. 模板生成只创建本地 OpenSpec 文件，不自动创建分支、提交、worktree 或
   修改用户已有文件；目标目录存在内容时先失败并输出可操作原因。

## Acceptance

- 静态规则输入未变化时可透明命中缓存；任一输入、命令、实现、schema 或
  记录状态变化均实际重算，损坏/失败记录不会假绿。
- fast、standard、required 三层的覆盖矩阵、退出码、PASS/FAIL/SKIP 和
  升级条件均有测试；required 不读取或写入缓存。
- 从模板生成的标准三件套可通过结构校验；缺失字段、空场景、占位符、
  多行命令或不完整本地整合策略会失败并定位文件。
- 相关工作流校验、模板契约、OpenSpec 严格校验全部通过，且用户未提交
  文件保持不变。
