import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import workflow_events


class WorkflowEventsTest(unittest.TestCase):
    def test_task_phase_cli_and_legacy_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/lib/workflow_event_cli.py'), str(path), 'r', 'standard', 'phase', 'PASS', 'ok', '12', '--task-id', 'task', '--phase', 'build'], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            with path.open('a') as stream:
                for event in [{'event':'summary','task_id':'task','phase':'build','duration_ms':99}, {'event':'phase','task_id':'other','phase':'build','duration_ms':20}, {'event':'check','duration_ms':1}]:
                    stream.write(json.dumps(event) + '\n')
            summary = workflow_events.summarize_task_events(path, 'task')
            self.assertEqual(12, summary['total_duration_ms'])
            self.assertEqual('build', summary['phases'][0]['phase'])

    def test_task_writer_and_invalid_phase_records(self):
        writer = workflow_events.EventWriter(None, 'r', 'standard', task_id='task')
        self.assertEqual('task', writer.emit('plan', 'INFO')['task_id'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'events.jsonl'
            for bad in ['{broken', '[]', json.dumps({'event':'phase','task_id':'task','phase':'build','status':'PASS','duration_ms':-1}), json.dumps({'event':'phase','task_id':'task','phase':'build','status':'PASS','duration_ms':True}), json.dumps({'event':'phase','task_id':'task','phase':3,'status':'PASS','duration_ms':1})]:
                path.write_text(bad + '\n')
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    workflow_events.summarize_task_events(path, 'task')

    def test_event_has_required_fields_and_jsonl_is_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            writer = workflow_events.EventWriter(path, "run-1", "fast")
            event = writer.emit("check", "PASS", reason_code="ok", duration_ms=3)
            writer.close()
            self.assertEqual(event["schema_version"], 1)
            self.assertEqual(event["run_id"], "run-1")
            self.assertEqual(event["layer"], "fast")
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(rows[0]["event"], "check")
            self.assertEqual(rows[0]["status"], "PASS")

    def test_invalid_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            writer = workflow_events.EventWriter(Path(tmp) / "events.jsonl", "r", "standard")
            with self.assertRaises(ValueError):
                writer.emit("check", "UNKNOWN")
            writer.close()

    def test_metrics_write_failure_is_nonfatal(self):
        result = workflow_events.write_metrics(Path("/dev/null"), {"run_id": "r"})
        self.assertFalse(result.ok)
        self.assertEqual(result.reason_code, "metrics_write_failed")


if __name__ == "__main__":
    unittest.main()
