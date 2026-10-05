# CSV formula boundary lab

A Python learning tool that compares correctly quoted CSV with an explicitly
data-changing apostrophe-prefix demonstration. It verifies literal string
roundtrips and reports conservative indicators. **Spreadsheet interpretation is
always unverified**, including when no indicators appear. No formula is evaluated
and no spreadsheet application is launched.

## Run and reuse

Tested locally on Windows CPython 3.13.7. Runtime uses only the standard library.
From this directory:

```powershell
python -m csv_boundary demo
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python tools/check_mutations.py
```

The analysis CLI accepts a UTF-8 JSON envelope on stdin and prints escaped JSON:

```powershell
'{"version":1,"rows":[["=1+1","a,b"],["","ordinary"]]}' | python -m csv_boundary analyze
```

This inert example exits 1 because an original cell has an indicator. Exit codes:
0 completed without indicators/passing demo, 1 completed with indicators/failed
demo, 2 rejected/unsupported/over-limit, 3 I/O failure. A short or failed write may
leave partial JSON; consumers must check the exit and complete JSON document.
There is no atomic-stdout guarantee. Raw CSV is never written to the terminal.

Reusable API (rows are uniformly treated, with no header guessing):

```python
from csv_boundary import compare, serialize_report

report = compare([["=1+1", "a,b"], ["", "'x"]])
print(serialize_report(report).decode("utf-8"))
```

`compare` accepts exact built-in list/tuple tables and rows, containing exact
strings. It rejects custom iterables/subclasses, numbers/None, ragged/empty shapes
and surrogate codepoints. `analyze_json` adds the strict versioned JSON boundary.
`serialize_report` formats internally built reports; it is not an arbitrary-object
input-validation API. See [frozen contract](CONTRACT.md) for reasons and limits.

## What the comparison proves

`quote_only` uses comma, double quotes, doubled embedded quotes and CRLF, quoting
every cell. Parsing that generated CSV returns the original strings exactly.
`apostrophe_all` prepends one literal apostrophe to **every** cell, including empty
and already-prefixed cells. It records every changed coordinate and roundtrips
to the transformed strings. Repeating it adds another apostrophe: not idempotent.
Neither demonstration is named or reported as safe to open in a spreadsheet.

The report inspects original complete strings for ASCII/full-width formula
markers, leading whitespace/control before markers, control/format characters
and existing apostrophes. `-1` is conservatively flagged; there is no numeric or
locale exception. Text is not trimmed, coerced or normalized. Commas/quotes/newlines
remain cell data when properly quoted; quoting is a syntax boundary.

## Architecture and threat model

Bounded JSON → strict string-table validation → original indicators → two fixed
in-memory CSV serializations → syntax roundtrip comparisons → escaped bounded JSON.

Limits: 16 KiB raw CLI input before parsing, JSON depth 4, numeric tokens 16
characters, 16 rows, 8 columns, 256 codepoints/cell, 4096 total codepoints and
64 KiB final JSON including newline/escaping. API limits match the table limits.
Reject the whole input rather than accepting a prefix. Output-limit fallback is
explicitly incomplete. The `version` integer is 1; unknown/duplicate keys and
floats/constants are rejected. All rows follow the same rules.

Attacker-controlled inputs can contain deceptive text or malformed JSON. Controls
exclude formula evaluation, consumer launch, network and file overwrite; cap input,
table and output work; preserve literal data; and keep interpretation unverified.
Trusted components are reviewed code and Python runtime. This is a synthetic
learning lab, not a malware sandbox or a production export sanitizer.

Consumer version/import path/locale, formula execution/display and editing,
saving and reopening are unverified. Prefixing changes underlying data and may
be changed again by consumers. Conservative indicators can miss behaviors or flag
ordinary text. No universal formula-prevention or vulnerability-free claim.
Fixtures contain inert text/arithmetic only, no command formulas/macros/DDE/links.

## Verification, sources and attribution

23 tests pass normally and with `-O`; six demos complete. Two deliberate in-memory
mutations are caught by independent expected-value tests, followed by successful
restoration checks. Bandit has no findings/errors/suppressions; local workflow
policy checks pass. See [verification](VERIFICATION.md), [ECC self-review](REVIEW.md)
and saved `evidence/`. Hosted Windows/Ubuntu CI and CodeQL are prepared, unrun.
No publication/merge/deployment. Scanner versions are pinned; artifact hashes and
a dedicated secret scanner are unavailable. Remote eligibility/protections remain
unverified. Runtime needs no development dependencies.

[Research](RESEARCH.md) compares Papa Parse (MIT), defusedcsv (Apache-2.0) and
terminal rendering. Original stdlib work was chosen; upstream code was inspected
but not copied, installed or executed. Reused CLI failure handling/test patterns
and workflow verifier from Jake's Archive Metadata Risk Lab; strict duplicate-key
pattern from AI Tool Policy Lab. Original project code is [MIT licensed](LICENSE).

Primary sources: [Python csv](https://docs.python.org/3.13/library/csv.html),
[LibreOffice import settings](https://help.libreoffice.org/latest/en-US/text/shared/00/00000208.html),
[Microsoft CSV import/export](https://support.microsoft.com/en-us/excel/get-started/import-or-export-text-txt-or-csv-files),
[OWASP CSV injection](https://community.owasp.org/attacks/CSV_Injection) and its
[save/reopen report](https://github.com/OWASP/www-community/issues/517).
No consumer observations were performed here.

Codex assisted source research, implementation, tests and self-review. One local
Ollama draft provided abstract ideas; incorrect schema and file-overwrite ideas
were rejected. No worker-generated code executed, remote inference or new spending.
See [decisions](DECISIONS.md) and [learning](LEARNING.md).

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
