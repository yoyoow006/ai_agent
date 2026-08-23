# 登录随机验证测试项目实施计划

## 目标与全局约束

- 在 `projects/test-login/` 新增一个离线可运行的 Python 3.8 标准库测试项目，实现注册、密码登录、随机 6 位验证码、一次性验证和会话 token。
- 项目仅用于本地测试，不声明生产可用；不接入网络、数据库、短信、邮件或外部认证服务。
- 不修改安装器、工作流资产、`.ai/kb/projects/registry.json` 或共享项目登记事实。
- 认证行为是运行时代码，必须执行 TDD：先写测试并确认按预期失败，再实现最小功能并跑绿。
- 严格模式默认隔离 worktree；实施时先在主工作区提交四件套与计划到 feature 分支，再切回 `main` 挂载 `.worktrees/add-test-login-project`。

## 任务 1：建立 feature 分支与隔离 worktree

### Preconditions

- `git status --short --branch` 只显示本变更四件套与计划。
- `git remote -v` 为空或仅存在用户明确配置的远端；本任务不推送。

### Commands

```bash
git switch -c feature/add-test-login-project
git add openspec/changes/add-test-login-project openspec/plan/add-test-login-project.md
git diff --cached --name-status
git diff --cached --check
git commit -m "chore: plan test login project"
git switch main
git worktree add .worktrees/add-test-login-project feature/add-test-login-project
cd .worktrees/add-test-login-project
git status --short --branch
```

### Expected

- feature 分支只提交本变更流程产物。
- 隔离 worktree 检出 `feature/add-test-login-project`。
- 主工作区不承载实现改动。

## 任务 2：创建测试先行的项目骨架

### Create

- `projects/test-login/tests/__init__.py`
- `projects/test-login/tests/test_login_service.py`
- `projects/test-login/tests/test_cli.py`

### Test contract

`tests/test_login_service.py` 必须先覆盖：

1. 注册校验：有效注册、非法用户名、弱密码、重复用户名；内部记录不保存明文密码，且每用户有独立随机盐与 PBKDF2 参数。
2. 密码错误路径：未知用户与错误密码抛出相同类型和相同安全消息；密码错误时不创建验证挑战。
3. 随机验证码：默认生成 `000000` 至 `999999` 的 6 位字符串；mock `secrets.randbelow` 证明使用密码学安全随机源；同批多次生成存在多个不同结果。
4. 生命周期：有效期内正确验证码返回 token；验证成功后挑战一次性消费；错误验证码递增计数；5 次错误后挑战失效；注入时钟达到 300 秒后过期。
5. Session token：登录成功返回非空 token；`validate_token` 通过；未知 token 失败。

`tests/test_cli.py` 必须先覆盖：

1. `demo --auto` 捕获随机验证码并完成成功登录。
2. `demo --auto --reject` 提交错误验证码并返回非零。
3. CLI 输出不包含用户密码。

### Red verification

```bash
cd /home/yoyoo/wksoft/ai_agent_install/.worktrees/add-test-login-project/projects/test-login
python3 -B -m unittest discover -v -s tests -p 'test_*.py'
```

### Expected red

- 测试因 `login_service` 或 CLI 模块尚不存在而失败。
- 失败原因是行为尚未实现，而不是环境或测试语法错误。
- 记录完整失败输出后再实现。

## 任务 3：实现登录服务核心

### Create

- `projects/test-login/login_service.py`

### Public interface

```python
class LoginService:
    def __init__(
        self,
        *,
        clock=None,
        delivery=None,
        code_generator=None,
        challenge_generator=None,
        token_generator=None,
        pbkdf2_iterations=100_000,
    ) -> None: ...

    def register(self, username: str, password: str) -> None: ...
    def begin_login(self, username: str, password: str) -> str: ...
    def complete_login(self, challenge_id: str, code: str) -> str: ...
    def validate_token(self, token: str) -> bool: ...
```

### Implementation contract

- 用户名仅允许 3–32 个 ASCII 字母、数字、下划线、点或短横线。
- 密码长度 10–128，至少包含字母和数字。
- 密码哈希使用每用户 16 字节随机盐、PBKDF2-HMAC-SHA256、默认至少 100,000 次迭代和 `hmac.compare_digest` 比较。
- 未知用户也执行一次等参数 dummy PBKDF2 计算，降低用户枚举时间差。
- `AuthenticationError` 对未知用户和错误密码使用同一安全消息。
- 验证码使用 `secrets.randbelow(1_000_000)` 格式化为 6 位，有效期 300 秒，最多 5 次错误，成功或耗尽后立即删除挑战。
- Challenge id 与 session token 分别使用 `secrets.token_urlsafe`。
- 验证码只传给 `VerificationDelivery` 通道，不通过 API 返回。

