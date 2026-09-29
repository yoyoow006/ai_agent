模式: 标准
状态: 待验证

# 登记电子签署项目 yuxiaor-e-signature

## Why

本地已检出 `yuxiaor-e-signature@6c679be`，但它尚未进入 `.ai/kb/projects/registry.json`。事实工具无法通过 `server-registry` 定位 `yuxiaor-e-sign-server`，也无法在电子签署项目中搜索 `EsignatureService`、回调、渠道适配等符号。

用户提供了权威登记口径：电子签署项目根目录、server/base/e签宝/君子签/API 模块、启动入口和对外 API/Feign 契约位置。仓库源码进一步核实了 Maven modules、`spring.application.name`、Feign service name、启动类、渠道实现与构建脚本。

## What Changes

- 在 `registry.json` 新增 `yuxiaor-e-signature` 项目：
  - `path: yuxiaor-e-signature`
  - `build: maven`
  - 项目卡：`.ai/kb/projects/yuxiaor-e-signature.md`
  - `applications` 登记 `yuxiaor-e-sign-server` 与 `com.yuxiaor.pms.esign.YuxiaorEsignApplication`
  - `search_roots` 覆盖 README、POM、构建脚本、API、base、e签宝、君子签、server 源码
  - `business_terms` 覆盖电子签署、实名认证、刷脸认证、合同签署、回调、渠道路由、账号、E签宝、君子签
  - `verification` 登记本地 build/test 展示入口，不声明未复验的 verified_commit
- 新建 `.ai/kb/projects/yuxiaor-e-signature.md` 项目卡，记录模块职责、废弃君子签渠道、入口、跨项目契约与残余不确定项。
- 更新 `.ai/rules/index.md` 项目路由表，新增“电子签署服务”模块条目。
- 不修改 `yuxiaor-e-signature` 源码、POM、配置或 Git 状态。

## Impact

- 事实查询：`project-context`、`server-registry`、`workspace-search`、`business-terms` 可进入该项目。
- 知识路由：后续电子签署、实名、刷脸、合同签署问题会路由到该项目卡和权威源码。
- 验证：本次仅验证登记结构与只读查询，不执行 Maven 构建；构建命令只作为人工验证入口展示。
- 风险：项目卡不声称服务部署状态、生产流量或历史兼容细节；未验证范围显式记录。

## 范围

### 包含

- `.ai/kb/projects/registry.json`
- `.ai/kb/projects/yuxiaor-e-signature.md`
- `.ai/rules/index.md`
- `openspec/changes/register-yuxiaor-e-signature/`

### 不包含

- 修改 `yuxiaor-e-signature` 项目源码或配置。
- 执行、修复或优化 Maven 构建。
- 登记 PMS 项目对电子签署项目的 registry 依赖；当前 registry 依赖语义面向直接项目依赖，二者关系先记录在项目卡跨仓库关系。
- 推送、创建 PR 或发布任何知识资产。

## 需要确认的方案假设

1. registry 项目名使用 `yuxiaor-e-signature`，显示名称为“电子签署项目”。
2. `yuxiaor-e-sign-junzi` 按用户输入标记为已废弃渠道模块，但仍作为搜索根保留，供历史代码和兼容排查。
3. 本次登记不添加 `verified_commit`，因为尚未对 `6c679be` 执行完整构建/测试证据基线。

## 验收口径

- registry JSON 可解析并通过事实工具的深层校验。
- `project-context --project yuxiaor-e-signature` 输出可用项目、server 应用入口和验证入口。
- `server-registry --server yuxiaor-e-sign-server` 唯一定位该项目。
- `business-terms` 可按“君子签”等业务词路由到项目与源码路径。
- `workspace-search` 可在电子签署项目中搜索权威符号且不进入未登记路径。
- `.ai/rules/index.md` 包含电子签署服务路由条目。
- OpenSpec strict 校验通过。
