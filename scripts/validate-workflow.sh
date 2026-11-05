#!/usr/bin/env bash
# 公共工作流门禁：对任何调用环境都运行内部 core 与顶层契约套件。
# --fast 仅运行 core（秒级），供标准模式 Verify 终验分层使用；全量仍是默认。
set -u
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1

run_id="$(python3 -B -c 'import uuid; print(uuid.uuid4().hex)')"
jsonl_path="${WORKFLOW_JSONL_PATH:-}"
if test "${WORKFLOW_OUTPUT:-}" = "jsonl" && test -z "$jsonl_path"; then
  jsonl_path=".ai-local/workflow-events.jsonl"
fi
run_started_ns="$(python3 -B -c 'import time; print(time.monotonic_ns())')"
output_parse_errors=0
emit_event() {
  test -n "$jsonl_path" || return 0
  emit_event_extra=()
  if test -n "${6:-}"; then emit_event_extra+=(--exit-code "$6"); fi
  if test -n "${7:-}"; then emit_event_extra+=(--field "command=$7"); fi
  python3 -B scripts/lib/workflow_event_cli.py "$jsonl_path" "$run_id" "${validation_layer:-standard}" "$1" "$2" "${3:-}" "${4:-}" --task-id "${WORKFLOW_TASK_ID:-}" --phase "${5:-}" ${emit_event_extra[@]+"${emit_event_extra[@]}"} >/dev/null 2>&1 || { output_parse_errors=$((output_parse_errors + 1)); printf '[INFO] output_parse_error\n' >&2; }
}
conflict_exit() {
  emit_event summary FAIL conflict 0 "" 2
  printf 'PASS=0 FAIL=1 SKIP=0\n'
  exit 2
}

fast_mode=0
standard_mode=0
archive_light=0
require_openspec_user=0
print_plan=0
standard_promoted=0
archive_files=()
forwarded_arguments=()
while test "$#" -gt 0; do
  argument="$1"
  case "$argument" in
    --fast)
      fast_mode=1
      shift
      ;;
    --standard)
      standard_mode=1
      shift
      ;;
    --archive-light)
      archive_light=1
      shift
      ;;
    --archive-files)
      shift
      while test "$#" -gt 0; do
        case "$1" in
          --*)
            break
            ;;
          *)
            archive_files+=("$1")
            shift
            ;;
        esac
      done
      ;;
    --require-openspec)
      require_openspec_user=1
      forwarded_arguments+=("$argument")
      shift
      ;;
    --output-jsonl)
      shift
      if test "$#" -eq 0 || test -z "$1"; then
        printf '[FAIL] --output-jsonl 需要路径（conflict）\n' >&2
        exit 2
      fi
      jsonl_path="$1"
      shift
      ;;
    --print-external-commands)
      # 诊断模式直接透传 core(只读、无汇总语义),不进入门禁流程。
      exec bash scripts/lib/validate-workflow-core.sh --print-external-commands
      ;;
    --print-plan)
      # 只读诊断：打印层级与契约套件执行计划后退出，不运行 core、不建锁、不写指标。
      print_plan=1
      shift
      ;;
    *)
      forwarded_arguments+=("$argument")
      shift
      ;;
  esac
done

derive_validation_layer() {
  validation_layer=standard
  if test "$fast_mode" -eq 1; then validation_layer=fast; fi
  if test "$require_openspec_user" -eq 1; then validation_layer=required; fi
  if test "$archive_light" -eq 1; then validation_layer=archive-light; fi
}
# 冲突退出前先推导 layer：事件必须如实反映请求旗标，而不是回退 standard。
derive_validation_layer

# --archive-light 与 --require-openspec 互斥（语义冲突：前者跳过契约套件、后者强制契约套件）
if test "$archive_light" -eq 1 && test "$require_openspec_user" -eq 1; then
  printf "[FAIL] --archive-light 与 --require-openspec 冲突（conflict）：归档轻量门禁与强制完整门禁不能同时启用\n" >&2
  conflict_exit
fi
if test "$fast_mode" -eq 1 && test "$require_openspec_user" -eq 1; then
  printf "[FAIL] --fast 与 --require-openspec 冲突（conflict）：快速分层不能替代强制完整门禁\n" >&2
  conflict_exit
