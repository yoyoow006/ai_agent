# 设计与待确认选择

## 目标与约束

验证 wrapper 负责计划与层级，角色契约负责派发前判定，core/工具负责事件和指标。计划、检查、dispatch/result 与 metrics 共享 run_id 和 schema 版本。不得修改业务运行时、公开契约或产生外部副作用。

## 方案与替代方案

- 方案：在现有 wrapper 入口生成声明式分层计划；以 Python 标准库实现 JSONL 与原子指标写入；代理调用前做四条件静态门控。
- 替代方案及取舍：不另造独立验证 CLI，保留现有入口；不把代理门控实现为默认并行；不引入数据库或长期遥测。

## 边界与错误路径

层级失败将后续依赖项标为未执行并给出原因码；JSONL 或指标写入失败只产生诊断，不吞掉人类输出，也不改变真实退出码；代理缺少任一条件则拒绝并由主会话处理。

## 验证矩阵

| 场景 | 命令 | 预期 |
|---|---|---|
| 分层升级 | `bash scripts/validate-workflow.sh --standard --archive-files scripts/validate-workflow.sh` | 输出升级原因并执行 required |
| 参数冲突 | `bash scripts/validate-workflow.sh --fast --require-openspec` | 退出 2，不执行部分门禁 |
| JSONL 诊断 | `WORKFLOW_OUTPUT=jsonl bash scripts/validate-workflow.sh --fast` | 每行可解析，末行保留人类汇总 |
| 指标降级 | `METRICS_DIR=/dev/null bash scripts/validate-workflow.sh --fast` | 验证结果不被写入失败改变 |

