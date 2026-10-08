"""Stable JSONL diagnostics and discardable local metrics for workflow runs."""

from __future__ import annotations

import json
import os
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
STATUSES = {"PASS", "FAIL", "SKIP", "INFO", "DENIED"}


def new_run_id() -> str:
    return uuid.uuid4().hex


@dataclass(frozen=True)
class WriteResult:
    ok: bool
    reason_code: str = "ok"


class EventWriter:
    def __init__(self, path: Path | None, run_id: str, layer: str, task_id: str | None = None):
        self.path = Path(path) if path else None
        self.run_id = run_id
        self.layer = layer
        self.task_id = task_id
        self._stream = None
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._stream = self.path.open("a", encoding="utf-8")

    def emit(self, event: str, status: str, **fields: Any) -> dict[str, Any]:
        if status not in STATUSES:
            raise ValueError(f"unsupported status: {status}")
        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "event": event,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "layer": self.layer,
            "status": status,
        }
        if self.task_id:
            payload["task_id"] = self.task_id
        payload.update(fields)
        if self._stream is not None:
            self._stream.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
            self._stream.flush()
        return payload

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None


def summarize_task_events(path: Path, task_id: str) -> dict[str, Any]:
    """Aggregate lifecycle events for one task while accepting legacy records."""
    phases: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("task_id") == task_id and "duration_ms" in event:
            phases.append({k: event[k] for k in ("phase", "duration_ms", "status", "reason_code") if k in event})
    return {"task_id": task_id, "phases": phases, "total_duration_ms": sum(p.get("duration_ms", 0) for p in phases)}

def write_metrics(directory: Path, metrics: dict[str, Any]) -> WriteResult:
    """Atomically write one aggregate record; failure never raises to callers."""
    try:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        run_id = str(metrics.get("run_id") or new_run_id())
        payload = {"schema_version": SCHEMA_VERSION, **metrics, "run_id": run_id}
        fd, temporary = tempfile.mkstemp(prefix=f".{run_id}.", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, directory / f"{run_id}.json")
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        return WriteResult(True)
    except (OSError, TypeError, ValueError):
        return WriteResult(False, "metrics_write_failed")
