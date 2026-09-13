# 设计

## 初步方向

本文件是严格模式 Open 四件套的一部分，不是独立实施计划。用户确认规范后，需按 Design 阶段产出可执行计划并再次确认。

初步方向是不手工零散复制文件，而是使用源仓库既有 manifest 驱动安装器，并把用户输入路径解析后的真实路径传给安装器。安装器负责事务写入、清单校验和目标台账，避免人工复制造成镜像漂移或漏装校验资产。

## 关键决策

- 仅安装 Codex 单侧适配：目标获得 `.codex/`，不获得 `.claude/` 或 `CLAUDE.md`。
- 不把源仓库业务项目、活跃变更、归档历史、Git 历史或远程配置带入目标。
- 不初始化目标 Git 仓库；目标 required 校验必须支持非 Git 根。
- 不登记 `ai_hospital` 业务项目卡，也不预设医院业务模块、构建系统或部署拓扑。
- 安装前后均核对用户文档 SHA-256，避免把非计划文件当作可覆盖内容。
- 写入前重新执行 dry-run；如果目标在此期间出现入口冲突或计划变化，停止并重新确认。

## 风险与边界

- 目标目录可被外部进程 concurrently 修改；第二次预览和实际安装之间仍存在竞态。缓解措施是紧邻写入执行预览，安装器使用事务和 manifest，并在安装后复核用户文件。
- OpenSpec CLI 不在 `/usr/bin`，本机可用路径为 `/home/yoyoo/.nvm/versions/node/v20.19.4/bin/openspec`；验证时显式使用该离线已有命令。
- 不联网、不安装依赖、不执行目标业务代码，不读取用户合作协议正文。

## 待 Design 细化

- 写入前目标状态、入口冲突和用户文件哈希的精确复核顺序。
- 安装器实际执行、幂等预览、required 门禁和 OpenSpec 严格校验的完整命令序列。
- 验证失败时是否以及如何使用安装器事务回滚，何时停止等待用户决定。

## Build 阶段补充事实

- 原安装命令在目标文件系统失败且事务完整回滚；受保护文档哈希不变。
- 根因是 `fuseblk` 不支持安装器依赖的 `renameat2(..., RENAME_NOREPLACE)`，最小探测返回 `EINVAL`。
- 同文件系统临时诊断证明：预创建 35 个清单推导空父目录、重建计划后，安装器可成功创建 55 个文件。该方案等待用户重新确认，未在目标重试。

## Empty-parent correction

- The 35-item list came from direct parents of manifest files and omitted required intermediate directories `.ai/prompts` and `.codex/skills`.
- The failed preparation created only four empty directories and did not touch the protected document.
- Continue only after user confirms the corrected 37-directory set and preflight confirms the four existing directories remain empty.
