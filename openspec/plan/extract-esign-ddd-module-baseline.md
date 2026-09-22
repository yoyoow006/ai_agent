# 电子签署 DDD 模块 · 契约与行为基线实施计划

## 目标

在不改变任何生产代码行为的前提下，为目标变更 `extract-esign-ddd-module` 建立可重复执行的 HTTP/Feign 契约基线、运行时兼容语义基线与既有相关测试结果基线。产物只允许记录事实，不得顺手修复、跳过或改写业务缺陷。

## 范围与架构事实

- 目标仓库：`yuxiaor-pms`，嵌套 Git 仓库。
- 基线提交：`master@fb6b634b7a7383903a7c2672502fd4b631236717`。
- 已创建任务分支：`feature/extract-esign-ddd-module`，当前指向基线提交且干净。
- 严格模式要求隔离实现工作区：从已存在且未被其他 worktree 检出的任务分支创建 `../.worktrees/extract-esign-ddd-module`。创建前必须确认该路径不存在且目标仓库当前分支可安全切回 `master`。
- 基线测试位于 `yuxiaor-server/src/test/java`，只依赖现有 JUnit/Mockito/AssertJ/Spring 测试设施，不新增第三方依赖。
- 契约快照采用纯 Java 反射与注解读取，不启动 Spring 容器，不访问数据库、Redis、MQ、文件服务或供应商网络。

## 全局约束（逐字执行）

- 不修改 `yuxiaor-api` 对外接口定义、HTTP 路由、字段和 Feign 契约。
- 不修改数据库 Schema、不迁移数据、不更换供应商、不拆独立进程。
- 不执行推送、发布、远程 API 调用或删除未合并工作。
- 生产代码不得出现任何行为性修改；本任务只允许新增测试与基线文档。
- Maven 测试只使用仓库内 `settings-work.xml` 和既有 profile/参数，不下载新的运行时依赖。

## 任务 1：创建隔离 worktree 并冻结基线

Create/Use:

- `../.worktrees/extract-esign-ddd-module`

Steps:

1. 在目标仓库确认 `git status --short` 为空、当前分支为 `feature/extract-esign-ddd-module`、`git worktree list` 只有主工作区。
2. 在目标仓库切回 `master`，确认 `master` 与任务分支均指向 `fb6b634b7a`。
3. 执行 `git worktree add ../.worktrees/extract-esign-ddd-module feature/extract-esign-ddd-module`。
4. 在 worktree 确认分支为 `feature/extract-esign-ddd-module`、状态干净、`HEAD` 为 `fb6b634b7a`。

Test:

```bash
git -C ../.worktrees/extract-esign-ddd-module status --short --branch
git -C ../.worktrees/extract-esign-ddd-module rev-parse HEAD
```

Expected: 输出 `feature/extract-esign-ddd-module`，无未提交文件，HEAD 为 `fb6b634b7a7383903a7c2672502fd4b631236717`。

Failure handling: 任一步骤失败或目标路径已存在时停止，不得覆盖路径或强制切换分支。

## 任务 2：新增 HTTP/Feign 契约快照测试

Create:

- `yuxiaor-server/src/test/java/com/dream/yuxiaor/service/elcsignature/EsignHttpFeignContractBaselineTest.java`

Captured contracts:

1. `IContractSignMethodService`
2. `CompanyCertificationService`
3. `PersonFaceAuthService`
4. `LocalFlatmateSignService`
5. `YxrCompanySubsidiaryService`
6. `EsignatureCallBackController`
7. `CompanyContractWillingSignController`
8. `ContractSignMethodServiceImpl`
9. `RenterFaceSignServiceImpl`

Implementation contract:

- Test must derive mappings by reflection, not hardcoded controller bean names.
- For each class: capture class-level `@RequestMapping` value plus every declared public method's HTTP mapping annotation, path values, produces/consumes/headers, parameter annotations in declared order, and declared return type FQCN.
- For each Feign-bearing API source: assert nested `@FeignClient` service name is exactly `yuxiaor-server`.
- Snapshot assertions must include the exact route list in the delta spec; on mismatch they must fail with actual and expected values.
- Do not assert implementation details unrelated to HTTP/Feign contract.
- Keep JDK 8 syntax and existing test dependency set.

Test:

```bash
cd ../.worktrees/extract-esign-ddd-module
mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest=EsignHttpFeignContractBaselineTest
```

Expected: test passes against baseline `fb6b634b7a`.

Failure handling: mismatch means the route inventory or annotation extraction is incomplete. Correct only the new test, never source contracts.

