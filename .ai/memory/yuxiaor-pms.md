## 2026-09-22 · 来源变更 extract-esign-ddd-module
**坑**：`yuxiaor-server@fb6b634b7a` 最初在 `WillingSignRejectResultDTO` 五处引用处生产编译失败；远端 API SNAPSHOT 未包含该类，且继续重试又暴露 `acc-bill-api` 缺少 `ContractReverseDetailReq/Dto`。
**解**：新克隆 `yuxiaor-e-signature@6c679be` 后，先 `package` API 模块，再用 `install:install-file` 本地安装（父 POM 会给库模块绑定错误的 Spring Boot start，不要直接 install）；`acc-bill-api` 可用本地 `1.0.0-20260901.062458-16` 快照恢复。此后生产 compile 已通过，但 full test 卡在4个无关 JUnit5/Mockito 测试，详见 `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md`。
