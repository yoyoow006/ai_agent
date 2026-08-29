# Design

## 关键决策

1. **只拆一个新文件 installer.md,不过度细分**。审计建议即"安装器类占一半,值得拆出";Git/openspec/流程类条目彼此关联紧密(治理规则互相引用),再拆 git.md 等只会增加跳转成本。32/24 的两文件分布已解决主要检索痛点;未来模块(如 test-login)出现持续新增再按新 ADDED Requirement 的"首个条目建文件"规则扩展。

2. **归属规则确定化**:按条目`来源变更`名映射 `.ai/rules/index.md` 模块表——安装器域变更(add-workflow-installer、install-portable-ai-workflow、fix-installer-python-38、remove-installer-business-knowledge、install-codex-workflow-yuxiaor、add-installer-upgrade-path)全条目进 installer.md;`工作流端到端验证(临时项目 add-greeting)` 3 条虽含 openspec/gitignore 主题,但其来源活动是安装器端到端验证(坑 1 即"校验器与安装器必须同步演进"),整体归 installer.md,避免同一来源条目散落两文件。其余留 workflow.md。边界条目(add-cancel-state-ci-mirror 沙箱白名单谈校验器、add-installer-upgrade-path 白名单双份坑谈安装器测试)按上述来源变更映射,不做逐条主题重判。

3. **逐字移动、脚本化执行**:用 awk 按条目边界(`^## ` 到下一条前)整块抽取搬运,不手抄;校验用"移动前后全部条目(标题+坑/解行)拼接 diff 为空"+"两文件计数和=56"双重机械证据,延续上一变更已验证的做法。

4. **格式与现状一致**:模块文件无 `#` 总标题,首行即首条 `##`(workflow.md 现状即如此);文件内维持原相对顺序(两文件分别保持时间序)。

5. **规格化为 ADDED 而非 MODIFIED**:README 既有约定未进过主规格;本变更把它固化为可校验要求,给 Archive 三写与路由读取一个规格锚点。不改动 README(其"按模块"表述已正确)。

## 替代方案

- **按主题逐条重判归属**:32+24 条逐条主观重判,边界条目必生争议且不可机械校验,否决。
- **仅建索引不拆文件**:不解决追加读写全文件的规模问题,否决。
- **快速模式直接改**:纯 Markdown 但涉及 56 条知识整体搬迁、错漏即知识损毁,且需留审查痕迹,按标准模式走。

## 风险与边界

- **知识损毁风险**:以整块 awk 搬运 + 双重机械校验 + 独立综合审查覆盖;条目正文零改写。
- **路由读取惯性**:CLAUDE.md/build/archive 技能引用 `.ai/memory/<模块>.md` 为通式,无需改技能;`.ai/rules/index.md` 模块行的关键词已含 memory 路由语义,不改。
- **资产一致性**:assets 只随包 `memory/README.md`,无正文,零影响。
- **范围外(不做)**:不拆第三类文件、不改 memory/README.md、不动 kb/rules、不调整条目顺序。
