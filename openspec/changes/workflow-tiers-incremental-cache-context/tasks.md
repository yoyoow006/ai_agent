模板版本: 1
# 任务清单

- [ ] 1. standard 指纹缓存
  - [x] 1.1 修改：`scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 复用 fast 缓存逻辑至 standard 层
  - [x] 1.2 补充契约测试：命中/FAIL 清缓存/输入缺失三场景
  - [ ] 1.3 验证：`bash scripts/validate-workflow.sh --standard` 暖跑第二次命中
  - 预期结果：暖跑行内标注指纹来源，PASS 计数与冷跑一致

- [ ] 2. 校验增量裁剪
  - [x] 2.1 修改：`scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh` 按变更文件分类决定检查子集
  - [x] 2.2 补充契约测试：文档-only 跳过树复制、core 子集、分类外全量
  - [x] 2.3 验证：`bash scripts/validate-workflow.sh --standard --print-plan` 检查集合符合分类
  - 预期结果：文档-only 变更不再全量 281 项，分类外仍全量

- [ ] 3. 内存轮转
  - [x] 3.1 修改：`.ai/memory/workflow.md` 轮转至最近 30 条，超出部分移入 `workflow-archive.md`；`.gitignore` 白名单与 `.ai/memory/README.md` 轮转规则
  - [x] 3.2 验证：`bash scripts/validate-workflow.sh --fast` + 统计续传行数
  - 预期结果：新会话上下文 <350 行（实测 318 行）

- [ ] 4. 续传摘要命令
  - [x] 4.1 修改：`scripts/new-openspec-change.py` 新增摘要子命令
  - [x] 4.2 验证：`python3 scripts/new-openspec-change.py summary openspec/changes/workflow-tiers-incremental-cache-context`
  - 预期结果：一行输出状态/未勾任务/commit/指纹且可独立解析

- [ ] 5. 全量终验
  - [ ] 5.1 验证：`bash scripts/validate-workflow.sh --require-openspec`
  - [ ] 5.2 验证：`openspec validate workflow-tiers-incremental-cache-context --strict --no-interactive`
  - 预期结果：全绿，无 FAIL/SKIP

## 已移除任务（2026-11-05 用户确认）

- 技能拆分（原任务 3）：技能为触发式加载，主路径不读；拆分需同步 manifest/资产/规格锚点，成本高收益趋零。
- index.md 关键词截断（原 4.1 后半）：关键词列即路由表，截断有路由降级风险；<350 行已由内存轮转单独达成。
- layered-validation 变更归档收尾（原任务 6）：该严格变更的 Verify 双阶段+归档移出本范围，随后单独处理。

## 本地整合策略

- 分支/worktree：默认 feature 分支 `feat/workflow-tiers-incremental-cache-context`，无需隔离 worktree
- 提交边界：standard 缓存+裁剪 / 内存轮转+摘要命令 / 范围收缩同步 三个职责单元独立提交
- 外部副作用授权：不推送、不合并 main、不删除归档外数据
- 手工测试编译输出：默认不适用；若用手工 javac/java，输出仅位于 /tmp
