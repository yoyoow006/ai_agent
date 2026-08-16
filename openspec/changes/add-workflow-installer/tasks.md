# 任务清单：add-workflow-installer

## 1. 安装脚本
- [x] 1.1 编写 scripts/install-workflow.sh（参数解析/冲突扫描/备份覆盖/复制清单/通用 project.md/装后自检）
- [x] 1.2 chmod +x 并以 git update-index --chmod=+x 提交（执行位坑）
## 2. 实测验收
- [ ] 2.1 空目标目录安装（/tmp 试验场）：全资产落位 + 装后自检全绿证据
- [ ] 2.2 冲突场景实测：预置 CLAUDE.md 与同名技能，验证默认中止清单与 --force 备份 .bak
- [ ] 2.3 无 openspec CLI 环境模拟（PATH 收窄）：安装与自检完整成功
## 3. 收尾
- [ ] 3.1 提交（feat: 前缀中文）与勾选回写
