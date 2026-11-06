import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.lib.agent_dispatch import gate_dispatch


ROOT = Path(__file__).resolve().parents[2]


def request(**overrides):
    value = {
        "role": "test_worker",
        "boundary": ["scripts/tests/test_agent_dispatch.py"],
        "acceptance_command": "python3 -B -m unittest -v scripts.tests.test_agent_dispatch",
        "shared_writes": False,
        "sequential_dependency": False,
        "task_size": "large",
        "layer": "required",
        "existing_boundaries": [],
    }
    value.update(overrides)
    return value


class AgentDispatchTests(unittest.TestCase):
    def test_valid_test_worker_is_allowed(self):
        result = gate_dispatch(request())
        self.assertEqual(result["dispatch"], "allowed")
        self.assertEqual(result["reason_code"], "allowed")
        self.assertEqual(result["role"], "test_worker")

    def test_missing_independent_boundary_is_denied(self):
        result = gate_dispatch(request(boundary=[]))
        self.assertEqual(result["dispatch"], "denied")
        self.assertEqual(result["reason_code"], "independent_boundary_required")
        self.assertEqual(result["next_action"], "主会话处理")

    def test_overlapping_boundary_is_denied(self):
        result = gate_dispatch(
            request(existing_boundaries=["scripts/tests/test_agent_dispatch.py"])
        )
        self.assertEqual(result["dispatch"], "denied")
        self.assertEqual(result["reason_code"], "boundary_overlap")

    def test_role_mismatch_is_denied(self):
        result = gate_dispatch(request(role="writer"))
        self.assertEqual(result["dispatch"], "denied")
        self.assertEqual(result["reason_code"], "role_mismatch")

    def test_invalid_command_is_denied(self):
        result = gate_dispatch(request(acceptance_command="python3\n-r bad"))
        self.assertEqual(result["dispatch"], "denied")
        self.assertEqual(result["reason_code"], "acceptance_command_invalid")

    def test_shared_write_or_order_dependency_is_denied(self):
        for field in ("shared_writes", "sequential_dependency"):
            with self.subTest(field=field):
                result = gate_dispatch(request(**{field: True}))
                self.assertEqual(result["dispatch"], "denied")
                self.assertEqual(result["reason_code"], "shared_state_conflict")

    def test_shared_state_flags_are_required_booleans(self):
        for field in ("shared_writes", "sequential_dependency"):
            missing = request()
            del missing[field]
            result = gate_dispatch(missing)
            self.assertEqual(result["reason_code"], "request_invalid")
            for value in (None, "false", 0, 1):
                result = gate_dispatch(request(**{field: value}))
                self.assertEqual(result["reason_code"], "request_invalid")

    def test_layer_task_size_and_boundary_schema_are_strict(self):
        for values in (
            {"layer": "unknown"},
            {"task_size": "medium"},
            {"boundary": ["../outside"]},
            {"boundary": ["/absolute/path"]},
            {"boundary": [123]},
        ):
            with self.subTest(values=values):
                result = gate_dispatch(request(**values))
                self.assertEqual(result["reason_code"], "request_invalid")

    def test_fast_and_standard_small_tasks_are_exempt(self):
        for values in ({"layer": "fast"}, {"task_size": "small", "layer": "standard"}):
            with self.subTest(values=values):
                result = gate_dispatch(request(**values))
                self.assertEqual(result["dispatch"], "denied")
                self.assertEqual(result["reason_code"], "task_scope_exempt")

    def test_cli_emits_one_stable_json_object(self):
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.lib.agent_dispatch"],
            input=json.dumps(request()) + "\n",
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(len(proc.stdout.splitlines()), 1)
        output = json.loads(proc.stdout)
        self.assertEqual(output["dispatch"], "allowed")
        self.assertEqual(output["reason_code"], "allowed")

    def test_cli_can_emit_dispatch_event(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            proc = subprocess.run(
                [sys.executable, "-m", "scripts.lib.agent_dispatch", "--event-path", str(path)],
                input=json.dumps(request()) + "\n", cwd=ROOT, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(proc.returncode, 0)
            event = json.loads(path.read_text().splitlines()[0])
            self.assertEqual(event["event"], "dispatch")
            self.assertEqual(event["dispatch"], "allowed")


    def test_result_mode_emits_validated_result_event(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            for exit_code, expected_status in ((0, "PASS"), (1, "FAIL")):
                with self.subTest(exit_code=exit_code):
                    payload = {
                        "exit_code": exit_code,
                        "failed": exit_code,
                        "unverified_scope": "无",
                        "residual_risk": "无",
                    }
                    proc = subprocess.run(
                        [sys.executable, "-m", "scripts.lib.agent_dispatch", "result",
                         "--event-path", str(path), "--run-id", "run-1", "--layer", "required"],
                        input=json.dumps(payload) + "\n", cwd=ROOT, text=True,
                        capture_output=True, check=False,
                    )
                    self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
                    event = json.loads(path.read_text().splitlines()[-1])
                    self.assertEqual(event["event"], "result")
                    self.assertEqual(event["status"], expected_status)
                    self.assertEqual(event["exit_code"], exit_code)
                    self.assertEqual(event["failed"], exit_code)
                    self.assertEqual(event["unverified_scope"], "无")
                    self.assertEqual(event["residual_risk"], "无")

    def test_result_mode_rejects_missing_fields(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            payload = {"exit_code": 1, "failed": 2, "unverified_scope": "无"}
            proc = subprocess.run(
                [sys.executable, "-m", "scripts.lib.agent_dispatch", "result",
                 "--event-path", str(path), "--run-id", "run-1", "--layer", "required"],
                input=json.dumps(payload) + "\n", cwd=ROOT, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(proc.returncode, 1)
            event = json.loads(path.read_text().splitlines()[-1])
            self.assertEqual(event["event"], "result")
            self.assertEqual(event["status"], "DENIED")
            self.assertEqual(event["reason_code"], "result_fields_missing")


    def test_invalid_utf8_input_yields_stable_json_not_traceback(self):
        # CQ-1：非法 UTF-8 输入必须落进稳定 JSON 拒绝对象，不得 traceback。
        for mode, expected_rc in (([], 0), (["result"], 1)):
            with self.subTest(mode=mode or "dispatch"):
                proc = subprocess.run(
                    [sys.executable, "-m", "scripts.lib.agent_dispatch", *mode],
                    input=b"\xff\xfe broken\n", cwd=ROOT, text=False,
                    capture_output=True, check=False,
                )
                self.assertEqual(expected_rc, proc.returncode,
                                 msg=proc.stderr.decode("utf-8", "replace"))
                stdout = proc.stdout.decode("utf-8", "replace")
                self.assertEqual(1, len(stdout.splitlines()), stdout)
                output = json.loads(stdout)
                self.assertIn(output.get("reason_code"),
                              ("request_invalid", "result_invalid"))


if __name__ == "__main__":
    unittest.main()
