# 新增登录随机验证测试项目

模式: 严格
状态: 构建中

## Why

用户要求在根目录 `projects/` 下创建一个测试项目，实现登录功能和随机验证功能。登录属于认证能力，失败路径可能影响凭据保密、用户枚举和验证码暴力破解边界，因此按仓库风险路由升级为严格模式。

当前 `projects/` 为空、未忽略且未跟踪，适合存放独立测试项目。本变更不修改 `.ai/kb/projects/registry.json`，避免把示例代码误登记为安装工具源仓库的业务项目事实。

## Assumptions

- 项目路径：`projects/test-login/`。
- 技术栈：Python 3.8 标准库，不引入第三方依赖，不联网。
- 形态：可导入的登录服务模块、命令行演示入口和 `unittest` 测试。
- 账户存储：内存存储；项目退出后不持久化用户数据。
- 随机验证：6 位数字验证码，使用密码学安全随机源，设置有效期、尝试次数上限和一次性使用语义。

## What Changes

- 新增 Python 测试项目：
  - 登录服务 API；
  - 用户注册与密码校验；
  - 随机验证码生成、有效期与尝试次数控制；
  - 登录会话 token 生成；
  - 命令行演示入口；
  - 单元测试与项目 README。
- 密码使用随机盐和 PBKDF2-HMAC-SHA256 存储，验证使用恒定时间比较。
- 验证码使用 `secrets` 生成；演示环境通过可注入测试投递通道获取，不打印生产凭据。
- 测试项目不接入网络、数据库、短信、邮件或外部认证服务。

## Impact

- 受影响路径：`projects/test-login/`、OpenSpec 变更目录。
- 不修改安装器运行时代码、资产清单、`.ai/kb/projects/registry.json` 或工作流校验器。
- 不把测试项目登记为共享知识层的业务项目。
- 安全边界：这是本地测试项目，不声明适合生产环境直接部署。

## Verification Evidence

### TDD red reconstruction

The initial implementation commit placed the tests and implementation in one commit, which did not preserve independently reviewable red evidence. To close `TLT-TDD-EVIDENCE-001`, the committed test-only set from `d566dd3` was copied to `/tmp/add-test-login-red.ZYt0R4` without `login_service.py`, `cli.py`, or `README.md`, then rerun with:

```bash
python3 -B -m unittest discover -v -s tests -p 'test_*.py'
```

The command exited `1` with the expected module-missing failures:

```text
test_cli (unittest.loader._FailedTest) ... ERROR
test_login_service (unittest.loader._FailedTest) ... ERROR

======================================================================
ERROR: test_cli (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_cli
Traceback (most recent call last):
  File "/tmp/add-test-login-red.ZYt0R4/tests/test_cli.py", line 5, in <module>
    from cli import run_demo
ModuleNotFoundError: No module named 'cli'

======================================================================
ERROR: test_login_service (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_login_service
Traceback (most recent call last):
  File "/tmp/add-test-login-red.ZYt0R4/tests/test_login_service.py", line 5, in <module>
    from login_service import (
ModuleNotFoundError: No module named 'login_service'

----------------------------------------------------------------------
Ran 2 tests in 0.000s

FAILED (errors=2)
```

### Security regression hardening

`TLT-SECURITY-REGRESSION-002` was closed by adding tests for:

- exact PBKDF2-HMAC-SHA256 call parameters and digest;
- one equal-parameter dummy PBKDF2 call for unknown users;
- password comparison delegation to `hmac.compare_digest`;
- secure `secrets.token_urlsafe(24)` challenge IDs and `secrets.token_urlsafe(32)` session tokens.

The strengthened suite runs 13 tests and passes. Four isolated mutations now fail:

- wrong PBKDF2 algorithm: `FAILED (failures=2)`;
- ordinary password equality instead of constant-time comparison: `FAILED (failures=1)`;
- deterministic session token: `FAILED (failures=1)`;
- removed unknown-user dummy work: `FAILED (failures=1)`.
