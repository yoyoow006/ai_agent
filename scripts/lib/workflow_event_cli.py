#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_events import EventWriter


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
    writer = EventWriter(Path(args.path), args.run_id, args.layer, task_id=args.task_id)
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
            fields[key] = value
    writer.emit(args.event, args.status, **fields)
    writer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
