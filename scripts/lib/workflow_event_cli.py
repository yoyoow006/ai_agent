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
    args = parser.parse_args()
    writer = EventWriter(Path(args.path), args.run_id, args.layer)
    fields = {}
    if args.reason:
        fields["reason_code"] = args.reason
    if args.duration:
        fields["duration_ms"] = int(args.duration)
    writer.emit(args.event, args.status, **fields)
    writer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
