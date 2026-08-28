# Tasks（范围清单——严格模式实现计划由 Design 阶段独立产出）

- [x] 1. 台账数据层：profile schema v2 读写、sha256 计算、legacy 识别与 fail-closed 校验（红：无实现时测试失败）
- [x] 2. 升级计划：build_upgrade_plan 四值判定＋REMOVED/KEPT 生成＋入口文件豁免；SKIPPED 不产生写动作
- [x] 3. CLI 与报告：`--upgrade` 参数、USAGE、逐文件报告与汇总、退出码语义（SKIPPED≠3）
- [x] 4. 事务集成：台账作为 PlanItem 同批原子发布/回滚；dry-run 零写入
- [x] 5. 文档：`.ai/tools/README.md` 升级章节、帮助文本
- [x] 6. 回归与终验：安装器测试全套＋全量 required 门禁；真实目标（yuxiaor）演练属外部动作，另行授权
