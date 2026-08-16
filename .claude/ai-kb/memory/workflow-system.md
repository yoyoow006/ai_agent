# workflow-system 踩坑与注意事项

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：仓库目录属主为 root 时 git 报 "dubious ownership" 拒绝操作
**解**：git config --global --add safe.directory <仓库路径>；注意这是机器级配置，换机器要重配

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：本机 git 版本旧，git init -b main 不被支持（exit 129）
**解**：git init 后用 git checkout -b main 兼容；写脚本时避免依赖新 git 特性

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：git 不跟踪空目录，openspec/specs、archive、.claude/skills 等骨架目录在 fresh clone 上消失，结构校验假红
**解**：空骨架目录放 .gitkeep 入库；终审发现的计划缺口，已修复

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：本机 core.fileMode=false 掩盖了脚本以 100644 提交的问题，fresh clone 无执行位
**解**：git update-index --chmod=+x <脚本> 直接改索引模式；校验含执行依赖的文件时留意 fileMode 配置