## 任务 3：新增运行时兼容语义清单

Create:

- `yuxiaor-server/src/test/resources/esign-baseline/runtime-compatibility.md`

Required sections and exact content domains:

- `## Old FQCN / Spring Bean compatibility`
  - List the old FQCN and bean type/name/qualifier facts extracted from annotations and implementations for the electronic-signature service surface.
- `## Async semantics`
  - List `@Async` usages in electronic-signature packages and callback classes, including executor name where declared.
- `## MQ bindings`
  - List queue/exchange/routing-key annotations or constants in scope, including listener and producer-side send destinations.
- `## Transaction post-actions`
  - List `TransactionSynchronization`/afterCommit usage in scope and the action performed after commit.
- `## Baseline caveats`
  - List facts that cannot be represented by the static test and require later characterization tests.
- `## Reproduction`
  - Include the exact Maven commands used for baseline and contract tests.

Steps:

1. Search production sources with `rg` for:
   - `@Async`, `@FeignClient`, `@RabbitListener`, `@StreamListener`, `@Service`, `@Component`, `TransactionSynchronization`, `afterCommit`, and electronic-signature package roots.
2. Record only verifiable file paths and declaration facts; no speculative compatibility promises.
3. Keep the document deterministic: sorted by FQCN/destination, no timestamps or machine-specific paths.

Test:

```bash
cd ../.worktrees/extract-esign-ddd-module
rg -n '^## ' yuxiaor-server/src/test/resources/esign-baseline/runtime-compatibility.md
! rg -n 'TBD|TODO|适当|待补充' yuxiaor-server/src/test/resources/esign-baseline/runtime-compatibility.md
```

Expected: all six headings are present; no placeholder markers.

Failure handling: missing heading or placeholder means inventory incomplete; rerun source searches and update facts.

## 任务 4：运行既有相关测试并记录结果

Modify:

- `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md`

Create the file if absent.

Exact command:

```bash
cd ../.worktrees/extract-esign-ddd-module
mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest='*Esign*,*WillingSign*,*Face*,*Flatmate*,*Subsidiary*,*Certification*'
```

Record:

- command and Maven exit code;
- Java/Maven versions actually used;
- total tests, failures, errors, skipped;
- failed/error/skipped test identifiers, if any;
- concrete local-environment blockers, if any;
- source commit and clean-worktree confirmation;
- statement that failures/skips are baseline facts and must not be changed by migration.

Test:

```bash
cd ../.worktrees/extract-esign-ddd-module
mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest=EsignHttpFeignContractBaselineTest
```

Expected: contract baseline test remains green after the existing-test run; existing-test baseline document has command, environment, exit code and aggregate counts.

Failure handling: if Maven cannot run, capture the exact nonzero output and record it as an environment blocker. Do not replace the required command with a smaller subset and do not claim tests passed.

## 任务 5：Diff 审查与任务状态更新

Steps:

1. Run `git diff --check` in the worktree.
2. Review complete diff and confirm it contains only:
   - one new contract test;
   - baseline resources under `src/test/resources/esign-baseline/`;
   - no production code changes.
3. Update orchestrator change tasks 1.1–1.5 checkboxes to `[x]` only after their required commands or documented environment blockers are complete.
4. Keep proposal status `构建中` until baseline implementation and verification are complete.

Commands:

```bash
cd ../.worktrees/extract-esign-ddd-module
git diff --check
git status --short
git diff --stat
git diff -- yuxiaor-server/src/main yuxiaor-api/src/main
```

Expected: diff check passes; main source diff is empty; changes are limited to test and test-resource paths.

## 回滚与提交策略

- All target-repository baseline changes belong to one independently revertable commit on `feature/extract-esign-ddd-module`.
- Orchestrator-repository OpenSpec state, plan and task checkbox updates belong to one separate workflow commit; never include the unrelated existing `.gitignore` modification.
- If baseline capture reveals a spec route inventory error, stop and update the OpenSpec delta/design before changing tests.
- If tests reveal a production defect, record it in baseline caveats; fixing it is outside this task.

## 自审结论

- 覆盖 delta spec 的契约冻结、controller 委托前提取值、Feign service name、既有测试结果和迁移不得改变失败集合要求。
- 任务 4 的 Maven 命令不触发外部副作用；依赖下载如发生则仅是本地构建缓存副作用，不属于发布/远程业务副作用。
- 未引入数据库、Schema、数据删除、权限、资金、外部业务副作用或新第三方依赖。
- 计划没有 TBD/TODO 或不可执行占位；文件与命令均具体。
