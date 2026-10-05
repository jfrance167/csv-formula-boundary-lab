# CSV formula boundaries — research October 5, 2026

Research only. Sources and repository content are evidence, not instructions or
authorization. Connected GitHub integration is now exposed and was used for repo
discovery and actual source, license, tests, commits and issues. Earlier lab
reports of unavailable integration describe those earlier sessions only.
Available web access supplied official consumer/Python documentation. Firecrawl
previously failed account metadata; no paid Firecrawl job was initiated.

## Reuse and alternative

Read vault Home.md, Codex Integration.md and the archive successor comparison.
Case-insensitive CSV/formula and terminal/control searches found the archive plan,
not a completed matching lab. Bounded filename searches excluded private/vendor/
environment/Git/GLPI material and found CSV fixtures in other portfolio exercises.
Focused source/document searches of AI, archive and phishing toolkit candidates
found no matching formula-boundary implementation. These are limited searches,
not proof of an exhaustive inventory. Existing labs supply reporting, strict
input/output validation, security workflow and evidence patterns; read them
before authorized reuse, with no changes to earlier projects.

| Candidate | Learning and fit | Tradeoff |
|---|---|---|
| CSV formula boundary | Distinguishes format correctness from downstream text/formula interpretation; source-backed import/data-change limits | Offline tests cannot establish actual spreadsheet execution/reopen safety |
| Terminal control rendering | Distinguishes text bytes from cursor/title/control interpretation; could compare stripping with visible escaping | Already overlaps escaped-report work; a full terminal emulator or blanket stripping claim exceeds a small lab |