### Green verification

```bash
cd /home/yoyoo/wksoft/ai_agent_install/.worktrees/add-test-login-project/projects/test-login
python3 -B -m unittest discover -v -s tests -p 'test_*.py'
```

### Expected green

- 任务 2 写入的全部测试通过。
- 无意外警告或额外失败。

## 任务 4：实现命令行演示与 README

### Create

- `projects/test-login/cli.py`
- `projects/test-login/README.md`

### CLI contract

```bash
python3 cli.py demo                 # 本地交互演示，打印验证码并等待输入
python3 cli.py demo --auto          # 自动读取内存通道中的验证码并完成登录
python3 cli.py demo --auto --reject # 故意提交错误验证码，演示失败路径
```

- `demo` 每次创建内存态演示用户，不持久化。
- 默认通道在本地终端打印验证码。
- `--auto` 使用内存捕获通道。
- `--reject` 返回非零并输出固定安全错误，不泄露密码或验证码。
- README 必须说明运行测试、成功演示、失败演示和生产使用边界。

### Verification

```bash
cd /home/yoyoo/wksoft/ai_agent_install/.worktrees/add-test-login-project/projects/test-login
python3 -B -m unittest discover -v -s tests -p 'test_*.py'
python3 -B -m py_compile login_service.py cli.py tests/test_login_service.py tests/test_cli.py
python3 cli.py demo --auto
set +e
python3 cli.py demo --auto --reject
status=$?
set -e
test "$status" -ne 0
```

### Expected

- 单元测试全部通过。
- 语法编译通过。
- `demo --auto` 退出码 0，输出 session token。
- `demo --auto --reject` 退出码非 0，输出固定失败信息。

## 任务 5：任务级审查

### Freeze

```bash
cd /home/yoyoo/wksoft/ai_agent_install/.worktrees/add-test-login-project
python3 .ai/tools/review_manifest.py freeze \
  --change add-test-login-project \
  --workspace "$PWD" \
  --repo-spec "$PWD::main" \
  --output .ai-local/reviews/add-test-login-project/task-1.json
```

### Review

- 独立 reviewer 在读取范围前和结论前分别运行 manifest verify。
- 审查范围为 `main..feature/add-test-login-project`。
- 必须覆盖 TDD 红—绿证据、密码哈希、用户枚举防护、验证码随机性与生命周期、token 生成、CLI 边界，以及是否误改安装器或项目登记层。
- Critical/Important 必须最小修复并做 delta 复审。

## 任务 6：严格终验

### Project verification

```bash
cd /home/yoyoo/wksoft/ai_agent_install/.worktrees/add-test-login-project/projects/test-login
python3 -B -m unittest discover -v -s tests -p 'test_*.py'
python3 -B -m py_compile login_service.py cli.py tests/test_login_service.py tests/test_cli.py
python3 cli.py demo --auto
```

### Repository verification

```bash
cd /home/yoyoo/wksoft/ai_agent_install/.worktrees/add-test-login-project
git diff --check
git status --short --branch
openspec validate add-test-login-project --strict --no-interactive
bash scripts/validate-workflow.sh --require-openspec
```

### Expected

- 项目测试、编译和成功演示全部通过。
- `git diff --check` 退出码 0。
- OpenSpec strict 校验通过。
- 严格工作流 required 门禁末尾 `FAIL=0`。

## 任务 7：双阶段 Verify

- 冻结最终 manifest。
- Reviewer A 只审规格符合性：逐条核对 Requirement/Scenario、本地演示边界、测试覆盖和生产不适用边界。
- Reviewer B 只审代码质量与安全：密码存储、用户枚举、随机性、验证码生命周期、CLI 输出和测试有效性。
- 两个 reviewer 读取范围前和结论前均执行 manifest verify；任一 `STALE` 立即停止。

## 任务 8：归档

- 双阶段 Verify 无未决 Critical/Important 后：
  - 合并 `test-login-verification` delta 到主规格；
  - 将变更目录移入 `openspec/archive/add-test-login-project/`；
  - 将严格计划移为归档目录内 `plan.md`；
  - proposal 状态置为`已归档`；
  - 提交归档结果；
  - 复跑 `openspec validate --all --no-interactive` 与 `bash scripts/validate-workflow.sh --require-openspec`。
- 最终汇报必须明确：项目可本地运行，但不适合未经加固直接用于生产。
