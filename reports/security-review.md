# Local security review — 2026-11-14

Scope: this coordination repository, not the referenced upstream projects.

| Finding | Evidence | Impact / recommendation |
|---|---|---|
| Mutable CI action references | Fixed 2026-11-18: `.github/workflows/oss-monitor.yml` now pins checkout, setup-python and upload-artifact to the same commit SHAs as `ci-sec.yml` (was checkout@v4, setup-python@v5, upload-artifact@v4) | Supply-chain hardening gap, not a confirmed compromise. Pin reviewed commit SHAs. New CI-SEC actions use SHAs. |
| No subprocess timeout | `scripts/github_read.py`, `default_runner` | A stalled gh process can exhaust job time. Set a subprocess timeout and handle TimeoutExpired as UNVERIFIED. This is an availability concern, not proven remote code execution. |
| Markdown links survive title sanitization | `scripts/render_report.py`, `plain` strips several metacharacters but preserves `[text](URL)` | Untrusted titles can render misleading links in summaries. Escape Markdown punctuation if plain text is intended. No demonstrated script execution. |

No confirmed exploitable CVE is asserted by this manual review. Automated scan
status and timestamp are in `reports/security/summary.json`; raw reports distinguish
scanner findings from unavailable tooling. Existing 23 CLI regression tests passed.
There is no server, Dockerfile or application dependency manifest in the repository.
DAST/IAST and default image coverage must not be interpreted as passing scans.

Automated run at 2026-11-14T11:07:33Z: Bandit found no medium/high issues;
Trivy found no high/critical secrets, and detected zero dependency/config files.
CycloneDX generation succeeded. This does not establish dependency/config safety.
The final regression run had 21 passes and two failures: target-count assertions
expected 8 but observed 13 after an independent edit to config/targets.json during
this task. That edit was not made or reverted by this security implementation.

Follow-up: replaced fixed target-count assumptions with comparisons against the
configured repository names and exact requested API paths. Each request must use
GET. Re-ran `python3 -m unittest discover -s tests -v`: all 23 tests passed.
This supersedes the regression failure above; scanners were not rerun for this
test-only correction.
