# 实现计划：扩展项目上下文与验证证据复用

## 全局约束

- 基线：`main`；实现分支/worktree：`feature/extend-project-context-and-evidence-reuse`。
- 源仓库 `.ai/kb/projects/registry.json` 必须保持 `{"schema_version":1,"projects":[]}`。
- 不复制 `/media/shitou/data2/ai-pms` 的项目名、服务名、业务词、源码路径、私有地址或团队事实。
- `project_facts.py` 保持只读：不联网、不 clone、不写 workspace、不执行 registry 声明的 build/test 命令。
- 运行时行为按红-绿-重构；文档/模板用内容契约、路径校验、manifest、镜像和 diff 校验。
- 所有随包复用资产必须与活动源字节同步；新增文件必须进入安装 manifest。
- 不 push、不创建 PR、不删除未合并工作。

## 任务 1：Registry 与 project-context 红测

- Modify: `.ai/tools/tests/test_project_facts.py`
- 新增 `test_project_context_outputs_dependencies_and_verification`：alpha 依赖 beta，声明 build/test 命令、证据路径和 `verified_commit`，断言 `DEPENDENCY`、`VERIFICATION` 与 `current`。
- 新增 `test_project_context_reports_drifted_and_unavailable_verified_commit`：HEAD 变化输出 `drifted`；项目缺失或非 Git 输出 `unavailable`。
- 新增 `test_registry_rejects_invalid_dependencies_and_verification`：覆盖未知/自/重复/循环依赖、空或多行命令、证据路径非法或缺失、commit 非 40/64 位十六进制。
- 扩展只读性测试，确认 `project-context` 不改变文件内容和 mtime。
- 命令：`python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_project_facts.py'`
- 预期：新增测试先失败，失败原因为 `dependencies` / `verification` 尚未被解析和输出。

## 任务 2：实现 registry 契约与 project-context 输出

- Modify: `.ai/tools/project_facts.py`
- Registry 契约：
  - 可选 `dependencies: list[str]`；
  - 可选 `verification`，字段为 `build_command`、`test_command`、`evidence`、`verified_commit`；
  - 字符串必须非空单行；
  - evidence 必须是相对 `.ai/` 的存在文件，禁止绝对路径与 `..`；
  - verified_commit 必须是 40/64 位十六进制；
  - 依赖必须已登记、非自身、不重复且无循环。
- 输出契约：
  - `DEPENDENCY\t<project>`；
  - `VERIFICATION\tbuild|test\t<command>`；
  - `VERIFICATION\tevidence\t<relative-path>`；
  - `VERIFICATION\tverified_commit\t<status>\t<declared>`；
  - status 只允许 `current`、`drifted`、`unavailable`。
- Git freshness：
  - 仅在项目存在且为 Git 工作树时执行只读 `git rev-parse HEAD`；
  - 失败、非 Git 或缺失输出 `unavailable`；
  - 不修改 index 或工作区。
- 命令：`python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_project_facts.py'`
- 预期：新增测试和既有事实工具测试全部通过。

## 任务 3：项目卡与验证证据模板

- Create: `.ai/kb/projects/_template.md`
  - frontmatter 包含 project、kind、domains、last_verified、verified_commit、sources；
  - 正文包含职责/非职责、高频入口、跨仓库关系、搜索锚点、验证入口、证据基线、定位特例；
  - 只使用非业务占位符。
- Create: `.ai/kb/verification-evidence.md`
  - 定义证据字段、等价复用条件、失效条件、脱敏要求和 OpenSpec/新鲜验证边界。
- 校验：模板不含 ai-pms 业务 token，链接有效，`git diff --check` 通过。

## 任务 4：共享文档与技能路由

- Modify: `.ai/kb/projects/README.md`、`.ai/kb/README.md`、`.ai/README.md`、`.ai/tools/README.md`、`.ai/rules/index.md`、双侧 `verification/SKILL.md`。
- 内容：
  - registry 新字段契约和示例；
  - project-context 新输出解释；
  - verified_commit 只证明基线一致，不证明当前任务通过；
  - verification 技能读取证据契约并遵守等价复用/失效边界。
- 校验：双侧技能镜像一致，文档链接有效，源 registry 仍为空。

## 任务 5：规格、安装资产与 manifest

- Modify: `openspec/specs/shared-ai-workflow-infrastructure/spec.md`、`scripts/ai-workflow-assets/manifest.json`、`scripts/ai-workflow-assets/shared/**`、installer/workflow 测试。
- 要求：
  - `_template.md` 与 `verification-evidence.md` 进入 shared manifest；
  - 复用文件源/资产字节同步；
  - installer 枚举所有物理资产并检查 mode；
  - workflow 测试覆盖证据复用边界和源 registry 空白。
- 命令：
  - `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow.PortableAssetContentTests`
  - `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow.PortableAssetManifestTests`

## 任务 6：完整验证

1. `python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'`
2. `python3 -B -m unittest -v scripts.tests.test_validate_workflow`
3. `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`
4. `python3 -B -m unittest -v scripts.tests.test_install_workflow`
5. `bash scripts/validate-workflow.sh --require-openspec`
6. `openspec validate --all --strict --no-interactive`
7. `git diff --check`

## 任务 7：任务级审查

- 审查单元 1：registry 依赖/verification 边界、Git freshness 与只读性。
- 审查单元 2：验证证据复用不削弱 OpenSpec 状态、新鲜验证和安装知识分层。
- reviewer 读取前和结论前运行 `review_manifest.py verify`；Critical/Important 全部关闭后进入 Verify。

## 任务 8：严格 Verify 双阶段与归档

- 规格符合性 reviewer 逐条核对 delta、Non-Goals、模板、registry 契约与任务。
- 代码质量 reviewer 审查正确性、边界、安全、测试有效性、资产同步和维护成本。
- 主会话终验 required 门禁与 OpenSpec strict。
- 全部通过后合并主规格、沉淀知识、归档、本地 `--no-ff` 合回 `main` 并复验。
