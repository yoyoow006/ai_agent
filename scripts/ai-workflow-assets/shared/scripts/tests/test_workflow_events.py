import json
import os
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
import workflow_events


class WorkflowEventsTest(unittest.TestCase):
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
