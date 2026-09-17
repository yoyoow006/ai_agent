# Build 审查与验证记录

## 任务级审查

- 最终任务级 manifest ID：`4fc9b763ec2160cb6a1cbfca575e42a8898bd82048286085ed3a49d8981d9cf7`
- comparison base：`main` / merge-base `c69492ab854fe7faf0c29d667eafb31a6f32a088`
- 审查 HEAD：`d8a11ea`

### 单元 A：工作流语义与验证降级边界

- 初审发现 1 条 Critical、3 条 Important：
  - `A-ARCHIVE-GATE-001` Critical：Archive diff 失败 fail-open、promotion 未把 required 语义传给 core。
  - `A-SPEC-ARCHIVE-001` Important：主规格同时保留旧 Archive 全量规则与新轻量升级规则。
  - `A-SEMANTIC-SYNC-001` Important：Build 技能、overview 与压力场景仍保留旧产物/审查/确认口径。
  - `A-OPENSPEC-IDENTITY-001` Important：活跃变更复用已归档变更名。
- 修复提交：`e7786c4`
- 复审结论：4 条 finding 均 resolved，无新增 Critical/Important。
- 测试适配 delta 复审：`d8a11ea` 仅增加安装目标真实缺件对应的设计性 skip allowlist，无新增 Critical/Important；manifest ID `4fc9b763...d9cf7` 有效。

### 单元 B：业务词查询边界与只读性

- 复审结论：PASS，无 finding。
- 核对范围：声明校验、包含/精确匹配、同义词、项目过滤、分页、零匹配、路径/symlink 边界、敏感正文不输出、只读性、源 registry 空白与安装资产同步。
- `d8a11ea` 相对前审 HEAD 未改变业务词实现文件，先前 PASS 结论继续成立。

## Build 验证

- `python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'`：57 tests，OK。
- `python3 -B -m unittest -v scripts.tests.test_validate_workflow`：197 tests，OK。
- `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`：89 tests，OK。
- `python3 -B -m unittest -v scripts.tests.test_install_workflow`：8 tests，OK。
- `bash scripts/validate-workflow.sh --require-openspec`：PASS=200 FAIL=0 SKIP=0。
- `openspec validate --all --strict --no-interactive`：11 passed，0 failed。
- `git diff --check`：通过。

## finding 状态

- Critical：0 open / 1 resolved。
- Important：0 open / 3 resolved。
- Minor：0 open / 0 total。

## 未验证范围

- 未向全新上下文 Agent 逐字执行 pressure scenarios 行为红/绿测试。
- 未执行真实外部业务项目的业务词登记；源 registry 按知识分层规范保持空数组。
- 未模拟并发替换 registry 或 symlink 的对抗性竞态。

## 残余风险

- `business_terms` 只证明声明式路由，不证明业务词语义与当前源码一致；目标维护者登记时必须从权威源码复核。
- Archive 自动升级依赖调用方提供正确 `WORKFLOW_ARCHIVE_BASE` 与完整 `--archive-files` 分类清单；清单遗漏语义文件时 wrapper 无法推断未列出路径。
