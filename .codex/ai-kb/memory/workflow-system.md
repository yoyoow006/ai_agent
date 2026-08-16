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

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：verify 阶段审查通过后未回写 proposal 状态字段（构建中→待验证→待归档两跳均漏），归档时才发现状态滞后
**解**：verify 技能后续版本应把状态回写列为显式收尾步；归档开工前先核对 状态: 待归档

## 2026-08-16 · 来源变更 工作流端到端验证（临时项目 add-greeting）
**坑**：迁移 .codex 工作流后只改了校验器未同步改安装器，install-workflow.sh 仍只装 .claude 资产，装后自检因 .codex 缺失整片判红
**解**：校验器与安装器是结构不变量的两面，必须同步演进；安装器已补 AGENTS.md + .codex/（README/skills/ai-kb/sdd）+ .gitignore 草稿区规则

## 2026-08-16 · 来源变更 工作流端到端验证（临时项目 add-greeting）
**坑**：openspec CLI 严格校验要求 Requirement 正文含英文 SHALL/MUST，纯中文"应"判错；且 validate --all 还会校验主 specs（缺 ## Purpose 即红）
**解**：Requirement 用"系统 SHALL …"中英混排；archive 新建主规格先写完整骨架（# 标题 + ## Purpose + ## Requirements）再并入 delta；终验跑 openspec validate --all

## 2026-08-16 · 来源变更 工作流端到端验证（临时项目 add-greeting）
**坑**：python unittest 的 __pycache__/*.pyc 被 git add -A 误跟踪，规格审查判越界；安装器不管理目标 .gitignore，.codex/sdd 草稿区裸奔为未跟踪文件
**解**：项目初始化即写 .gitignore（__pycache__/、*.pyc）；安装器幂等追加 .codex/sdd 忽略规则；实现提交后 git ls-files | grep pyc 自查
