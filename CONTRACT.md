# Frozen initial contract — October 5, before code

API table and rows: exact built-in list or tuple, nonempty rectangular 1–16 rows
of 1–8 cells. Cells exact built-in str, at most 256 Unicode codepoints each and
4096 total. Reject custom subclasses/iterables/objects before coercion or iteration.
Reject any surrogate codepoint U+D800–U+DFFF; no replacement or normalization.
Working copies of accepted cells remain immutable tuples within the comparison.

CLI analysis accepts exact bytes, at most 16384 before strict UTF-8 decoding or
JSON parsing. JSON nesting maximum 4, counting each object/array outside strings;
scan bounded text before json.loads. All numeric tokens at most 16 characters,
including sign; floats/constants rejected. Duplicate keys rejected. Exact root
object keys version/rows, version exact int 1; other integers unsupported versions,
other types rejected. No BOM allowance, sniffed dialect or arbitrary CSV import.

Full text inspected without trimming/normalization. Sorted indicator codes:
- ascii_formula_prefix: first codepoint in ASCII `=+-@`.
- fullwidth_formula_prefix: first codepoint in `＝＋－＠`.
- formula_after_leading_space_or_control: after a nonempty prefix of ASCII space,
  tab/CR/LF/VT/FF or Unicode categories Cc/Cf/Zs/Zl/Zp, next codepoint is one of
  those eight markers. This is a conservative rule, not a consumer emulator.
- control_or_format: any codepoint in Cc/Cf/Zl/Zp anywhere.
- existing_apostrophe: first codepoint is literal ASCII apostrophe.
Empty strings have no indicators. `-1` is flagged, not parsed as a number.
Whitespace/control-only strings receive only applicable control indicators.

No header guessing; coordinates are zero-based [row,column]. quote_only uses
comma/double-quote/doublequote=True/QUOTE_ALL/CRLF, StringIO with newline=''.
apostrophe_all prepends exactly one ASCII apostrophe to every cell and uses the
same dialect. Both compare generated csv.reader strings to their target table;
no type conversion. Changes list every cell coordinate; repeated transformation
adds another apostrophe, expressly non-idempotent. No stripping or safety claim.

Independently fixed expected two-row example (backslash escapes are display):
table = [["=1+1", "a,b"], ["", "'x"]]
quote_only = '"=1+1","a,b"\r\n"","\'x"\r\n'
apostrophe_all = '"\'=1+1","\'a,b"\r\n"\'","\'\'x"\r\n'
changes = [[0,0],[0,1],[1,0],[1,1]]. First cell retains its original prefix
indicator, while apostrophe-leading [1,1] gets existing_apostrophe.
Embedded double quote is doubled in a quoted cell; embedded CR/LF preserved.

Reports: status comparison_complete/rejected/unsupported/over_limit, complete
Boolean, reason, consumer_interpretation='unverified', fixed not_verified list.
Complete results include original indicators, both CSV strings, independently
calculated target roundtrip results, data-change coordinates and prefix metadata.
No safe verdict field. JSON ensure_ascii=True and allow_nan=False, compact UTF-8
plus one LF. Maximum output 65536 bytes, including escape expansion and newline;
oversize replaced with fixed incomplete output_limit result, not truncated.
Serialization only accepts internally built bounded reports, not arbitrary input.

CLI exits: 0 comparison completed without original indicators / passing demo;
1 comparison complete with indicators / failed demo; 2 rejected, unsupported or
over-limit; 3 input/output failure. Demo output-limit fallback also exits 2.
Check full write and flush; failed/short writes may leave a partial JSON stream,
so consumers must require exit success and complete valid JSON. No atomic stdout
promise. Stderr uses only a fixed escaped error, never exception/input content.
