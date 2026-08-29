# 审查台账(严格模式:任务级审查×2 轮 + Verify 双阶段)

- 任务级首轮 manifest `f50c710c…`(head 3aa3879,reviewer 中止于 STALE 留 F1–F5);差异复审 manifest `d8719f82…`(head ce11a15,PASS,F1–F5 resolved,新增 R1 resolved)。
- 阶段 1(规格符合性)manifest `ee79c827…`(head eae38e9,PASS,VQ-F1/2/3);修复后 `24f2e091…`(head bcfedc8)。
- 阶段 2(代码质量)manifest `24f2e091…`(PASS,VC-Q1/2/3)。
- 全部 reviewer 均在读取前/结论前 verify manifest;12 条 finding 全部主会话核实后处置。

## 任务级(首轮 F 系列)

- **F1 Critical→resolved**:随包契约测试副本失同步;58a87da 起同步,`test_reusable_assets_are_byte_synchronized…` 常绿。
- **F2 Critical→resolved**:目标侧适配(锁 skip、Ran N 动态统计、skip 理由白名单);目标安装测试终验 OK(EXIT=0)。
- **F3 Critical→resolved**:钩子去参数透传+索引 100755+带参/索引断言用例。
- **F4 Minor→resolved(注记)**:跨提交红历史偏差注记于 tasks 9/10,不改写历史。
- **F5 Minor→resolved**:README 锁描述限定公共入口。
- **R1 Minor→resolved**(差异复审新增):带参用例 stub 参数敏感+红探针(eae38e9)。

## Verify 阶段 1(VQ 系列)

- **VQ-F1 Minor→归档时处置**:MODIFIED 覆盖会使主规格失去"OpenSpec CLI 预装后不得 SKIP"场景;按 archive 技能"保留未明确删除且仍有效的场景"在归档合并时并回。
- **VQ-F2 Minor→resolved**:新增 flock 缺失降级用例(bcfedc8)。
- **VQ-F3 Minor→resolved**:状态 构建中→待验证 补迁移,tasks 1/10 补勾(bcfedc8)。

## Verify 阶段 2(VC 系列)

- **VC-Q1 Minor→resolved**:wrapper 拦截 `--print-external-commands` 透传 core,不再合成 FAIL 误入全量(02d9c39)。
- **VC-Q2 Minor→resolved**:锁基础设施故障(mkdir/fd 失败)降级提示而非误诊并发占用;实现时发现并修复 exec 行重定向持久化吞 stderr 的副作用(编组限定)。
- **VC-Q3 Minor→resolved**:清单解析 helper 失败携带 core stderr 诊断。

## 环境性豁免(非 finding)

- `test_manifest_modes_are_exact_and_match_files` 在本机挂载(全 0777、core.fileMode=false)必败;Git 索引/manifest 模式正确(100644/100755),CI 真实文件系统为权威。终验:82 用例仅此 1 失败、零 error。

## 未验证范围

- CI(GitHub Actions)真实执行未本地复现(yml 结构断言+CLI 语法已验);安装器套件步骤首跑结果以 CI 为准。
- 压力场景行为重放(P3c)按决定不做。

## 残余风险

- 目标内受限 PATH 无 flock,锁并发行为仅源仓覆盖(白名单显式登记)。
- `Ran N` 动态计数与 skip 白名单依赖随包契约测试结构稳定,新增 skip 理由需登记(有子集断言强制)。
- 主会话两次在套件运行期间提交造成时序伪影(F2 复现/CONFLICT),已在流程上改为"终验链期间零编辑";教训入 memory。
