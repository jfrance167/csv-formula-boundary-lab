"""Independent inert serialization oracles and strict boundary regressions."""

from contextlib import ExitStack
import importlib
import csv
from io import StringIO
import json
from unittest import TestCase
from unittest.mock import patch

from csv_boundary import analyze_json, compare, serialize_report
from csv_boundary.core import MAX_INPUT_BYTES, MAX_OUTPUT_BYTES
from csv_boundary.fixtures import demo_cases


class CoreTests(TestCase):
    def envelope(self, rows, version=1):
        return json.dumps({"version": version, "rows": rows}).encode("utf-8")

    def flags(self, value):
        report = compare([[value]])
        return report["original_indicators"][0]["indicators"] if report["original_indicators"] else []

    def test_fixed_serialization_and_coordinates(self):
        report = compare([["=1+1", "a,b"], ["", "'x"]])
        self.assertEqual(report["quote_only"]["csv"], '"=1+1","a,b"\r\n"","\'x"\r\n')
        self.assertEqual(report["apostrophe_all"]["csv"], '"\'=1+1","\'a,b"\r\n"\'","\'\'x"\r\n')
        self.assertEqual(report["apostrophe_all"]["changed_coordinates"], [[0, 0], [0, 1], [1, 0], [1, 1]])
        self.assertFalse(report["quote_only"]["data_changed"])
        self.assertTrue(report["apostrophe_all"]["data_changed"])
        self.assertFalse(report["apostrophe_all"]["idempotent"])

    def test_fixed_quote_newline_and_nul_literals(self):
        report = compare([['a"b', "x\r\ny", "\x00"]])
        self.assertEqual(report["quote_only"]["csv"], '"a""b","x\r\ny","\x00"\r\n')
        self.assertEqual(report["apostrophe_all"]["csv"], '"\'a""b","\'x\r\ny","\'\x00"\r\n')
        self.assertTrue(report["quote_only"]["roundtrip_equal"])

    def test_ascii_and_fullwidth_markers(self):
        for marker in "=+-@":
            self.assertEqual(self.flags(marker + "1+1"), ["ascii_formula_prefix"])
        for marker in "＝＋－＠":
            self.assertEqual(self.flags(marker + "1+1"), ["fullwidth_formula_prefix"])
        self.assertEqual(self.flags("-1"), ["ascii_formula_prefix"])
        self.assertEqual(self.flags("x=1+1"), [])

    def test_space_control_and_format_policy(self):
        for prefix in (" ", "\t", "\r", "\n", "\v", "\f", "\x00", "\u200b", "\u00a0", "\u2028"):
            with self.subTest(prefix=repr(prefix)):
                self.assertIn("formula_after_leading_space_or_control", self.flags(prefix + "=1+1"))
                self.assertIn("formula_after_leading_space_or_control", self.flags(prefix + "＝1+1"))
        self.assertEqual(self.flags(" "), [])
        self.assertEqual(self.flags("\t"), ["control_or_format"])
        self.assertEqual(self.flags("x\u200by"), ["control_or_format"])
        self.assertEqual(self.flags("'=1+1"), ["existing_apostrophe"])

    def test_first_row_uniform_no_header_guess(self):
        report = compare([["=1+1"], ["=1+1"]])
        self.assertEqual(report["original_indicators"], [
            {"coordinate": [0, 0], "indicators": ["ascii_formula_prefix"]},
            {"coordinate": [1, 0], "indicators": ["ascii_formula_prefix"]}])

    def test_roundtrip_mismatch_cannot_report_complete(self):
        with patch("csv_boundary.core.csv.reader", return_value=[["changed"]]):
            report = compare([["original"]])
        self.assertFalse(report["complete"])
        self.assertEqual(report["reason"], "internal_roundtrip_failure")
        self.assertNotIn("quote_only", report)

    def test_non_idempotent_and_original_preservation(self):
        table = [["", "'x", " =1+1", "cafe\u0301"]]
        snapshot = [list(table[0])]
        report = compare(table)
        self.assertEqual(table, snapshot)
        prefixed = list(csv.reader(StringIO(report["apostrophe_all"]["csv"], newline="")))
        self.assertEqual(prefixed, [["'", "''x", "' =1+1", "'cafe\u0301"]])
        self.assertNotEqual(compare(prefixed)["apostrophe_all"]["csv"], report["apostrophe_all"]["csv"])

    def test_exact_types_and_no_custom_iteration_or_coercion(self):
        class CustomList(list):
            def __iter__(self):
                raise AssertionError("custom iteration")
        class CustomStr(str):
            def __str__(self):
                raise AssertionError("custom stringification")
        class Custom:
            def __iter__(self):
                raise AssertionError("custom iteration")
            def __str__(self):
                raise AssertionError("custom coercion")
        for table in (Custom(), CustomList([["x"]]), [CustomList(["x"])], [[CustomStr("x")]],
                      [[Custom()]], [[1]], [[True]], [[None]], (x for x in [["x"]])):
            self.assertEqual(compare(table)["status"], "rejected")
        self.assertTrue(compare((("x",),))["complete"])

    def test_invalid_and_ragged_shapes(self):
        for table in ([], [[]], [["x"], []], [["x"], ["x", "y"]], "x", ["x"]):
            self.assertEqual(compare(table)["status"], "rejected")

    def test_each_table_limit_boundary_and_one_over(self):
        for accepted, rejected, reason in (([[""]] * 16, [[""]] * 17, "row_limit"),
            ([[""] * 8], [[""] * 9], "column_limit"),
            ([["x" * 256]], [["x" * 257]], "cell_limit"),
            ([["x" * 256] * 8] * 2, [["x" * 256] * 8] * 2 + [["x"] + [""] * 7], "total_character_limit")):
            self.assertTrue(compare(accepted)["complete"])
            report = compare(rejected)
            self.assertEqual(report["status"], "over_limit")
            self.assertEqual(report["reason"], reason)
            self.assertNotIn("quote_only", report)

    def test_surrogates_rejected_without_replacement(self):
        for cell in ("\ud800", "\udfff", "\ud800\udc00"):
            self.assertEqual(compare([[cell]])["reason"], "unpaired_surrogate")
        self.assertEqual(analyze_json(b'{"version":1,"rows":[["\\ud800"]]}')["reason"], "unpaired_surrogate")
        # Valid JSON escaped pair is decoded to one scalar by json.loads.
        self.assertTrue(analyze_json(b'{"version":1,"rows":[["\\ud83d\\ude00"]]}')["complete"])

    def test_byte_limit_precedes_parser_and_utf8(self):
        valid = self.envelope([["x"]])
        self.assertTrue(analyze_json(valid + b" " * (MAX_INPUT_BYTES - len(valid)))["complete"])
        with patch("csv_boundary.core.json.loads", side_effect=AssertionError("parser called")):
            self.assertEqual(analyze_json(b"x" * (MAX_INPUT_BYTES + 1))["reason"], "input_limit")
            self.assertEqual(analyze_json(bytearray(valid))["reason"], "input_type")

    def test_json_depth_and_escaped_structural_text(self):
        with patch("csv_boundary.core.json.loads", side_effect=AssertionError("parser called")):
            self.assertEqual(analyze_json(b"[[[[[]]]]]")["reason"], "depth_limit")
        for cell in ('[{]}', 'a"[', '\\"[[[[['):
            self.assertTrue(analyze_json(self.envelope([[cell]]))["complete"])
        self.assertEqual(analyze_json(b'{"version":1,"rows":[[["x"]]]}')["reason"], "cell_type")

    def test_json_numeric_bounds_versions_and_constants(self):
        self.assertEqual(analyze_json(b'{"version":1111111111111111,"rows":[["x"]]}')["status"], "unsupported")
        self.assertEqual(analyze_json(b'{"version":11111111111111111,"rows":[["x"]]}')["reason"], "numeric_token_limit")
        for token in ("true", '"1"', "null", "1.0", "NaN", "Infinity", "-Infinity"):
            raw = ('{"version":' + token + ',"rows":[["x"]]}').encode()
            self.assertEqual(analyze_json(raw)["status"], "rejected")
        self.assertEqual(analyze_json(b'{"version":1e11111111111111111,"rows":[["x"]]}')["reason"], "numeric_token_limit")
        self.assertEqual(analyze_json(self.envelope([["x"]], 2))["status"], "unsupported")

    def test_json_duplicate_unknown_shape_and_encoding(self):
        for raw in (b'{"version":1,"version":1,"rows":[["x"]]}',
                    b'{"version":1,"rows":[["x"]],"escapeFormula":true}',
                    b'{"version":1}', b'[]', b'null', b'{}', b'\xff', b'\xef\xbb\xbf{}', b'{'):
            self.assertEqual(analyze_json(raw)["status"], "rejected")
        self.assertEqual(analyze_json(b'{"version":1,"rows":[["x"]],"rows":[["y"]]}')["reason"], "duplicate_key")

    def test_consumer_unverified_for_every_outcome(self):
        for report in (compare([["x"]]), compare([]), compare([["x"]] * 17),
                       analyze_json(self.envelope([["x"]], 2))):
            self.assertEqual(report["consumer_interpretation"], "unverified")
            self.assertIn("edit_save_reopen", report["not_verified"])
            self.assertNotIn("safe_csv", report)
            self.assertNotIn("safe_to_open", report)

    def test_output_escaping_bounds_and_determinism(self):
        for _, table in demo_cases() + [("max text", [["界" * 256] * 8] * 2),
                                       ("all C0 controls", [["".join(chr(i) for i in range(32))]])]:
            report = compare(table)
            encoded = serialize_report(report)
            self.assertLessEqual(len(encoded), MAX_OUTPUT_BYTES)
            self.assertEqual(encoded, serialize_report(report))
            self.assertEqual(encoded.count(b"\n"), 1)
            self.assertNotIn(b"\r", encoded)
            self.assertNotIn(b"\t", encoded)
            self.assertNotIn(b"\x1b", encoded)
            self.assertFalse(any(byte < 32 for byte in encoded[:-1]))
            self.assertEqual(json.loads(encoded)["consumer_interpretation"], "unverified")
        report = json.loads(serialize_report({"synthetic_test": "x" * MAX_OUTPUT_BYTES}))
        self.assertEqual(report["reason"], "output_limit")
        self.assertFalse(report["complete"])

    def test_forbidden_execution_launch_file_and_network_capabilities(self):
        cases = demo_cases()
        # Resolve/import stdlib guard targets before blocking exec; module loading
        # legitimately executes module definitions and is outside runtime analysis.
        targets = []
        for module_name, attribute in (("subprocess", "run"), ("subprocess", "Popen"),
                                      ("os", "system"), ("os", "startfile"), ("socket", "socket"),
                                      ("urllib.request", "urlopen"), ("webbrowser", "open"),
                                      ("builtins", "open"), ("builtins", "eval"), ("builtins", "exec")):
            module = importlib.import_module(module_name)
            if hasattr(module, attribute):
                targets.append((module, attribute))
        with ExitStack() as stack:
            for module, attribute in targets:
                stack.enter_context(patch.object(module, attribute, side_effect=AssertionError("forbidden capability")))
            for _, table in cases:
                self.assertTrue(compare(table)["complete"])
                self.assertTrue(analyze_json(self.envelope(table))["complete"])
