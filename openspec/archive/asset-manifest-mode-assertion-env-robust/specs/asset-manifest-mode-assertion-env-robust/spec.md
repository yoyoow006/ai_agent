# 资产清单模式断言环境无关化

## ADDED Requirements

### Requirement: 资产清单模式断言必须环境无关

系统 SHALL 以 git 索引记录的规范模式（100644/100755）校验 manifest 声明模式的一致性；对工作树文件系统的模式断言 SHALL 仅约束可执行位与声明一致，不得因 `core.sharedRepository`、umask 等环境策略引入的组写位失败；未跟踪资产 SHALL 以明确错误终止而非跳过校验。

#### Scenario: sharedRepository 环境下断言稳定

- **WHEN** git `core.sharedRepository` 或 umask 使工作树 manifest 资产带组写位（如 0664/0775）
- **THEN** 模式断言按 git 索引规范模式判定并通过
- **AND** 工作树文件仅校验可执行位与声明一致

#### Scenario: 可执行位漂移仍被捕获

- **WHEN** manifest 声明 0755 的资产在 git 索引中记录为 100644（或反向）
- **THEN** 模式断言失败

#### Scenario: 未跟踪资产 fail-fast

- **WHEN** manifest 资产文件未被 git 跟踪
- **THEN** 模式断言以指名文件的明确错误终止，不得静默跳过
