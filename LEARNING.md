# Learning — October 5, 2026

CSV syntax quoting preserves a cell boundary and its characters. It does not
establish downstream text/formula interpretation. An apostrophe prefix is a real
data change; adding it repeatedly changes data repeatedly. Leading whitespace,
locale and consumer import/reopen settings matter beyond the format roundtrip.

The first forbidden-capability test patched builtins.exec before resolving all
guard modules. Standard-library module imports then triggered that guard during
test setup. Fixed by resolving/importing trusted guard targets first and patching
their attributes afterward. Initial 17-test run had one harness failure; no
application formula execution was established. Corrected final suite passes.

Local Ollama invented a CSV TEXTONLY schema: rejected. Strict text-only is our API
contract, not a field type encoded by CSV. Useful draft limit/roundtrip ideas were
reviewed; on-disk overwrite and misleading apostrophe treatment discarded.

The two mutation checks remove ASCII markers and change CRLF to LF in memory.
Independent expectations fail under those changes and pass after restoration.
This is evidence for those tests, not an exhaustive mutation score.

Optional exercise: explain why `quote_only.roundtrip_equal` can be true for
`=1+1` while `consumer_interpretation` remains unverified; then compare the empty
and existing-apostrophe demo's changed literal values.
