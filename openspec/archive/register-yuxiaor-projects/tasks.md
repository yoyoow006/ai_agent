# Tasks

- [x] 从三个项目的 README、POM、启动类和源码目录复核登记事实。
- [x] 更新 `.ai/kb/projects/registry.json`，确保 JSON 可解析、路径存在、依赖只引用已登记项目。
- [x] 新增三个项目卡并写入事实来源、职责边界、入口和验证命令，不填写未经执行的验证证据。
- [x] 更新 `.ai/rules/index.md` 项目登记路由关键词。
- [x] 运行 `python3 -B -m json.tool .ai/kb/projects/registry.json`。
- [x] 运行 `python3 -B -m unittest discover -v -s .ai/tools/tests -p test_project_facts.py`，并检查 `git diff --check` 与完整 diff。

验证证据：事实工具测试 30/30 通过；`project-context` 与 `business-terms` 查询通过；仓库快速门禁 PASS=125、FAIL=0、SKIP=1；manifest `1b77a9ff69c5ab12d02360ad34fb474822404a34ed8ea8f77f32ca6664db6aa5` 为 VALID；comparison base 为根仓 `HEAD` 及三个项目当前 HEAD；未验证 Maven 构建/测试。

本地整合策略：主工作区直接整合本次知识登记；不创建 worktree、不提交 Git、不执行外部发布动作。
