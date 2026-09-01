# Tasks: slim-workflow-skills

严格模式：本文件为范围清单；可执行实现计划由 Design 阶段的 `openspec/plan/slim-workflow-skills.md` 承担。

- [ ] 1. 校验器守卫红测：向 6 个 SKILL.md 路径注入"未随本仓库迁移"、删除 writing-skills 锚串，新契约用例先行失败（注入必红）
- [ ] 2. 实现 `validate-workflow-core.sh` 三守卫（迁移注记 absence、`tr -d`/`wc -m` 锚串、`workflow-pressure-scenarios.md`/`重跑` 绑定锚串；显式 return 0；零新外部命令）＋干净必绿配对；同步契约套件计数断言
- [ ] 3. writing-skills 内联瘦身（迁移注记并一行、示例单例化、去重；目标 ≤7500 去空白字符）＋字符口径验证命令与阈值登记＋场景重跑绑定句
- [ ] 4. parallel-agents 示例本土化（bash/python 安装器场景）＋叙事节压缩（目标 ≤1800）；保留适配注记行与 5 个现行工具名
- [ ] 5. systematic-debugging 示例本土化（安装器/校验器多层排查替代 macOS 签名链）；宿主语汇中性化；阈值合规（≤5000）
- [ ] 6. 四副本同步（`.codex`＋资产树两侧，路径前缀适配）；现验 mirror_equal、适配注记计数=1、废弃工具名零残留、资产/工作树逐字一致
- [ ] 7. 9 个施压场景全量重跑；逐场景 PASS/FAIL 与逐字理由记录至 `scenario-rerun.md`
- [ ] 8. 严格终验链：`--require-openspec` 全量门禁＋`openspec validate --all --strict`＋安装器套件（`-B`、串行、后台长跑）；umask-002 环境先做权限规范化；终验链期间零提交
