"""Compare CSV literal transformations without evaluating cell content."""

import csv
from io import StringIO
import json
import unicodedata

MAX_INPUT_BYTES = 16_384
MAX_DEPTH = 4
MAX_NUMERIC_CHARS = 16
MAX_ROWS = 16
MAX_COLUMNS = 8
MAX_CELL_CHARS = 256
MAX_TOTAL_CHARS = 4096
MAX_OUTPUT_BYTES = 65_536
ASCII_MARKERS = frozenset("=+-@")
FULLWIDTH_MARKERS = frozenset("＝＋－＠")
PREFIX_CATEGORIES = frozenset(("Cc", "Cf", "Zs", "Zl", "Zp"))
CONTROL_CATEGORIES = frozenset(("Cc", "Cf", "Zl", "Zp"))
NOT_VERIFIED = ("spreadsheet_execution", "import_path", "consumer_version",
                "display", "locale", "edit_save_reopen")


class _Invalid(ValueError):
    def __init__(self, reason: str, status: str = "rejected"):
        self.reason = reason
        self.status = status


def _outcome(status: str, reason: str) -> dict:
    return {"status": status, "complete": status == "comparison_complete", "reason": reason,
            "consumer_interpretation": "unverified", "not_verified": list(NOT_VERIFIED)}


def _table(rows: object) -> tuple[tuple[str, ...], ...]:
    # Reject subclasses/custom iterators before any user-defined behavior runs.
    if type(rows) not in (list, tuple):
        raise _Invalid("table_type")
    if not rows:
        raise _Invalid("empty_table")
    if len(rows) > MAX_ROWS:
        raise _Invalid("row_limit", "over_limit")
    columns = None
    total = 0
    result = []
    for row in rows:
        if type(row) not in (list, tuple):
            raise _Invalid("row_type")
        if not row:
            raise _Invalid("empty_row")
        if len(row) > MAX_COLUMNS:
            raise _Invalid("column_limit", "over_limit")
        if columns is not None and len(row) != columns:
            raise _Invalid("ragged_table")
        columns = len(row)
        for cell in row:
            if type(cell) is not str:
                raise _Invalid("cell_type")
            if len(cell) > MAX_CELL_CHARS:
                raise _Invalid("cell_limit", "over_limit")
            total += len(cell)
            if total > MAX_TOTAL_CHARS:
                raise _Invalid("total_character_limit", "over_limit")
            if any(0xD800 <= ord(char) <= 0xDFFF for char in cell):
                raise _Invalid("unpaired_surrogate")
        result.append(tuple(row))
    return tuple(result)


def _indicators(cell: str) -> list[str]:
    flags = set()
    if cell[:1] in ASCII_MARKERS:
        flags.add("ascii_formula_prefix")
    if cell[:1] in FULLWIDTH_MARKERS:
        flags.add("fullwidth_formula_prefix")
    if cell.startswith("'"):
        flags.add("existing_apostrophe")
    if any(unicodedata.category(char) in CONTROL_CATEGORIES for char in cell):
        flags.add("control_or_format")
    index = 0
    while index < len(cell) and (cell[index] in " \t\r\n\v\f"
                               or unicodedata.category(cell[index]) in PREFIX_CATEGORIES):
        index += 1
    if index and cell[index:index + 1] in ASCII_MARKERS | FULLWIDTH_MARKERS:
        flags.add("formula_after_leading_space_or_control")
    return sorted(flags)


def _csv(table: tuple[tuple[str, ...], ...]) -> tuple[str, bool]:
    buffer = StringIO(newline="")
    writer = csv.writer(buffer, delimiter=",", quotechar='"', doublequote=True,
                        quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    writer.writerows(table)
    text = buffer.getvalue()
    parsed = tuple(tuple(row) for row in csv.reader(StringIO(text, newline=""),
                   delimiter=",", quotechar='"', doublequote=True, strict=True))
    return text, parsed == table


def compare(rows: object) -> dict:
    """Compare a bounded built-in string table using the frozen CONTRACT.md.

    No header inference, trimming, coercion or Unicode normalization. An exact
    syntax roundtrip never verifies spreadsheet interpretation. Original indicators
    inspect complete cells, including rows a caller might consider headers.
    """
    try:
        original = _table(rows)
        prefixed = tuple(tuple("'" + cell for cell in row) for row in original)
        unchanged_csv, unchanged_roundtrip = _csv(original)
        changed_csv, changed_roundtrip = _csv(prefixed)
        if not unchanged_roundtrip or not changed_roundtrip:
            return _outcome("rejected", "internal_roundtrip_failure")
        indicators = []
        changes = []
        for row_index, row in enumerate(original):
            for column_index, cell in enumerate(row):
                coordinate = [row_index, column_index]
                flags = _indicators(cell)
                if flags:
                    indicators.append({"coordinate": coordinate, "indicators": flags})
                changes.append(coordinate)
        return {**_outcome("comparison_complete", "syntax_only"),
                "shape": [len(original), len(original[0])], "original_indicators": indicators,
                "quote_only": {"csv": unchanged_csv, "roundtrip_equal": unchanged_roundtrip,
                               "data_changed": False},
                "apostrophe_all": {"csv": changed_csv, "roundtrip_equal": changed_roundtrip,
                                   "data_changed": True, "changed_coordinates": changes,
                                   "prefix": "'", "idempotent": False}}
    except _Invalid as error:
        return _outcome(error.status, error.reason)


def _depth(text: str) -> None:
    # Count structural brackets outside strings before json.loads allocates
    # nested containers. json.loads remains responsible for syntax validity.
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise _Invalid("depth_limit", "over_limit")
        elif char in "]}":
            depth -= 1


def _unique(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _Invalid("duplicate_key")
        result[key] = value
    return result


def _integer(token: str) -> int:
    if len(token) > MAX_NUMERIC_CHARS:
        raise _Invalid("numeric_token_limit", "over_limit")
    return int(token)


def _reject_number(token: str) -> None:
    if len(token) > MAX_NUMERIC_CHARS:
        raise _Invalid("numeric_token_limit", "over_limit")
    raise _Invalid("non_integer_number")


def analyze_json(raw: object) -> dict:
    """Validate bounded exact UTF-8 bytes and compare the version-1 table envelope."""
    if type(raw) is not bytes:
        return _outcome("rejected", "input_type")
    if len(raw) > MAX_INPUT_BYTES:
        return _outcome("over_limit", "input_limit")
    try:
        text = raw.decode("utf-8", errors="strict")
        _depth(text)
        envelope = json.loads(text, object_pairs_hook=_unique, parse_int=_integer,
                              parse_float=_reject_number, parse_constant=_reject_number)
        if type(envelope) is not dict or set(envelope) != {"version", "rows"}:
            raise _Invalid("envelope_shape")
        if type(envelope["version"]) is not int:
            raise _Invalid("version_type")
        if envelope["version"] != 1:
            raise _Invalid("version", "unsupported")
        return compare(envelope["rows"])
    except _Invalid as error:
        return _outcome(error.status, error.reason)
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError):
        return _outcome("rejected", "invalid_json_or_utf8")


def serialize_report(report: dict) -> bytes:
    """Escape and cap an internally built report, including its final newline.

    This is an output formatter, not an arbitrary-object input validation API.
    Output-limit fallback is explicitly incomplete; the CLI then exits nonzero.
    """
    encoded = json.dumps(report, ensure_ascii=True, allow_nan=False,
                         separators=(",", ":")).encode("utf-8") + b"\n"
    if len(encoded) > MAX_OUTPUT_BYTES:
        return serialize_report(_outcome("over_limit", "output_limit"))
    return encoded