fi
if test "$fast_mode" -eq 1 && test "$archive_light" -eq 1; then
  printf "[FAIL] --fast 与 --archive-light 冲突（conflict）：两种轻量入口语义不能叠加\n" >&2
  conflict_exit
fi
if test "$standard_mode" -eq 1 && { test "$fast_mode" -eq 1 || test "$archive_light" -eq 1 || test "$require_openspec_user" -eq 1; }; then
  printf "[FAIL] --standard 与其他验证层参数冲突（conflict）：一次调用只能选择一个层级\n" >&2
  conflict_exit
fi

if test "$standard_mode" -eq 1; then
  printf '[INFO] validation layer: standard\n'
  if test "${#archive_files[@]}" -gt 0; then
    standard_promoted=0
    for validation_file in "${archive_files[@]}"; do
      case "$validation_file" in
        AGENTS.md|CLAUDE.md|.ai/*|.codex/*|.claude/*|openspec/*|scripts/validate-workflow.sh|scripts/lib/validate-workflow-core.sh|scripts/new-openspec-change.py|scripts/ai-workflow-assets/*)
          standard_promoted=1
          printf '[INFO] standard gate promoted to --require-openspec: %s\n' "$validation_file"
          ;;
      esac
    done
    if test "$standard_promoted" -eq 1; then
      require_openspec_user=1
      forwarded_arguments+=(--require-openspec)
    fi
  fi
fi

# 升级（standard/archive 自动 promoted）后重新推导 layer。
derive_validation_layer

# --archive-light 单独使用 = 纯轻量（仅跑 core，不做 diff 分类）
#   配合 --archive-files + WORKFLOW_ARCHIVE_GATE=1 才做 diff 分类自动升级

# Archive 的 diff 分类必须在运行 core 前完成：命中语义变化时，本次调用从一开始
# 就按 required 语义执行，而不是只追加顶层契约套件。
archive_promoted=0
if test "$archive_light" -eq 1; then
  printf "[INFO] archive-light gate engaged (files=%d)\n" "${#archive_files[@]}"
  if test "${WORKFLOW_ARCHIVE_GATE:-0}" = "1" && test "${#archive_files[@]}" -gt 0; then
    diff_base="${WORKFLOW_ARCHIVE_BASE:-HEAD}"
    if ! command -v git >/dev/null 2>&1; then
      printf "[FAIL] WORKFLOW_ARCHIVE_GATE=1 但 git 不可用；无法执行 diff 分类自动升级。请安装 git 或撤销 WORKFLOW_ARCHIVE_GATE。\n" >&2
      exit 2
    fi
    diff_output=""
    if ! diff_output="$(git diff --name-only "$diff_base" -- ${archive_files[@]+"${archive_files[@]}"} 2>&1)"; then
      printf "[FAIL] Archive diff 分类失败（base=%s）：%s\n" "$diff_base" "$diff_output" >&2
      exit 2
    fi
    if test -n "$diff_output"; then
      while IFS= read -r diff_file; do
        test -n "$diff_file" && printf "[INFO] archive gate promoted to --require-openspec: %s\n" "$diff_file"
      done <<EOF
$diff_output
EOF
      archive_promoted=1
      forwarded_arguments+=(--require-openspec)
    fi
  fi
fi

# ---- standard 层契约套件增量裁剪分类（只读；无法确定时一律全量 fail-closed）----
# 仅当调用方显式提供 WORKFLOW_STANDARD_BASE 且基线后没有工作流资产变更时裁剪
# 顶层契约套件；git 缺失、diff 失败、未跟踪工作流资产、promoted 层级均保持全量。
standard_suite_pruned=0
standard_suite_reason="未提供 WORKFLOW_STANDARD_BASE"

workflow_asset_changed() {
  # 用法: workflow_asset_changed <仓库相对路径>
  # fail-closed 口径：顶层契约套件实际依赖的资产（含 README/docs 语义漂移断言、
  # 安装器入口、压力契约场景）变更即全量；scripts 整目录视为工作流资产。
  case "$1" in
    AGENTS.md|CLAUDE.md|README.md|.ai/*|.claude/*|.codex/*|.github/*|shared/*|docs/*|scripts/*)
      return 0
      ;;
    openspec/*)
      # 源仓语义：openspec 是工作流治理数据，变更即全量；
      # 安装目标语义（无 install_ai_workflow.py）：openspec 是业务数据层，可裁剪。
      test -f scripts/lib/install_ai_workflow.py && return 0
      return 1
      ;;
  esac
  return 1
}

classify_standard_suite() {
  standard_suite_pruned=0
  standard_suite_reason="未提供 WORKFLOW_STANDARD_BASE"
  test "$standard_mode" -eq 1 || return 0
  test "$require_openspec_user" -eq 0 || {
    standard_suite_reason="层级已升级为 required"
    return 0
  }
  test -n "${WORKFLOW_STANDARD_BASE:-}" || return 0
  command -v git >/dev/null 2>&1 || {
    standard_suite_reason="git 不可用"
    return 0
  }
  local standard_changed="" standard_untracked=""
  if ! standard_changed="$(git diff --name-only "$WORKFLOW_STANDARD_BASE" 2>&1)"; then
    standard_suite_reason="diff 分类失败（base=${WORKFLOW_STANDARD_BASE}）"
    return 0
  fi
  while IFS= read -r standard_file; do
    test -n "$standard_file" || continue
    if workflow_asset_changed "$standard_file"; then
      standard_suite_reason="工作流资产变更：$standard_file"
      return 0
    fi
  done <<EOF
$standard_changed
EOF
  if ! standard_untracked="$(git ls-files --others --exclude-standard 2>&1)"; then
    standard_suite_reason="未跟踪文件枚举失败"
    return 0
  fi
  while IFS= read -r standard_file; do
    test -n "$standard_file" || continue
    if workflow_asset_changed "$standard_file"; then
      standard_suite_reason="未跟踪工作流资产：$standard_file"
      return 0
    fi
  done <<EOF
$standard_untracked
EOF
  standard_suite_pruned=1
  standard_suite_reason="基线 ${WORKFLOW_STANDARD_BASE} 后无工作流资产变更"
}
classify_standard_suite

# R1：计划事件必须可审计地列明检查集合与升级条件（触发原因=layer，停止规则固定）。
contract_suite_state() {
  if test "$fast_mode" -eq 1; then
    printf 'contract-suite=not-run(fast)'
  elif test "$archive_light" -eq 1; then
    if test "$archive_promoted" -eq 1; then
      printf 'contract-suite=run(archive-gate-promoted)'
    else
      printf 'contract-suite=not-run(archive-light)'
    fi
  elif test "$standard_suite_pruned" -eq 1; then
    printf 'contract-suite=pruned(%s)' "$standard_suite_reason"
  else
    printf 'contract-suite=run(%s)' "$standard_suite_reason"
  fi
}
plan_promotion() {
  if test "$archive_promoted" -eq 1; then printf 'archive-gate→required'; return; fi
  if test "$standard_promoted" -eq 1; then printf 'standard→required'; return; fi
  printf 'none'
}

if test "$print_plan" -eq 1; then
  printf '[PLAN] layer: %s\n' "$validation_layer"
  if test "$fast_mode" -eq 1 || test "$standard_mode" -eq 1; then
    printf '[PLAN] core: run（输入指纹缓存：开）\n'
  else
    printf '[PLAN] core: run（输入指纹缓存：关）\n'
  fi
  if test "$fast_mode" -eq 1; then
    printf '[PLAN] contract-suite: not-run（fast 层不执行契约套件）\n'
  elif test "$archive_light" -eq 1; then
    if test "$archive_promoted" -eq 1; then
      printf '[PLAN] contract-suite: run（archive gate 升级）\n'
    else
      printf '[PLAN] contract-suite: not-run（archive-light）\n'
    fi
  elif test "$standard_suite_pruned" -eq 1; then
    printf '[PLAN] contract-suite: pruned（%s）\n' "$standard_suite_reason"
  else
    printf '[PLAN] contract-suite: run（%s）\n' "$standard_suite_reason"
  fi
  exit 0
fi

# plan 事件置于 print-plan 退出点之后：只读诊断模式不产生任何事件流记录。
if test -n "$jsonl_path"; then
  python3 -B scripts/lib/workflow_event_cli.py "$jsonl_path" "$run_id" "$validation_layer" plan INFO validation_plan \
    --task-id "${WORKFLOW_TASK_ID:-}" \
    --field "trigger=$validation_layer" \
    --field "checks=core=run;$(contract_suite_state)" \
    --field "promotion=$(plan_promotion)" \
    --field "stop_rule=core-failure:exit-1-diagnostic-suite-allowed" >/dev/null 2>&1 || { output_parse_errors=$((output_parse_errors + 1)); printf '[INFO] output_parse_error\n' >&2; }
fi

# 串行化同一工作树的并发校验：契约套件含 mutation,并发实例会互踩产生假失败。
if command -v flock >/dev/null 2>&1; then
  # 注意:exec 无命令时其重定向会持久作用到当前 shell,故 2>/dev/null 必须
  # 用编组限定作用域,否则锁冲突消息会被整体吞掉。
  if mkdir -p .ai-local 2>/dev/null && { exec 9>>.ai-local/.validate.lock; } 2>/dev/null; then
    if ! flock -n 9; then
      printf '[FAIL] 另一校验实例运行中，本实例退出（并发校验会互踩）\n' >&2
      exit 2
    fi
  else
    printf '锁文件不可用，降级为无锁并发保护\n' >&2
  fi
else
  printf 'flock 不可用，降级为无锁并发保护\n' >&2
fi

core_output="$(mktemp)"
contract_output="$(mktemp)"
cleanup() {
  rm -f -- "$core_output" "$contract_output"
}
finalize() {
  local code="$?"
  local now duration=0
  now="$(python3 -B -c 'import time; print(time.monotonic_ns())')"
  duration=$(( (now - run_started_ns) / 1000000 ))
  if test "$code" -eq 0; then
    emit_event phase PASS "exit_code_0" "$duration" "$validation_layer"
    emit_event summary PASS "exit_code_0" "$duration" "" "$code"
  else
    emit_event phase FAIL "exit_code_$code" "$duration" "$validation_layer"
    emit_event summary FAIL "exit_code_$code" "$duration" "" "$code"
  fi
  if test -n "$jsonl_path" || test -d .ai-local; then
    METRICS_DIR="${METRICS_DIR:-.ai-local/metrics}" METRICS_RUN_ID="$run_id" METRICS_DURATION="$duration" \
      METRICS_LAYER="$validation_layer" METRICS_PASS="${pass_count:-0}" \
      METRICS_FAIL="${fail_count:-0}" METRICS_SKIP="${skip_count:-0}" \
      METRICS_CACHE_REUSED="${cache_reused_count:-0}" METRICS_PARSE_ERRORS="${output_parse_errors:-0}" \
      python3 -B - <<'PY' >/dev/null 2>&1 || printf '[INFO] metrics_write_failed\n' >&2
import json, os, tempfile
from pathlib import Path
d=Path(os.environ["METRICS_DIR"])
try:
    d.mkdir(parents=True, exist_ok=True)
    payload={"schema_version":1,"run_id":os.environ["METRICS_RUN_ID"],"layer":os.environ["METRICS_LAYER"],"duration_ms":int(os.environ.get("METRICS_DURATION","0")),"counts":{"PASS":int(os.environ["METRICS_PASS"]),"FAIL":int(os.environ["METRICS_FAIL"]),"SKIP":int(os.environ["METRICS_SKIP"])},"agent_allowed":0,"agent_denied":0,"cache_reused":int(os.environ["METRICS_CACHE_REUSED"]),"output_parse_errors":int(os.environ["METRICS_PARSE_ERRORS"])}
    if os.environ.get('WORKFLOW_TASK_ID'):
        payload['task_id'] = os.environ['WORKFLOW_TASK_ID']
    fd,tmp=tempfile.mkstemp(prefix=".metrics.",dir=d); os.close(fd)
    with open(tmp,"w",encoding="utf-8") as h: json.dump(payload,h,sort_keys=True); h.write("\n")
    os.replace(tmp,d/(payload["run_id"]+".json"))
except (OSError, ValueError, TypeError):
    raise SystemExit(1)
PY
  fi
  cleanup
  exit "$code"
}
trap finalize EXIT

# 顶层契约套件只在此函数内出现一次,便于静态检查与 mutation 测试。
run_contract_suite() {
  if test "${WORKFLOW_TEST_JOBS:-0}" = "1"; then
    python3 -B -m unittest -v scripts.tests.test_validate_workflow >"$contract_output" 2>&1
  else
    python3 -B scripts/tests/run_validate_workflow_parallel.py --module scripts.tests.test_validate_workflow >"$contract_output" 2>&1
  fi
}

# 契约套件内部设计性跳过（源仓专属能力，如 CI / pre-push 钩子）必须
# 在汇总前逐条可见；不计入顶层 SKIP 字段。失败/解析错误直接 fail-closed。
render_contract_suite_skips() {
  contract_skip_status=0
  contract_skips="$(grep -c '\.\.\. skipped' "$contract_output")" || contract_skip_status=$?
  case "$contract_skip_status" in
    0|1)
      case "$contract_skips" in
        ""|*[!0-9]*)
          printf "[FAIL] 契约套件内部跳过计数解析失败（结果必须为非负整数）\n"
          fail_count=$((fail_count + 1))
          contract_skips=0
          ;;
      esac
      ;;
    *)
      printf "[FAIL] 契约套件内部跳过计数解析失败（grep exit %d）\n" "$contract_skip_status"
      fail_count=$((fail_count + 1))
      contract_skips=0
      ;;
  esac
  if test "$contract_skips" -gt 0; then
    printf "  契约套件内部设计性跳过 %d 项（源仓专属能力；不影响门禁计数）:\n" "$contract_skips"
    sed -n '/\.\.\. skipped/{s/^/  - /;p;}' "$contract_output"
    # $? 必须紧跟 sed 捕获其退出码；本行与 sed 之间不得插入任何命令。
    contract_skip_render_status=$?
    if test "$contract_skip_render_status" -ne 0; then
      printf "[FAIL] 契约套件内部跳过明细渲染失败（sed exit %d）\n" "$contract_skip_render_status"
      fail_count=$((fail_count + 1))
    fi
  fi
}

report_contract_suite_success() {
  contract_count="$(sed -n 's/^Ran \([1-9][0-9]*\) tests\{0,1\}\( in .*\)\{0,1\}$/\1/p' "$contract_output" | tail -1)"
  if test -n "$contract_count"; then
    printf "[PASS] 工作流顶层契约测试（%s tests）\n" "$contract_count"
    return 0
  fi
  printf "[FAIL] 契约套件用例计数解析失败\n"
  sed "s/^/  /" "$contract_output"
  return 1
}

# R3：core check 事件的 command/exit_code 取自实际被包装的命令与其退出码。
core_command="scripts/lib/validate-workflow-core.sh"
if test "${#forwarded_arguments[@]}" -gt 0; then
  core_command="$core_command ${forwarded_arguments[*]}"
fi
core_status=0
if test "$fast_mode" -eq 1 || { test "$standard_mode" -eq 1 && test "$require_openspec_user" -eq 0; }; then
  WORKFLOW_FAST_CACHE=1 bash scripts/lib/validate-workflow-core.sh ${forwarded_arguments[@]+"${forwarded_arguments[@]}"} >"$core_output" 2>&1 || core_status=$?
else
  # 非 fast/standard 门禁（含 promoted 为 required 的调用）必须实际执行：
  # 显式关闭外部可能继承的缓存开关，维持 required 层"禁止读写验证缓存"契约。
  WORKFLOW_FAST_CACHE=0 bash scripts/lib/validate-workflow-core.sh ${forwarded_arguments[@]+"${forwarded_arguments[@]}"} >"$core_output" 2>&1 || core_status=$?
fi
internal_result="$(sed -n "s/^INTERNAL_RESULT PASS=[0-9][0-9]* FAIL=[0-9][0-9]* SKIP=[0-9][0-9]*$/&/p" "$core_output" | tail -1)"
sed "/^INTERNAL_RESULT PASS=[0-9][0-9]* FAIL=[0-9][0-9]* SKIP=[0-9][0-9]*$/d" "$core_output"

# R4：缓存沿用计数来自 core 输出的实际"指纹…沿用"行（实测值，非常量）。
cache_reused_count=0
cache_reused_count="$(grep -c '未变，沿用' "$core_output")" || cache_reused_count=0

if test -n "$internal_result"; then
  counts="${internal_result#INTERNAL_RESULT }"
  pass_field="${counts%% *}"
  counts="${counts#* }"
  fail_field="${counts%% *}"
  skip_field="${counts#* }"
  pass_count="${pass_field#PASS=}"
  fail_count="${fail_field#FAIL=}"
  skip_count="${skip_field#SKIP=}"
  if test "$fail_count" -gt 0; then
    emit_event check FAIL core_failed "" "" "$core_status" "$core_command"
  else
    emit_event check PASS core_passed "" "" "$core_status" "$core_command"
  fi
else
  pass_count=0
  fail_count=1
  skip_count=0
  printf "[FAIL] 内部验证 core 未返回可解析结果\n"
  emit_event check FAIL core_result_unparseable "" "" "$core_status" "$core_command"
fi

if test "$fail_count" -gt 0 || test "$core_status" -ne 0; then
  if test "$fast_mode" -eq 0 && test "$archive_light" -eq 0 && test "$standard_suite_pruned" -eq 0 && test "$core_status" -eq 1; then
    # 门禁立即终止（exit 1）；随包契约套件仅作诊断执行（不参与门禁计数），
    # 事件必须如实记录实际执行（F2），不得谎报 SKIP。
    emit_event check INFO diagnostic_suite_run
    if run_contract_suite; then
      report_contract_suite_success || true
    else
      printf "[FAIL] 工作流顶层契约测试（core failed）\n" >&2
    fi
  else
    emit_event check SKIP dependent_layer_blocked
    printf '[SKIP] 依赖层因 core 失败未执行\n'
  fi
  printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
  exit 1
fi

# 参数错误保持 CLI 退出码 2；有效调用永远继续运行顶层契约套件。
if test "$core_status" -eq 2; then
  printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
  exit 2
fi

if test "$fast_mode" -eq 1; then
  printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
  if test "$fail_count" -gt 0 || test "$core_status" -ne 0; then
    exit 1
  fi
  exit 0
fi

# 归档轻量门禁：跳过顶层契约套件，core 结果已足；diff 分类自动升级如下。
# 1) WORKFLOW_ARCHIVE_GATE=1 + --archive-files 非空 + git diff --name-only <base> -- <files> 非空 → 改跑契约套件
if test "$archive_light" -eq 1; then
  if test "$archive_promoted" -eq 1; then
    # 改跑契约套件（与正常路径同一段）
    if run_contract_suite; then
      if report_contract_suite_success; then
        pass_count=$((pass_count + 1))
      else
        fail_count=$((fail_count + 1))
      fi
    else
      printf "[FAIL] 工作流顶层契约测试（promoted）\n"
      fail_count=$((fail_count + 1))
      sed "s/^/  /" "$contract_output"
    fi
    render_contract_suite_skips
  fi
  printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
  if test "$fail_count" -gt 0 || test "$core_status" -ne 0; then
    exit 1
  fi
  exit 0
fi

if test "$standard_suite_pruned" -eq 1; then
  printf '[INFO] 工作流顶层契约测试裁剪（standard：%s）\n' "$standard_suite_reason"
  emit_event check INFO contract_suite_pruned
  printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
  if test "$fail_count" -gt 0 || test "$core_status" -ne 0; then
    exit 1
  fi
  exit 0
fi

if run_contract_suite; then
  if report_contract_suite_success; then
    pass_count=$((pass_count + 1))
  else
    fail_count=$((fail_count + 1))
  fi
else
  printf "[FAIL] 工作流顶层契约测试\n"
  fail_count=$((fail_count + 1))
  sed "s/^/  /" "$contract_output"
fi
render_contract_suite_skips

printf "PASS=%d FAIL=%d SKIP=%d\n" "$pass_count" "$fail_count" "$skip_count"
if test "$fail_count" -gt 0 || test "$core_status" -ne 0; then
  exit 1
fi
exit 0
