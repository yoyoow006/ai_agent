## 2026-09-22 · 来源变更 extract-esign-ddd-module
**坑**：`yuxiaor-server@fb6b634b7a` 编译在 `WillingSignRejectResultDTO` 五处引用失败；当前及本地缓存的 `elc-signature-api`、`yuxiaor-e-signature-api` SNAPSHOT 均无该类，仓库本地/远端分支也无源码。该依赖由提交 `783c5cfe26` 引入。
**解**：不要在迁移分支内补 DTO 或改生产代码；先恢复/发布配套外部 API 构件，再按 `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md` 的原命令重跑基线。API 契约断言可用 Maven 测试 classpath 单独编译/运行，验证不受该生产编译缺失类影响。
