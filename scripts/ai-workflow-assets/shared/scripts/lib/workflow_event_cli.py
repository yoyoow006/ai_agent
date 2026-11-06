#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_events import EventWriter


RESERVED_FIELD_KEYS = {"schema_version", "run_id", "event", "timestamp", "layer", "status"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("run_id")
    parser.add_argument("layer")
    parser.add_argument("event")
    parser.add_argument("status")
    parser.add_argument("reason", nargs="?", default="")
    parser.add_argument("duration", nargs="?", default="")
    parser.add_argument('--task-id')
    parser.add_argument('--phase')
    parser.add_argument('--exit-code', type=int)
    parser.add_argument('--field', action='append', default=[])
    args = parser.parse_args()
    fields = {}
    if args.phase:
        fields['phase'] = args.phase
    if args.reason:
        fields["reason_code"] = args.reason
    if args.duration:
        fields["duration_ms"] = int(args.duration)
    if args.exit_code is not None:
        fields["exit_code"] = args.exit_code
    for item in args.field:
        key, sep, value = item.partition('=')
        if sep and key:
            # 协议保留键不得被调用方覆盖（CQ-5）：schema_version 类型与 status/event 语义不变。
            if key in RESERVED_FIELD_KEYS:
                parser.error(f"--field must not override reserved key: {key}")
            fields[key] = value
    # 保留键拒绝发生在创建输出文件之前：被拒绝的调用不得留下半成品事件文件。
    writer = EventWriter(Path(args.path), args.run_id, args.layer, task_id=args.task_id)
    writer.emit(args.event, args.status, **fields)
    writer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
