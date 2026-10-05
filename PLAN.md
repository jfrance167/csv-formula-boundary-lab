# Proposed CSV formula boundary lab — October 5, 2026

Tier 3, stages 1–3 approved by coordinator October 5, 01:21 Eastern under Jake's
verified direct mandate. Approval recorded before code. Research: RESEARCH.md. Sole writer
in the current chat. No actions beyond the local approved successor mandate;
cutoff October 6, 08:00 Eastern. No earlier-project/shared-tooling modifications.

## Problem, success and alternatives

Show why correctly quoted CSV can preserve a formula-looking string without
establishing that a spreadsheet will treat it as text. Given a small table of
synthetic strings, compare quote-only serialization with an explicitly
data-changing apostrophe-prefix demonstration and report conservative indicators.
Success means deterministic bounded reports, exact string roundtrip evidence,
explicit data changes and consumer behavior always unverified—not safe CSV.

Recommend build original standard-library core. Papa Parse (MIT) and defusedcsv
(Apache-2.0) were inspected as implementations; their wider/configuration-sensitive
contracts differ from this lab. Terminal-control rendering was compared and held
as an alternate because escaped-report learning already overlaps earlier work.
No dependency installation, formula evaluator or upstream code execution needed.

## Scope and proposed contract to freeze before implementation

- Reusable API and CLI demo/analysis. API accepts a rectangular finite table of
  exact strings, with rows treated uniformly; there is no guessed header/schema.
  CLI accepts bounded UTF-8 JSON with exactly `version: 1` and `rows` keys.
  Reject duplicates, unknown keys, non-string cells, wrong types, ragged/empty
  shapes and unsupported versions. No implicit number/None conversion.
- Proposed limits: 16 KiB raw input before decoding/parsing, JSON nesting depth 4,
  16 rows, 8 columns, 256 characters/cell, 4096 total cell characters. Numeric
  tokens are bounded and version must be exact integer 1, never Boolean 1.
  Analyze the full table or reject it; do not approve a truncated prefix.
- Fixed comma delimiter, double quote, doubled embedded quotes, CRLF record end,
  no dialect sniffing/locale detection/import of arbitrary CSV. All cells quoted.
  Use csv writer/reader on memory buffers to verify generated-table roundtrip.
- Produce two labeled demonstrations: `quote_only` preserves all literal input;
  `apostrophe_all` prepends one literal apostrophe to every cell (including empty
  and already-apostrophe-leading cells) before the same syntax quoting. Record
  every changed coordinate. This transformation is deliberately not idempotent;
  never strip apostrophes or describe it as universally safe or lossless.
- Indicators inspect full original strings: ASCII formula-leading characters;
  leading whitespace/control followed by a formula marker; control/format
  characters anywhere; full-width formula-marker variants; existing apostrophe.
  Freeze the exact prefix/Unicode category policy in stage 1. Preserve text
  without trimming or Unicode normalization. Numeric-looking strings such as
  `-1` may be conservatively flagged; no locale-sensitive numeric exemption.
- JSON reports include original indicators, changed coordinates, escaped CSV
  demonstrations and roundtrip results. Interpretation is always `unverified`;
  no `safe_to_open`/`safe_csv` field. Final UTF-8 JSON plus newline capped at
  64 KiB; over-limit output returns explicit incomplete status, never partial
  success. All untrusted display strings escaped; raw CSV never written to stdout.
- Statuses distinguish completed comparison, rejected/unsupported input and
  over-limit. CLI I/O failure exits nonzero with fixed escaped error; oversized
  result exits nonzero. Exact CLI exit mapping frozen in stage 1.

Fixtures use ordinary text and inert arithmetic such as `=1+1`, marker variants,
spaces/tab/CR/LF, apostrophe, commas, semicolons, quotes, negative numeric-looking
text and small Unicode examples. No DDE, command formulas, macros, external links,
data-exfiltration functions, executable content, automatic spreadsheet launch,
filesystem overwrite, network, HTTP service, production/customer data or live
terminal control rendering. Runtime has no model inference.

## Architecture, threat model and limitations

Bounded UTF-8 JSON → strict table validation → conservative text indicators →
two fixed in-memory CSV serializations → syntax roundtrip comparison → bounded
escaped JSON. Standard-library runtime, no consumer execution capabilities.

Attacker controls cell text and CLI input. Assets: host execution boundary,
report integrity, original data and honest interpretation. Controls: no evaluator/
application-launch/file/network capability, strict bounded table/JSON, standard
syntax writer, explicit transformation records and escaped final output.
Trust includes reviewed code/runtime; a normal host sandbox is not malware isolation.

Risks: conservative false positives/false negatives, parser bugs, terminal/report
misuse and downstream consumer assumptions. Leading Unicode whitespace, format
controls, full-width variants, locale/delimiters and import options vary. CSV
quoting is syntax. Prefixing changes data; editing/export/reopening can change
it again. Spreadsheet version/import path/reopen execution, display, formulas,
external behavior and locale are unverified even for zero-indicator results.
No spreadsheet profiles pretending to be actual consumer measurements.

## Stages and definitions of done

1. Freeze exact validation/indicator/status/exit rules and source-linked expected
   examples before coding. Implement reusable bounded core and memory-only
   serializations. Done: precise public contract, accepted ordinary table,
   complete change accounting and rejected malformed/over-limit input.
2. Inert fixtures/CLI and regressions. Done: quote-only generated reader returns
   exactly the original table; prefixed reader returns exactly transformed table;
   indicators remain after syntax quoting; unknown config rejected; controls
   escaped; data changes explicit; no consumer-launch/evaluation/file/network calls.
3. ECC self-review, affected checks and portfolio evidence. Done: available unit/
   integration tests, Bandit and pinned local workflow-policy checks recorded;
   README/setup/demo/threat model/license/AI disclosure, STATE/DECISIONS/LEARNING,
   exact verification limits. Prepare local owned-Python security baseline only
   after approval; hosted CI/CodeQL/protections/publication remain unverified.

Tests must cover each boundary plus one-over limit; invalid UTF-8, JSON duplicates/
depth/numeric tokens/Boolean version, unknown keys/version, non-string/ragged
rows; first-cell/header-equivalent treatment; whitespace/control/full-width cases;
embedded delimiters/quotes/newlines; existing apostrophe and negative-number data
tradeoffs; exact roundtrip/changed coordinates; deterministic escaped output;
final-byte cap and read/write/short-write failures. Patch forbidden capabilities
while running inert cases. Never execute formulas to validate them.

Prior local-first draft was reviewed and corrected (RESEARCH.md). Retain raw
drafts separately; security judgments and code review stay with Codex. No remote
call without verified eligibility/guardrails, no spending or automatic fallback.
At approval, no implementation/tests had run. Next: execute approved stages.

## Mandatory approval clarifications recorded before code

Coordinator SUCCESSORS.md section CSV implementation approval — October 5, 01:21
heartbeat requires frozen indicator/numeric/Unicode/exit rules (CONTRACT.md);
bounded exact built-in table containers/strings without arbitrary iteration or
coercion; explicit surrogate rejection; original-data preservation; every cell
changed by prefixing; independent fixed serialization/coordinate expectations;
uniform first-row handling. All listed input/output/JSON limits apply to the API
and CLI. Output failure is honest nonzero, with no atomic-stdout guarantee.
Keep consumer interpretation unverified, forbidden capabilities absent and inert
fixtures only. Finish normal/optimized tests, ECC actual-code review, SAST/local
baseline and portfolio/Obsidian evidence. No hosted/publication/merge assurances.
