# 任务清单

- [ ] 1. 更新项目 registry
  - [ ] 1.1 修改 `.ai/kb/projects/registry.json`，在 `projects` 数组追加 `yuxiaor-e-signature`。
  - [ ] 1.2 按权威源码登记 `search_roots`：README、根 POM、构建脚本、`yuxiaor-e-signature-api/src/main`、`yuxiaor-e-sign-base/src/main`、`yuxiaor-e-sign-bo/src/main`、`yuxiaor-e-sign-junzi/src/main`、`yuxiaor-e-sign-server/src/main`。
  - [ ] 1.3 登记 application：server/module 为 `yuxiaor-e-sign-server`，main class 为 `com.yuxiaor.pms.esign.YuxiaorEsignApplication`，source path 为 `yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/YuxiaorEsignApplication.java`。
  - [ ] 1.4 声明 `business_terms`：电子签署、实名认证、刷脸认证、合同签署、电子签署回调、渠道路由、电子签署账号、E签宝、君子签；每条 source path 指向对应权威源码。
  - [ ] 1.5 声明展示用 build/test 命令：`cd yuxiaor-e-signature && ./build.sh` 与 `cd yuxiaor-e-signature && mvn -s settings-work.xml -T2C test -P dev,env-actuator`；不声明 verified_commit。

- [ ] 2. 新建项目卡并更新路由索引
  - [ ] 2.1 从 `_template.md` 结构创建 `.ai/kb/projects/yuxiaor-e-signature.md`。
  - [ ] 2.2 记录项目与模块职责：server 启动、E签宝渠道、君子签废弃渠道、基础持久化/配置、对外 API/Feign。
  - [ ] 2.3 记录高频入口、跨仓库关系、搜索锚点、验证入口和未验证范围。
  - [ ] 2.4 在 `.ai/rules/index.md` 模块表中新增“电子签署服务”行，覆盖项目卡、registry、业务词和模块关键词。

- [ ] 3. 验证登记与 OpenSpec
  - [ ] 3.1 运行 `python3 -m json.tool .ai/kb/projects/registry.json`，预期 JSON 可解析。
  - [ ] 3.2 运行 `python3 .ai/tools/project_facts.py project-context --workspace "$PWD" --project yuxiaor-e-signature`，预期输出 PROJECT/APPLICATION/VERIFICATION 且状态 available。
  - [ ] 3.3 运行 `python3 .ai/tools/project_facts.py server-registry --workspace "$PWD" --server yuxiaor-e-sign-server`，预期唯一匹配。
  - [ ] 3.4 运行 `python3 .ai/tools/project_facts.py business-terms --workspace "$PWD" --text 君子签 --exact --limit 20`，预期返回电子签署项目与源码路径。
  - [ ] 3.5 运行 `python3 .ai/tools/project_facts.py workspace-search --workspace "$PWD" --project yuxiaor-e-signature --text EsignatureService --limit 20`，预期返回权威源码路径。
  - [ ] 3.6 运行 `openspec validate register-yuxiaor-e-signature --strict --no-interactive`，预期 valid。
  - [ ] 3.7 运行 `bash scripts/validate-workflow.sh --fast`，预期无 FAIL；如 OpenSpec CLI 缺失按工具契约记录 SKIP。

## 本地整合策略

- 在根仓库现有 `feature/extract-esign-ddd-module` 上新建本变更三件套；实施前等待用户唯一确认。
- 仅修改根仓库 `.ai/`、`.ai/kb/projects/registry.json` 和 OpenSpec 变更目录；不触碰 `yuxiaor-e-signature`、`yuxiaor-pms` 或用户本地未提交文件。
- 实施后不自动提交；由用户审阅 diff 后决定是否提交。
