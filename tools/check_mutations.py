"""Prove two focused regressions detect deliberate in-memory mutations.

Usage: python tools/check_mutations.py
No source edits, files written, external commands or network calls. Tests use
trusted inert fixtures. JSON reports caught mutations/restoration; exit 0 only
if both were caught and the same tests passed after patch context restoration.
This is focused evidence, not a mutation score or exhaustive fault coverage.
"""

from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from csv_boundary import core
from test_core import CoreTests


def run_case(name: str) -> bool:
    result = unittest.TextTestRunner(stream=StringIO()).run(unittest.TestSuite([CoreTests(name)]))
    return result.wasSuccessful()


def main() -> int:
    fixed_csv = core._csv

    def wrong_newlines(table):
        text, equal = fixed_csv(table)
        return text.replace("\r\n", "\n"), equal

    expectations = []
    with patch.object(core, "ASCII_MARKERS", frozenset()):
        expectations.append({"mutation": "missing_ascii_markers",
                             "detected": not run_case("test_ascii_and_fullwidth_markers")})
    with patch.object(core, "_csv", wrong_newlines):
        expectations.append({"mutation": "wrong_record_newline",
                             "detected": not run_case("test_fixed_serialization_and_coordinates")})
    restored = all(run_case(name) for name in (
        "test_ascii_and_fullwidth_markers", "test_fixed_serialization_and_coordinates"))
    print(json.dumps({"mutations": expectations, "restored_tests_pass": restored,
                      "scope": "two in-memory changes; no source mutation"}, indent=2))
    return 0 if restored and all(item["detected"] for item in expectations) else 1


if __name__ == "__main__":
    raise SystemExit(main())
