# 分支工作流比较与合并决策

比较方向：当前 `20f3976` → LC 指定分支 `76a1676`；来源治理提交包括 `b93f3e2 feat(workflow): restrict automatic strict routing to assistant gates`。使用 git show 读取来源，未读取其未提交内容作为合并依据。

| 领域 | 当前项目 | 来源分支 | 决策 |
|---|---|---|---|
| 风险路由 | 认证、资金、迁移、并发、公开契约等自动严格 | 仅助手门禁语义变化自动严格；业务高风险完整标准 | 待用户确认后采用，保留业务风险保障和用户升级 |
| 严格审查单元 | 主要举业务不变量 | 明确模式、授权、状态、验证、证据、归档与安装传播不变量 | 合并，并同步双助手 |
| 验证入口说明 | AGENTS 和 Codex README 有 fast/standard/required 与模板入口 | 删除相关段落 | 保留当前说明，追加新路由 |
| 标准小任务归档 | 无 manifest 可归档，持久综合自查 | Archive 技能改为一律 manifest VALID，入口清理条款也收紧为 manifest ID | 不采用倒退；完整审查与小任务分别处理 |
| 精确归档路径 | wrapper 已有 diff 分类和 fail-closed | 新增 .ai/rules/archive.md 强调 --archive-files 精确文件 | 合并可达规则，保留自动升级 |
| 审查证据 | review_manifest freeze/verify/delta | 新增 finalize，验证当前身份后写终局 JSON | 合并并补测试；明确写出后 manifest 可能变陈旧，记录代表写出前验证身份 |
| 度量 | run_id、layer、耗时与结果 | task_id、phase、summarize_task_events | 合并；处理旧记录、异常数据和重复耗时统计边界 |
| OpenSpec 预检 | 检查模式等字段 | 新增拒绝列表前缀模式/状态；同时改写默认值实现 | 仅合并有效预检，保留现有默认值实现 |
| 项目登记 | 只读 project_facts 查询及空 registry | project_registry validate/render 和 30 个业务项目登记 | 只合并通用工具，不带业务数据；支持库模块无应用、显式构建类型、防止多文件静默覆盖 |
| Git 规则 | feature/worktree 通用规则 | 增加嵌套业务仓默认分支保护 | 通用化；恢复默认分支须明确授权，不自动 reset |
| archive_openspec_change | 现有归档工具 | 主要引号/格式改写，测试 argv 出现 openc 拼写 | 不合并无收益格式及拼写变化 |
| 知识 | 通用历史 memory、空项目 registry | 项目知识、本机环境及大段历史 memory 删除 | 保留当前历史，仅抽取新增可复用事实 |
| 分发 | Codex、Claude、安装资产完整源仓 | 安装目标侧主要改 Codex，无对应完整源资产更新 | 在本仓补齐双侧与安装镜像，不能整树覆盖 |

来源新增 project_registry.render 强制主类等字段且默认 Maven，与来源项目登记规格允许库模块空 applications 的约定不一致；目前仅 card 有覆盖检查，其他两个输出可覆盖。来源耗时汇总遍历全部 duration_ms，需防止 summary 和 phase 计时重复相加。这些属于移植时必须解决的边界。

本仓已有待验证的 layered-validation-agent-gating-output-metrics；其事件接口作为兼容基线，不改变其状态或冒用验证证据。本次归档只合并自身 delta。
