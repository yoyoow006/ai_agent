# 任务清单（规范阶段范围）

- [x] 1.1 明确分层执行计划数据结构、升级原因码和停止规则，覆盖现有 wrapper 入口。
- [x] 1.2 设计并实现统一事件字段与 JSONL 输出开关，保持人类汇总末行兼容。
- [x] 1.3 为 core、wrapper、required/standard 升级与失败停止补充契约测试。
- [x] 2.1 在代理角色契约和 Codex 入口加入四条件门控、拒绝原因码及快速/标准小任务豁免。
- [x] 2.2 为合法 dispatch、拒绝 dispatch、结果缺字段和共享边界冲突补充测试。
- [x] 3.1 新增轻量度量记录器，采用 schema、run_id、原子写入和写入失败降级。
- [x] 3.2 将层级、代理、缓存和解析计数接入运行末端，验证 required 不读缓存。
- [x] 3.3 同步共享规格、规则索引、技能和安装资产镜像，避免双树语义漂移。
- [x] 4.1 运行目标契约测试、--fast、standard、required、OpenSpec strict 与 diff 校验并记录证据。

## 本地整合策略

- 分支/worktree：严格模式默认隔离 worktree；四件套确认前不创建独立计划、不实现代码。
- 提交边界：输出协议、代理门控、度量记录器和规格同步按职责单元实现与审查。
- 外部副作用授权：不自动提交、推送、发布或调用外部服务；.ai-local/metrics/ 仅为本地运行产物。

## Verify 终局记录（2026-11-06）

- summary: SUMMARY change=layered-validation-agent-gating-output-metrics mode=严格 status=待归档 unchecked=0/9 head=9fdc75b94777 rules=c1f51966572f
- 测试证据：pytest 六文件全量 360 passed + 471 subtests（0:17:27，仅 2 个环境性预存失败，干净 worktree 探针证明与本变更无关）；require-openspec 门禁 PASS=282 FAIL=0 SKIP=0（gate_rc=0）；openspec validate --strict valid；镜像 cmp 全 SAME；git diff --check 工作树与足迹段干净。
- diff 范围：comparison base de3c26a；足迹 = de3c26a..ffa9c2c（原始实现，18 文件 +770/-7）+ 13fdcc3..9fdc75b（Verify 修复三提交：939c5ac 阶段一 15 文件、ddcf6f7 阶段二 18 文件 +333/-102、9fdc75b CQ-10 2 文件）。
- finding 状态：阶段一 F1..F10 全部 resolved（F8 由 47ca474 自消；F2/F4 按用户 2026-11-05 裁定收敛）；阶段二 CQ-1..CQ-10 全部 resolved（CQ-3 按用户裁定删死字段+修规格）；10 项排除核实无 finding。终局 manifest-final 见 .ai-local 归档后清理。
- 未验证范围：完整标准层由 required 等价覆盖未单独跑；CQ-10 修复未在真实 fresh-clone 冷缓存重复概率实验（断言对任意顺序成立，不依赖该实验）；宿主侧实际代理调度行为（仓库外）。
- 残余风险：manifest 模式断言与枚举断言两项环境性失败待后续变更处理（sharedRepository 模式坑）；WORKFLOW_STANDARD_BASE 技能接线待后续变更；finalize 一次取时 spawn 与 EventWriter 非法 status 先建文件均为已判定可接受的既有行为。
