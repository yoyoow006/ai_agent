# 变更：扩展项目上下文与验证证据复用

模式: 严格
状态: 待归档

## Why

当前项目已经有空白项目 registry、项目卡、`project-context` / `server-registry` / `workspace-search` / `business-terms` 查询和安装资产同步能力，但目标项目安装后仍缺少两类可复用上下文：

- 项目卡只有维护原则，没有通用模板来约束职责边界、高频入口、跨仓关系、搜索锚点、验证入口和证据基线。
- registry 只描述单项目路径、构建类型、应用入口、搜索范围和业务词，没有多项目依赖声明，也没有验证入口、证据位置和已验证 commit 等技术事实。

同时，长验证缺少共享的证据复用口径：要么重复执行耗时测试，要么风险不透明地沿用旧结果。需要借鉴 `/media/shitou/data2/ai-pms` 的“最小充分验证 + 可信证据复用”经验，同时保持本仓库 OpenSpec 唯一状态真源和完成前新鲜验证门禁。

## What Changes

- 增加通用项目卡模板 `.ai/kb/projects/_template.md`，包含职责/非职责、高频入口、跨仓库关系、搜索锚点、验证入口、证据基线和定位特例；模板只使用非业务占位符，不携带 ai-pms 业务事实。
- 扩展项目 registry 的可选声明字段：
  - `dependencies`：项目名列表，用于声明同 workspace 内项目依赖；
  - `verification.build_command` / `verification.test_command`：非空单行本地命令描述，仅供展示和人工/AI 执行参考，`project_facts.py` 不执行；
  - `verification.evidence`：相对 `.ai/` 的证据文档路径，声明时必须存在且不得越界；
  - `verification.verified_commit`：40 或 64 位十六进制 Git commit，用于和当前项目 HEAD 机械比较。
- `project-context` 输出依赖、验证命令、证据路径和 `verified_commit` 的 current / drifted / unavailable 状态；查询保持只读、不联网、不 clone、不执行 registry 命令。
- Registry 校验拒绝未知依赖、自依赖、重复依赖、循环依赖、非法命令、非法证据路径和非法 commit。
- 增加共享验证证据复用规则 `.ai/kb/verification-evidence.md`：证据必须记录范围、命令、输入与环境身份、执行结果、日志或报告位置和限制；仅在 commit、输入、命令和运行环境等价时复用，不得替代 OpenSpec 状态，不得把 NOT_RUN/UNKNOWN 当作通过。
- 更新 verification 技能、项目登记文档、工具文档、共享路由、shared infrastructure 规格、安装资产 manifest 和对应测试。

## Impact

- 影响 `/media/shitou/石头/wksource/git_me_prj/ai_agent/.ai/kb/projects/`、`/media/shitou/石头/wksource/git_me_prj/ai_agent/.ai/tools/project_facts.py`、事实工具测试、verification 双侧技能、`.ai` 文档、OpenSpec 主规格、安装器资产和测试。
- 源仓库 registry 继续保持空数组；不复制 `/media/shitou/data2/ai-pms` 的项目名、服务名、业务词、源码路径、团队或业务文档。
- `project_facts.py` 新增只读 Git HEAD 观察和 registry 结构校验，不执行 build/test 命令，不新增外部副作用。
- 实现、验证与审查使用严格模式；默认隔离 worktree。

## Non-Goals

- 不实现自动构建、自动测试、远端 clone、缓存写入或测试报告解析。
- 不把验证证据变成第二套任务状态；标准/严格变更进度仍唯一来自 OpenSpec。
- 不引入 ai-pms 的业务项目卡、业务规格、私有 Git 地址或运行脚本。
- 不放宽完成前新鲜验证、严格 required 门禁或 OpenSpec 校验。
