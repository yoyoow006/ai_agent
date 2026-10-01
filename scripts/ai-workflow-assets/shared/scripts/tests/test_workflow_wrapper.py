import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts" / "validate-workflow.sh"


class WorkflowWrapperOutputTests(unittest.TestCase):
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
