模板版本: 1
# 任务清单

- [ ] 1. standard 指纹缓存
  - [ ] 1.1 修改：`scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 复用 fast 缓存逻辑至 standard 层
  - [ ] 1.2 补充契约测试：命中/FAIL 清缓存/输入缺失三场景
  - [ ] 1.3 验证：`bash scripts/validate-workflow.sh --standard` 暖跑第二次命中
  - 预期结果：暖跑行内标注指纹来源，PASS 计数与冷跑一致

- [ ] 2. 校验增量裁剪
  - [ ] 2.1 修改：`scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 按变更文件分类决定检查子集
  - [ ] 2.2 补充契约测试：文档-only 跳过树复制、core 子集、分类外全量
  - [ ] 2.3 验证：`bash scripts/validate-workflow.sh --standard --print-plan` 检查集合符合分类
  - 预期结果：文档-only 变更不再全量 281 项，分类外仍全量

- [ ] 3. 巨型技能拆分
  - [ ] 3.1 修改：`.claude/skills/systematic-debugging/`、`.claude/skills/writing-skills/` + `.codex/skills/` 镜像拆核心+附录
  - [ ] 3.2 验证：`bash scripts/validate-workflow.sh --fast` 镜像 byte-identical 通过
  - 预期结果：两技能核心 ≤80 行，双树镜像一致

- [ ] 4. 内存与索引瘦身
  - [ ] 4.1 修改：`.ai/memory/workflow.md` 轮转至 30 条分模块文件；`.ai/rules/index.md` 关键词截断完整表入附录
  - [ ] 4.2 验证：`bash scripts/validate-workflow.sh --fast` + 统计续传行数
  - 预期结果：新会话上下文 <350 行，路由测试通过

- [ ] 5. 续传摘要命令
  - [ ] 5.1 修改：`scripts/new-openspec-change.py` 新增摘要子命令
  - [ ] 5.2 验证：`python3 scripts/new-openspec-change.py summary openspec/changes/workflow-tiers-incremental-cache-context`
  - 预期结果：一行输出状态/未勾任务/commit/指纹且可独立解析

- [ ] 6. 待验证变更收尾归档
  - [ ] 6.1 操作：确认 `openspec/changes/layered-validation-agent-gating-output-metrics/` 归档证据已持久化后归档并精确清理 `.ai-local/reviews/layered-validation-agent-gating-output-metrics/`
  - [ ] 6.2 验证：`bash scripts/validate-workflow.sh --archive-light` + `git status --porcelain -- .ai-local/reviews`
  - 预期结果：归档完成，残留 reviews 目录仅剩活跃变更

- [ ] 7. 全量终验
  - [ ] 7.1 验证：`bash scripts/validate-workflow.sh --require-openspec`
  - [ ] 7.2 验证：`openspec validate workflow-tiers-incremental-cache-context --strict --no-interactive`
  - 预期结果：全绿，无 FAIL/SKIP

## 本地整合策略

- 分支/worktree：默认 feature 分支 `feat/workflow-tiers-incremental-cache-context`，无需隔离 worktree
- 提交边界：standard 缓存+裁剪 / 技能拆分+索引瘦身 / 摘要+收尾归档三组职责单元独立提交
- 外部副作用授权：不推送、不合并 main、不删除归档外数据；清理仅限已持久化证据的精确子路径
- 手工测试编译输出：默认不适用；若用手工 javac/java，输出仅位于 /tmp
