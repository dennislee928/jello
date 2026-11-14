# Security checks

Run `python -m pip install bandit==1.8.6`, then `python scripts/test/security.py`.
Docker must be running; Trivy downloads its vulnerability database. Optional:
`python scripts/test/security.py --image registry.example/app@sha256:DIGEST`.
No image is built or application started automatically.

CI-SEC runs on pushes, pull requests and manual dispatch with contents: read,
no persisted checkout credentials, and no upstream writes. Reports are artifacts,
not commits. It fails on medium/high Bandit findings, high/critical Trivy findings,
regression failures, missing tools and scanner errors. See raw JSON and stderr to
distinguish findings from execution failures. Reports may contain sensitive source
excerpts; artifacts expire in seven days. Secret scanning covers the working tree,
not git history. The scanner image is digest-pinned; pip transitive dependencies remain mutable;
review and refresh scanner pins periodically.

Coverage: Python SAST (Bandit); supported dependency vulnerability matching,
secrets and IaC configuration (Trivy); CycloneDX SBOM; existing CLI regression
suite; optional image OS/library vulnerability and secret scanning. SBOM is an
inventory, not evidence of safety. No dependency manifest exists for this stdlib
CLI, so dependency coverage may be empty. Python interpreter, host packages and
GitHub runner software are not inventoried by the filesystem scan. DAST and IAST
are not applicable without a deployed app and instrumentation; unit tests are not
IAST. Named upstream projects are research records, not checked-out source targets.

Tool references:
- https://bandit.readthedocs.io/en/latest/man/bandit.html
- https://trivy.dev/docs/latest/guide/target/filesystem/
