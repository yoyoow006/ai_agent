# Tasks

- [ ] 1.1 落点:确认工作区仅含快速批次两个文件与四件套;创建并切到 `feature/split-shared-memory-by-module`;按两个职责单元分别提交:①四件套(proposal`状态: 构建中`、specs、design、tasks);②快速批次文档(`.ai/rules/index.md` 目标侧产物标注、`openspec/archive/README.md` 归档索引,审计 P3a/P3b,提交信息注明)。
      验证:两笔 `git show --stat` 各只含对应文件;`git branch --show-current` 为 feature。
- [ ] 1.2 预检基线:记录拆分前机械基线——`grep -c '^## ' .ai/memory/workflow.md` = 56;全部条目(标题+坑/解行)拼接保存为基准文件。
      验证:基准文件存在且行数与 56 条结构相符。
- [ ] 1.3 拆分:awk 按条目整块抽取安装器域 32 条(来源变更:add-workflow-installer、工作流端到端验证(临时项目 add-greeting)、install-portable-ai-workflow、fix-installer-python-38、remove-installer-business-knowledge、install-codex-workflow-yuxiaor、add-installer-upgrade-path)写入新文件 `.ai/memory/installer.md`;从 `workflow.md` 删除这些条目;两文件内保持原时间序。
      验证:`grep -c '^## ' .ai/memory/installer.md` = 32;`grep -c '^## ' .ai/memory/workflow.md` = 24;两文件首条均为 `## 2026-08-16`。
- [ ] 1.4 逐字无损校验:拆分后两文件全部条目(标题+坑/解行)按原 workflow.md 顺序拼接,与 1.2 基准 diff 为空;再按 installer.md→workflow.md 顺序拼接同样比对(证明条目集合等价)。
      验证:两个方向 diff 均为空;`git diff --check` 干净。
- [ ] 1.5 门禁:`bash scripts/lib/validate-workflow-core.sh` FAIL=0;`openspec validate split-shared-memory-by-module --strict --no-interactive` 通过;完整门禁 `bash scripts/validate-workflow.sh` 后台串行现跑 FAIL=0。
      验证:三个命令退出码均 0。
- [ ] 1.6 提交:memory 拆分作为单一职责单元提交。
      验证:`git show --stat HEAD` 仅 `.ai/memory/{installer.md,workflow.md}`。
- [ ] 2.1 状态推进:tasks 全勾、proposal `状态: 待验证` 并提交。
- [ ] 3.1 Verify:主会话 freeze manifest;独立上下文 reviewer 全 diff 综合审查(逐字无损、32/24 计数、归属符合 design 规则 2、范围无扩大);finding 闭环。
      验证:manifest 两次 verify VALID;Critical/Important 清零。
- [ ] 4.1 终验:现跑完整门禁 FAIL=0 + `git diff --check`;`状态: 待归档` 并提交。
- [ ] 5.1 归档:delta 合并入主规格;`状态: 已归档`;目录移入 archive;追加 `openspec/archive/README.md` 索引行;归档后现跑完整门禁;`chore(archive)` 提交。
- [ ] 6.1 整合:本地 `--no-ff` 合回 main,合并结果复跑完整门禁;按确认授权推送 origin/main。
