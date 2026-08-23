#!/usr/bin/env bash
# 公共工作流门禁：对任何调用环境都运行内部 core 与顶层契约套件。
set -u
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1

core_output="$(mktemp)"
contract_output="$(mktemp)"
cleanup() {
  rm -f -- "$core_output" "$contract_output"
}
trap cleanup EXIT

core_status=0
bash scripts/lib/validate-workflow-core.sh "$@" >"$core_output" 2>&1 || core_status=$?
internal_result="$(sed -n "s/^INTERNAL_RESULT PASS=[0-9][0-9]* FAIL=[0-9][0-9]* SKIP=[0-9][0-9]*$/&/p" "$core_output" | tail -1)"
sed "/^INTERNAL_RESULT PASS=[0-9][0-9]* FAIL=[0-9][0-9]* SKIP=[0-9][0-9]*$/d" "$core_output"

if test -n "$internal_result"; then
  counts="${internal_result#INTERNAL_RESULT }"
  pass_field="${counts%% *}"
  counts="${counts#* }"
  fail_field="${counts%% *}"
  skip_field="${counts#* }"
  pass_count="${pass_field#PASS=}"
  fail_count="${fail_field#FAIL=}"
  skip_count="${skip_field#SKIP=}"
else
  pass_count=0
  fail_count=1
  skip_count=0
  printf "[FAIL] 内部验证 core 未返回可解析结果\n"
fi

# 参数错误保持 CLI 退出码 2；有效调用永远继续运行顶层契约套件。
if test "$core_status" -eq 2; then
  printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
  exit 2
fi

if python3 -B -m unittest -v scripts.tests.test_validate_workflow >"$contract_output" 2>&1; then
  printf "[PASS] 工作流顶层契约测试\n"
  pass_count=$((pass_count + 1))
else
  printf "[FAIL] 工作流顶层契约测试\n"
  fail_count=$((fail_count + 1))
  sed "s/^/  /" "$contract_output"
fi

printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
if test "$fail_count" -gt 0 || test "$core_status" -ne 0; then
  exit 1
fi
exit 0
