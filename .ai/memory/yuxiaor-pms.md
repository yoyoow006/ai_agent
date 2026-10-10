## 2026-09-22 · 来源变更 extract-esign-ddd-module
**坑**：`yuxiaor-server@fb6b634b7a` 最初在 `WillingSignRejectResultDTO` 五处引用处生产编译失败；远端 API SNAPSHOT 未包含该类，且继续重试又暴露 `acc-bill-api` 缺少 `ContractReverseDetailReq/Dto`。
**解**：新克隆 `yuxiaor-e-signature@6c679be` 后，先 `package` API 模块，再用 `install:install-file` 本地安装（父 POM 会给库模块绑定错误的 Spring Boot start，不要直接 install）；`acc-bill-api` 可用本地 `1.0.0-20260901.062458-16` 快照恢复。此后生产 compile 已通过，但 full test 卡在4个无关 JUnit5/Mockito 测试，详见 `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md`。

## 2026-10-09 · 来源变更 add-contract-basis-rent-price-placeholder
**坑**：当前默认本地 Maven 仓库在沙箱只读，且 `yuxiaor-server` 全量 `testCompile` 被4个无关 JUnit5/Mockito3 风格测试阻断；`master` 亦依赖较新 `agent-api` SNAPSHOT。
**解**：复制 `/media/shitou/data3/repoYxr` 到 `/tmp` 并用 `-Dmaven.repo.local`，离线跑生产 `compile`；目标测试用 Surefire 独立 classpath 下的 JUnit 4 编译/执行。更新 `agent-api` 为 Nexus `20260917.102435-7` 后生产编译可过；不要把无关测试修复混入业务分支。

## 2026-10-10 · 来源变更 tenant-light-owner-realname-flex
**坑**：`yuxiaor-server` Maven 目标测试会在 `testCompile` 被既有 JUnit5/Mockito3 风格无关测试阻断；直接 Maven 还会因沙箱 DNS 访问 Nexus 失败。现有独立测试 classpath 缓存指向不存在的 `/home/shitou/workspace/repoYxr`。
**解**：使用 `/tmp/repoYxr-compatible`、`-o -Dmaven.repo.local` 先跑生产 compile；把 `/tmp/esign-test-classpath.txt` 中旧仓库前缀映射到 `/tmp/repoYxr-compatible`，用 `javac` 单独编译目标测试，再以 `org.junit.runner.JUnitCore` 执行，避免混入无关测试修复。Mockito `@InjectMocks` 对 superclass 字段注入时，测试不要再用局部变量遮蔽 request，stub 必须绑定实际请求实例。
