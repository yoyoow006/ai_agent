"""Static gate for the limited validation-agent roles.

The module deliberately decides whether a host may dispatch an agent; it never
starts one.  It accepts a JSON object on stdin so callers can use the same
decision path from shell wrappers and from Python.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable


ROLES = {"explorer", "reviewer", "test_worker"}
LAYERS = {"fast", "standard", "required", "archive-light"}
TASK_SIZES = {"small", "tiny", "large"}


def _items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value):
        return list(value)
    return []


def _overlap(boundary: Iterable[str], existing: Iterable[str]) -> bool:
    """Return true when a path is equal to or nested under another path."""
    def normalise(path: str) -> str:
        return os.path.normpath(path.strip())

    ours = [normalise(item) for item in boundary]
    theirs = [normalise(item) for item in existing]
    for left in ours:
        for right in theirs:
            if left == right or left.startswith(right + os.sep) or right.startswith(left + os.sep):
                return True
    return False


def _command_is_executable(command: Any) -> bool:
    if not isinstance(command, str) or not command.strip() or "\n" in command or "\r" in command:
        return False
    try:
        words = shlex.split(command)
    except ValueError:
        return False
    if not words or any("\n" in word or "\r" in word for word in words):
        return False
    executable = words[0]
    # A direct path must be executable.  For a bare command, resolve it using
    # PATH; this rejects typos while allowing python3, bash, and project tools.
    candidate = executable if os.path.dirname(executable) else shutil.which(executable)
    return bool(candidate and os.access(candidate, os.X_OK))


def gate_dispatch(request: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the four dispatch conditions and return a stable decision."""
    if not isinstance(request, dict):
        request = {}

    raw_role = request.get("role")
    role = raw_role.strip() if isinstance(raw_role, str) else ""
    layer = request.get("layer")
    task_size = request.get("task_size")

    if not isinstance(layer, str) or layer not in LAYERS:
        return _decision("denied", "request_invalid", role, "主会话处理")
    if not isinstance(task_size, str) or task_size not in TASK_SIZES:
        return _decision("denied", "request_invalid", role, "主会话处理")

    # Fast and concentrated standard work stays in the main session even when
    # all other fields happen to be present.
    if layer == "fast" or task_size == "fast" or (layer == "standard" and task_size in {"small", "tiny"}):
        return _decision("denied", "task_scope_exempt", role, "主会话处理")

    boundary_value = request.get("boundary")
    boundary = _items(boundary_value)
    if not boundary:
        reason = "independent_boundary_required" if "boundary" not in request or boundary_value == [] else "request_invalid"
        return _decision("denied", reason, role, "主会话处理")
    if any(os.path.isabs(path) or path == ".." or path.startswith("../") or "/../" in path for path in boundary):
        return _decision("denied", "request_invalid", role, "主会话处理")
    existing = _items(request.get("existing_boundaries", []))
    if not isinstance(request.get("existing_boundaries", []), list):
        return _decision("denied", "request_invalid", role, "主会话处理")
    if _overlap(boundary, existing):
        return _decision("denied", "boundary_overlap", role, "主会话处理")

    if role not in ROLES:
        return _decision("denied", "role_mismatch", role, "主会话处理")

    command = request.get("acceptance_command")
    if not _command_is_executable(command):
        return _decision("denied", "acceptance_command_invalid", role, "主会话处理")

    if not isinstance(request.get("shared_writes"), bool) or not isinstance(request.get("sequential_dependency"), bool):
        return _decision("denied", "request_invalid", role, "主会话处理")
    shared = request["shared_writes"]
    dependent = request["sequential_dependency"]
    if shared or dependent:
        return _decision("denied", "shared_state_conflict", role, "主会话处理")

    result = _decision("allowed", "allowed", role, "派发代理")
    result["boundary"] = boundary
    result["acceptance_command"] = command
    return result


def _decision(dispatch: str, reason_code: str, role: str, next_action: str) -> dict[str, Any]:
    return {
        "dispatch": dispatch,
        "reason_code": reason_code,
        "role": role,
        "next_action": next_action,
    }


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--event-path")
    parser.add_argument("--run-id", default="agent-dispatch")
    parser.add_argument("--layer", default="standard")
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        result = gate_dispatch(payload)
    except (json.JSONDecodeError, OSError, TypeError):
        result = _decision("denied", "request_invalid", "", "主会话处理")
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    if args.event_path:
        try:
            from scripts.lib.workflow_events import EventWriter
        except ImportError:
            from workflow_events import EventWriter
        writer = EventWriter(Path(args.event_path), args.run_id, args.layer)
        status = "INFO" if result["dispatch"] == "allowed" else "DENIED"
        writer.emit("dispatch", status, dispatch=result["dispatch"], role=result["role"], reason_code=result["reason_code"], next_action=result["next_action"])
        writer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