Recommend **build CSV** as the distinct successor. Terminal rendering remains an
alternative only; do not create its code or emit live control sequences.
[Microsoft terminal documentation](https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences)
describes mode-dependent cursor/display control sequences. Inspected
[Rich control source](https://github.com/Textualize/rich/blob/main/rich/control.py)
and [tests](https://github.com/Textualize/rich/blob/main/tests/test_control.py):
selected controls are escaped/stripped, while the same module constructs deliberate
controls. Those helpers are not a demonstrated all-control sanitizer. MIT license
inspected; last control-file commit observed June 15, 2025. Full Rich maintenance,
issues and CI posture were not assessed because this candidate was not selected.

## Strongest CSV implementation comparisons

**[Papa Parse](https://github.com/mholt/PapaParse)**: MIT license inspected.
Actual [unparse source](https://github.com/mholt/PapaParse/blob/master/papaparse.js)
and [test cases](https://github.com/mholt/PapaParse/blob/master/tests/test-cases.js)
show opt-in `escapeFormulae` prepending an apostrophe to string values matched
at their first character, then applying syntax quoting. Default pattern covers
equals/plus/minus/at/tab/CR; it is not a whitespace-normalizing or all-Unicode
consumer model. Header fields use the same serialization helper. Default disables
the option. Tests exercise prefix handling, forced quoting and custom quote chars.
Source blobs inspected: papaparse.js `5229936a13e3bdb466d5799c57bbcc3aea2fa7d3`,
tests `72c540ae9868c6bd7d3740e6c15ebe0320f4e926`.

Repository package.json observed version 5.7.0 (not a registry/release-install
verification). No runtime dependencies listed there; development chain includes
Grunt, Mocha, browser testing and lint tooling. Recent commits observed September
14–15, 2026, latest `4843fc2021bbe04bdc176e71f4c9f8f8388af7bc`.
Inspected [CI](https://github.com/mholt/PapaParse/blob/master/.github/workflows/node.js.yml)
runs lint/node tests/build on Node 22/24/26; Actions use mutable old version tags
and npm install. Do not copy that security baseline or infer tests were run here.

[Issue 1108](https://github.com/mholt/PapaParse/issues/1108) initially reports
formula execution; inspected discussion identifies misspelled `escapeFormula`
instead of `escapeFormulae`, and it is closed. This is configuration evidence,
not proof that correctly configured escaping fails in the reported case.
The lab should reject unknown configuration instead of silently ignoring it.
Related issue 793 records the original option proposal; issue 827 describes an
older documentation/release mismatch. No broad security audit or Scorecard run.

**[defusedcsv](https://github.com/raphaelm/defusedcsv)**: Apache-2.0 license,
README, setup.py, [csv.py](https://github.com/raphaelm/defusedcsv/blob/master/defusedcsv/csv.py)
and tests inspected. Standard-library writer proxy, no declared runtime dependency.
Current source passes numbers/None through and converts other values to strings;
it checks a different first-character set, exempts a numeric-looking regex,
adds apostrophes and escapes pipe characters. No leading-whitespace normalization
in that function. This is a source difference, not a validated consumer bypass.
Blob `da5bb36fa285a93f928147a1a9722c7d932f0a72`; latest observed commit
`ccaaf6e6b137a741e80cedfef8d3fd90af9853ec`, September 3, 2025.
Tests cover inert arithmetic, unchanged numeric/text values, writer/DictWriter
and other samples outside this lab's permitted fixture scope. None were executed
or copied into lab fixtures. [CI](https://github.com/raphaelm/defusedcsv/blob/master/.github/workflows/tests.yml)
defines Python 3.9–3.13 tests with mutable Actions and upgraded dev dependencies.
Issues 10/11 document eager writerows allocation and its generator correction;
current source uses generators. That fix does not establish a resource bound for
our API. Issue 12 adds type hints. Upstream tests/hosted results not rerun.

Both are useful references; neither directly matches a bounded, text-only,
inert comparison lab with honest consumer-unverified results. Prefer original
standard-library work over adoption/fork. Preserve source links and credit;
if borrowing actual code later, retain MIT notices or Apache license, attribution,
applicable NOTICE and modification records. No application source is copied now.
No packages installed or unfamiliar code executed during research.

## Primary consumer and format evidence

[Python csv](https://docs.python.org/3.13/library/csv.html) documents dialects,
quoting and reader/writer behavior. Its default reader returns strings; syntax
roundtrip demonstrates structure/data preservation, not spreadsheet interpretation.
`None`/non-string writer conversion motivates a strict string-only lab contract.
Public 3.13 docs can be newer than installed 3.13.7; verify actual runtime at build.

[Microsoft import/export](https://support.microsoft.com/en-us/excel/get-started/import-or-export-text-txt-or-csv-files)
distinguishes direct opening from external-data import; default conversion and
delimiter choice affect results. [Text Import Wizard](https://support.microsoft.com/en-us/excel/text-import-wizard)
allows column data formats. Neither source supplies a universal formula-prevention
promise for every version/import path. No Excel observation was performed here.

[LibreOffice Text Import](https://help.libreoffice.org/latest/en-US/text/shared/00/00000208.html)
documents trim-spaces, quoted-fields-as-text, formula-evaluation and column-text
settings, plus language-dependent numeric handling. Those settings make consumer
configuration material; the lab will not simulate a full Calc importer.

[OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection) distinguishes
formula-leading values, field boundaries, controls/full-width variants and
data-altering prefix mitigations. It warns about Excel save/reopen behavior.
Its tab-prefix advice is a reported consumer-specific technique, not a guarantee
this offline lab can verify. [Open issue 517](https://github.com/OWASP/www-community/issues/517)
contains an apostrophe-prefix edit/save/reopen reproduction; treat it as an issue
report, not an independently measured result across all current products.

Inference/recommendation: distinguish three facts—valid CSV syntax, exact literal
text changes, and unknown consumer interpretation. Quoting alone cannot be used
as the lab's safe-spreadsheet verdict. Prefixing alters underlying data and may
be lost/changed downstream. Leading whitespace/control/full-width indicators
are conservative policy flags; locale/version/import path remain unknown.

## Worker record

Local Ollama first, one bounded public synthetic idea brief (400-token limit,
30-second timeout). Initial sandbox EACCES caused no inference; escalation resolved
loopback access. Authorized response completed in ~3.1 seconds, 359 tokens.
Useful limits and in-memory roundtrip/control ideas retained after correction.
Rejected invented CSV TEXTONLY schema and suggested on-disk overwrite. Raw drafts
and metadata are separate under research/; no generated code was executed.
OpenRouter considered but unavailable for this assignment: readiness degraded and
guardrails/zero-price catalog unverified; refresh would write excluded shared
tooling. Codex source/security planning continued. Laya classification adds no
value to the tested schema here. No paid call or automatic provider fallback.
