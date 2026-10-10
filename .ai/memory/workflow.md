
## 2026-10-10 · 来源变更 tenant-light-owner-realname-flex
**坑**：Archive 自动升级时把 `--archive-files` 传成 `.ai`、`openspec`、`.codex` 等目录级预设清单，普通归档/知识文件也会命中 diff，误触发 required 全量契约套件并暴露无关 profile 夹具失败。
**解**：业务归档未触及治理/工作流语义时直接运行 `--archive-light`；确需自动分类时，先取 Verify 后 diff，再把其中精确变更的治理/工作流文件逐个传给 `--archive-files`，禁止目录或预设大清单。
