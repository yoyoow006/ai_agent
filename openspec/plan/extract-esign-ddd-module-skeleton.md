# 电子签署 DDD 模块 · 模块骨架与分层门禁实施计划

## 目标

在 `yuxiaor-pms` 中新增进程内 Maven 模块 `yuxiaor-esign`，建立电子签署四个限界上下文的 DDD 分层目录，并用可执行测试固化 Maven 依赖方向和 package import 门禁。此阶段只建立骨架和门禁，不迁移业务行为。

## 全局约束（逐字执行）

- 不修改 `yuxiaor-api` 对外接口定义、HTTP 路由、字段和 Feign 契约。
- 不修改数据库 Schema、不迁移数据、不更换供应商、不拆独立进程。
- 不执行推送、发布、远程 API 调用或删除未合并工作。
- `yuxiaor-esign` 不依赖 `yuxiaor-server`。
- 不迁移生产业务逻辑，不新增生产 Bean。

## 任务 1：新增 Maven 模块

Modify:

- `pom.xml`: `<modules>` 增加 `yuxiaor-esign`。
- `yuxiaor-esign/pom.xml`: parent 为 `com.yuxiaor.pms:yuxiaor`; artifactId 为 `yuxiaor-esign`; jar packaging; `maven.compiler.source/target=1.8`。
- Dependencies:
  - `com.yuxiaor.pms:yuxiaor-api`
  - `com.yuxiaor.pms:elc-signature-api`
  - `com.yuxiaor.pms:yuxiaor-e-signature-api`
  - `org.springframework.boot:spring-boot-starter`
  - `org.springframework.boot:spring-boot-starter-test` scope test
- 不声明 `yuxiaor-server`，不声明 MyBatis/Redis/MQ/供应商 SDK；版本均由父 dependencyManagement 管理。

## 任务 2：分层 package 骨架

Create deterministic package-info source files, not empty directories:

- `src/main/java/com/dream/yuxiaor/esign/subject/domain/package-info.java`
- `src/main/java/com/dream/yuxiaor/esign/subject/application/package-info.java`
- `src/main/java/com/dream/yuxiaor/esign/subject/infrastructure/package-info.java`
- `src/main/java/com/dream/yuxiaor/esign/subject/adapter/package-info.java`
- same four layers for `face`, `contractsign`, `shared`

Each file contains only the matching package declaration.

## 任务 3：模块依赖与分层门禁测试（TDD）

Create:

- `yuxiaor-esign/src/test/java/com/dream/yuxiaor/esign/EsignModuleArchitectureTest.java`

Required assertions:

1. Resolve module source paths from the running module directory; do not hardcode `/media/...`.
2. Maven direction:
   - `yuxiaor-esign/pom.xml` contains no `yuxiaor-server` dependency.
   - `yuxiaor-server/pom.xml` will declare `yuxiaor-esign` after task 4.
3. Required packages exist for all four bounded contexts and all four layers.
4. Domain import denylist by literal source scan:
   - `org.springframework`
   - `org.apache.ibatis`
   - `org.apache.ibatis.annotations`
   - `feign.`
   - `org.springframework.cloud.openfeign`
   - `redis.clients`
   - `org.springframework.data.redis`
   - `com.rabbitmq`
   - `com.junziqian`
   - `org.ebaoquan`
   - `com.taobao`
5. Module-wide deny server internals:
   - imports starting `com.dream.yuxiaor.service.`
   - imports starting `com.dream.yuxiaor.mappers.`
   - imports starting `com.dream.yuxiaor.entity.`
6. Application layer deny imports:
   - `org.springframework`
   - `org.apache.ibatis`
   - Feign/Redis/MQ/vendor packages
   - module `infrastructure` and `adapter` packages
7. Test fails with exact file/import path and is deterministic under JDK 8/JUnit 4.

Red/Green:

- Write test before `yuxiaor-server` dependency modification and run module test.
- Expected initial result: module test can pass for skeleton, server dependency assertion fails if implemented in same test; therefore stage assertion code with server dependency check activated in this task, then make it pass in task 4.

## 任务 4：server 单向依赖

Modify:

- `yuxiaor-server/pom.xml`: add `com.yuxiaor.pms:yuxiaor-esign` dependency immediately after `yuxiaor-api` dependency.
- Do not change `yuxiaor-api` dependency or exclusions.

## 任务 5：验证与状态回写

Commands:

```bash
cd yuxiaor-pms
mvn -s settings-work.xml -pl yuxiaor-esign test -P dev,env-actuator -Denforcer.skip=true
mvn -s settings-work.xml -pl yuxiaor-esign,yuxiaor-server -am validate -P dev,env-actuator -Denforcer.skip=true
```

Expected:

- module architecture test green;
- Reactor includes both modules;
- validate exits 0;
- no Maven cycle.

Additional checks:

- `git diff --check`
- production source diff limited to POM and package-info declarations
- `yuxiaor-api` source diff empty
- update task 2 checklist only after both commands exit 0.

## 提交策略

- Target repository: one revertable commit containing module POMs, package skeleton, architecture test, and server dependency.
- Root repository: one commit updating task status and review evidence; do not include user files `.gitignore`, `.vscode/`, `httpclient.http`, `work_daily.md`.

## 自审结论

- 覆盖 delta spec 的独立 Maven 模块、单向依赖、启动扫描、DDD 分层和 domain/application 禁依赖要求。
- 只新增源码骨架和测试门禁，不改变业务行为、API、Schema、数据或外部副作用。
- 不引入新第三方测试依赖；使用 JDK 标准库和 JUnit 4。
- 无 TBD/TODO；文件与命令具体。
