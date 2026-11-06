import json
import os
import subprocess
import tempfile
import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts" / "validate-workflow.sh"
sys.path.insert(0, str(ROOT / 'scripts/lib'))
from workflow_events import summarize_task_events


class WorkflowWrapperOutputTests(unittest.TestCase):
    def test_task_id_propagates_to_events_and_metrics_on_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            metrics = Path(tmp) / 'metrics'
            env = {**os.environ, 'WORKFLOW_JSONL_PATH':str(path), 'WORKFLOW_TASK_ID':'task-2', 'METRICS_DIR':str(metrics)}
            result = subprocess.run(['bash', str(WRAPPER), '--fast', '--unknown-test-option'], cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertTrue(rows)
            self.assertTrue(all(row.get('task_id') == 'task-2' for row in rows))
            records = list(metrics.glob('*.json'))
            self.assertEqual(1, len(records))
            self.assertEqual('task-2', json.loads(records[0].read_text())['task_id'])
            self.assertEqual('summary', rows[-1]['event'])
            self.assertEqual('phase', rows[-2]['event'])
            self.assertEqual('fast', rows[-2]['phase'])
            summary = summarize_task_events(path, 'task-2')
            self.assertEqual(1, len(summary['phases']))
            self.assertEqual(rows[-1]['duration_ms'], summary['total_duration_ms'])

    def test_jsonl_contains_plan_check_summary_and_human_summary_is_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            env = os.environ.copy()
            env["WORKFLOW_JSONL_PATH"] = str(path)
            proc = subprocess.run(
                ["bash", str(WRAPPER), "--fast"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertIn("PASS=", proc.stdout)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(rows[0]["event"], "plan")
            self.assertIn("check", {row["event"] for row in rows})
            self.assertEqual(rows[-1]["event"], "summary")

    def test_conflicting_layers_fail_before_core(self):
        proc = subprocess.run(
            ["bash", str(WRAPPER), "--fast", "--require-openspec"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("冲突", proc.stderr)



    def test_summary_events_carry_numeric_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            env = {**os.environ, 'WORKFLOW_JSONL_PATH': str(path)}
            ok = subprocess.run(['bash', str(WRAPPER), '--fast'], cwd=ROOT, env=env,
                                capture_output=True, text=True, check=False)
            self.assertEqual(0, ok.returncode, msg=ok.stdout)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            summary_ok = [row for row in rows if row['event'] == 'summary'][-1]
            self.assertEqual(0, summary_ok['exit_code'])
            conflict = subprocess.run(['bash', str(WRAPPER), '--fast', '--require-openspec'],
                                      cwd=ROOT, env=env, capture_output=True, text=True,
                                      check=False)
            self.assertEqual(2, conflict.returncode)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            summary_conflict = [row for row in rows if row['event'] == 'summary'][-1]
            self.assertEqual(2, summary_conflict['exit_code'])

    def test_conflict_summary_reports_derived_layer(self):
        # 冲突退出的事件 layer 必须按请求旗标推导（fast→required→archive-light 顺序），
        # 而不是无条件回退 standard。
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            env = {**os.environ, 'WORKFLOW_JSONL_PATH': str(path)}
            cases = (
                (['--fast', '--require-openspec'], 'required'),
                (['--fast', '--archive-light'], 'archive-light'),
            )
            for flags, expected in cases:
                with self.subTest(flags=flags):
                    proc = subprocess.run(['bash', str(WRAPPER), *flags], cwd=ROOT, env=env,
                                          capture_output=True, text=True, check=False)
                    self.assertEqual(2, proc.returncode)
                    rows = [json.loads(line) for line in path.read_text().splitlines()]
                    summary = [row for row in rows if row['event'] == 'summary'][-1]
                    self.assertEqual(expected, summary['layer'])

    def test_plan_event_lists_trigger_checks_promotion_and_stop_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            env = {**os.environ, 'WORKFLOW_JSONL_PATH': str(path)}
            proc = subprocess.run(['bash', str(WRAPPER), '--fast'], cwd=ROOT, env=env,
                                  capture_output=True, text=True, check=False)
            self.assertEqual(0, proc.returncode, msg=proc.stdout)
            plan = json.loads(path.read_text().splitlines()[0])
            self.assertEqual('plan', plan['event'])
            self.assertEqual('fast', plan['trigger'])
            self.assertIn('core=run', plan['checks'])
            self.assertIn('contract-suite', plan['checks'])
            self.assertEqual('none', plan['promotion'])
            self.assertIn('exit-1', plan['stop_rule'])

    def test_core_check_event_carries_command_and_exit_code(self):
        # R3：适用时事件包含 command 与 exit_code——core check 事件描述被包装的实际命令。
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            env = {**os.environ, 'WORKFLOW_JSONL_PATH': str(path)}
            proc = subprocess.run(['bash', str(WRAPPER), '--fast'], cwd=ROOT, env=env,
                                  capture_output=True, text=True, check=False)
            self.assertEqual(0, proc.returncode, msg=proc.stdout)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            core_checks = [row for row in rows
                           if row['event'] == 'check' and row.get('reason_code') == 'core_passed']
            self.assertEqual(1, len(core_checks))
            self.assertIn('validate-workflow-core.sh', core_checks[0]['command'])
            self.assertEqual(0, core_checks[0]['exit_code'])

    def test_output_jsonl_argument_streams_events_without_env(self):
        # --output-jsonl 显式参数无须 WORKFLOW_OUTPUT=jsonl 即可输出事件流。
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'out.jsonl'
            env = {k: v for k, v in os.environ.items()
                   if k not in ('WORKFLOW_OUTPUT', 'WORKFLOW_JSONL_PATH')}
            proc = subprocess.run(['bash', str(WRAPPER), '--fast', '--output-jsonl', str(path)],
                                  cwd=ROOT, env=env, capture_output=True, text=True,
                                  check=False)
            self.assertEqual(0, proc.returncode, msg=proc.stdout)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertGreaterEqual(len(rows), 3)
            self.assertEqual('summary', rows[-1]['event'])
            self.assertIn('PASS=', proc.stdout.splitlines()[-1])


    def test_output_jsonl_rejects_option_as_path(self):
        # CQ-8：--output-jsonl 后跟选项时必须报冲突，不得把 --fast 当路径静默改层级。
        proc = subprocess.run(
            ["bash", str(WRAPPER), "--output-jsonl", "--fast"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(2, proc.returncode)
        self.assertIn("需要路径", proc.stderr)

    def test_print_plan_and_plan_event_agree_on_contract_suite_state(self):
        # CQ-6：--print-plan 文本与 plan 事件的检查集合/升级条件必须同源一致。
        import re
        plan = subprocess.run(
            ["bash", str(WRAPPER), "--fast", "--print-plan"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, plan.returncode, msg=plan.stdout)
        match = re.search(r"\[PLAN\] contract-suite: (.+)$", plan.stdout, re.M)
        self.assertIsNotNone(match, plan.stdout)
        value = match.group(1)
        self.assertIn("[PLAN] promotion:", plan.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            env = {**os.environ, 'WORKFLOW_JSONL_PATH': str(path)}
            proc = subprocess.run(['bash', str(WRAPPER), '--fast'], cwd=ROOT, env=env,
                                  capture_output=True, text=True, check=False)
            self.assertEqual(0, proc.returncode, msg=proc.stdout)
            plan_event = json.loads(path.read_text().splitlines()[0])
            self.assertIn(f"contract-suite={value}", plan_event["checks"])

    def test_real_core_warm_cache_counts_cache_reuse(self):
        # CQ-4：cache_reused 指标与真实 core 缓存沿用输出耦合的回归锁——
        # core 沿用文案变化时本测试变红，指标不会无声归零。
        with tempfile.TemporaryDirectory() as tmp:
            metrics = Path(tmp) / 'metrics'
            env = {**os.environ, 'METRICS_DIR': str(metrics)}
            for _ in range(2):
                proc = subprocess.run(['bash', str(WRAPPER), '--fast'], cwd=ROOT,
                                      env=env, capture_output=True, text=True,
                                      check=False)
                self.assertEqual(0, proc.returncode, msg=proc.stdout)
            records = sorted(metrics.glob('*.json'))
            self.assertEqual(2, len(records))
            # CQ-10：记录文件名是随机 uuid，字典序与运行顺序无关（冷缓存首跑
            # cache_reused=0 时旧 records[-1] 断言约半数概率取错记录）；断言对顺序不敏感。
            payloads = [json.loads(record.read_text(encoding='utf-8')) for record in records]
            self.assertGreaterEqual(max(item['cache_reused'] for item in payloads), 1)


if __name__ == "__main__":
    unittest.main()
