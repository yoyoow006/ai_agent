# 新增登录随机验证测试项目

模式: 严格
状态: 已归档

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

### Build verification

- Project suite: 18 tests passed.
- Python compilation for service, CLI, and tests exited 0.
- `python3 cli.py demo --auto` exited 0 and returned a session token.
- `python3 cli.py demo --auto --reject` exited 1 with the fixed safe failure message.
- `openspec validate add-test-login-project --strict --no-interactive` passed.
- `git diff --check` exited 0.
- `bash scripts/validate-workflow.sh --require-openspec` passed with `FAIL=0`.
- Final specification review passed with manifest `d3c007cfb89a10120fa8836484ab9cd38a4df1fae89dc4fd57ecf89ae8ddae8d`.
- Final quality review passed after delta remediation with manifest `95f4b628795934a9642adf755375349f1dd2debe9b5d601c04de5c0da192cdad`.
- The final main-session required workflow run output `PASS=169 FAIL=0 SKIP=0`.

### Second-stage review hardening

The quality review found four test or lifecycle gaps. Focused tests were added first and produced the expected three behavior failures:

- `test_active_challenge_repr_does_not_expose_the_verification_code`;
- `test_expired_unused_challenges_are_cleaned_by_later_login_activity`;
- `test_non_string_and_unhashable_usernames_use_the_same_safe_failure`.

The implementation then added:

- a redacted `_Challenge.__repr__`;
- safe unknown-user handling for non-string and unhashable usernames;
- expired-challenge cleanup on later successful credential checks;
- regression coverage for secure 16-byte salt generation and the default 100,000 PBKDF2 iterations.

The strengthened suite now runs 18 tests and passes. Two isolated mutations are caught:

- deterministic salt: `FAILED (failures=2)`;
- default iterations reduced to 1: `FAILED (failures=1)`.
