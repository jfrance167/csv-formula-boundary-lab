# Verification — October 5, 2026

Actual platform: Windows, CPython 3.13.7. Runtime standard library only. Evidence
records source hashes/runtime version; no spreadsheet/terminal interpretation
observations, real samples or formulas executed.

| Check | Actual result |
|---|---|
| `python -m unittest discover -s tests -v` | 23 methods pass |
| `python -O -m unittest discover -s tests -v` | Same 23 methods pass |
| `python -m csv_boundary demo` | Six inert syntax comparisons complete |
| `python tools/check_mutations.py` | Both focused mutations caught; restored tests pass |
| `python -m bandit -r csv_boundary tools -f json -o evidence/bandit.json` | No findings/errors/suppressions, exit 0 |
| `python tools/verify_workflows.py` (also `-O`) | Local YAML/pin/permission/trigger checks PASS |
| `python -m pip check` | Installed environment has no broken requirements |

Saved logs/reports are under evidence/, with explicit exit-code summary. Initial
17-method run had one guard-setup failure; correction is documented in LEARNING.md.
Independent exact CSV/coordinate expectations supplement generated roundtrips.
Both in-memory mutation contexts restore automatically; no source mutation saved.

Real analysis CLI stdin smoke with the README's inert arithmetic/text table exited
1 as expected and emitted complete escaped JSON (cli-analysis*.json). Content
review reports zero bounded pattern matches; ignored raw drafts and vault staging
notes remain local separately, not Git portfolio content.

Forbidden-capability tests block eval/exec, file opening, subprocess/system launch,
socket, URL opener and browser launcher while inert API and JSON scenarios run.
Trusted stdlib modules are loaded before the guards. Windows startfile is guarded
when present; absence on other platforms is not represented as execution evidence.
All C0 characters remain escaped in final JSON. Synthetic fixture content is not
evaluated. Partial failed writes can exist; nonzero status is required by contract.

Action commit pins were reused from the earlier labs' official-source verified
mapping (checkout v7.0.1, setup-python v7.0.0, CodeQL v4.38.2). Local verifier checks
exact pins; it does not verify hosted execution. Prepared Windows/Ubuntu Python
3.13 CI, weekly/manual CodeQL and Bandit have not run on GitHub. No remote repository
configured; visibility, protections, secret-scanning and update eligibility unverified.

Scanner versions are pinned without artifact hashes: previous canonical PyPI TLS
metadata attempts failed, so no integrity lock claim. Dedicated secret scanner
unavailable; bounded credential/private-path patterns plus manual code/docs review
are limited and do not prove every secret is absent. Upstream candidate tests/CI
were inspected only; not rerun. No dependency security certification or Scorecard.

ECC implementing-agent self-review is in REVIEW.md. Runtime/resource bounds do
not establish hard process RSS/time isolation or universal consumer safety.
