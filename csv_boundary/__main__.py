"""Bounded stdin JSON or inert demo; never raw CSV terminal output."""

import argparse
import json
import sys

from .core import MAX_INPUT_BYTES, analyze_json, compare, serialize_report
from .fixtures import demo_cases


def main() -> int:
    parser = argparse.ArgumentParser(description="CSV syntax boundaries; consumer behavior unverified")
    parser.add_argument("command", choices=("analyze", "demo"))
    args = parser.parse_args()
    try:
        if args.command == "analyze":
            report = analyze_json(sys.stdin.buffer.read(MAX_INPUT_BYTES + 1))
        else:
            cases = [{"case": name, "report": compare(table)} for name, table in demo_cases()]
            report = {"mode": "inert_syntax_comparison", "cases": cases,
                      "consumer_interpretation": "unverified",
                      "passed": all(case["report"]["complete"] for case in cases)}
        payload = serialize_report(report)
        emitted = json.loads(payload)
        if sys.stdout.buffer.write(payload) != len(payload):
            raise OSError("short output write")
        sys.stdout.buffer.flush()
    except OSError:
        # Partial output may already exist. Suppress a second failed flush at
        # interpreter shutdown without opening another file or hiding the exit.
        sys.stdout = None
        try:
            print('{"error":"input_or_output_failure"}', file=sys.stderr)
        except OSError:
            pass
        return 3
    if emitted.get("status") == "over_limit":
        return 2
    if args.command == "demo":
        return 0 if report["passed"] else 1
    if not report["complete"]:
        return 2
    return 1 if report["original_indicators"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
