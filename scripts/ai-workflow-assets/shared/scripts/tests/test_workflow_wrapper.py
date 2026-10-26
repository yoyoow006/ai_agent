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



if __name__ == "__main__":
    unittest.main()
