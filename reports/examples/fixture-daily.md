# OSS Contribution Hub 日報

- verified_at：`2026-11-14T01:00:00Z`
- partial：是
- baseline：`tests/fixtures/scan_fixture.json`
- baseline verified_at：`2026-11-01T00:00:00Z`
- 略過的舊項目：2

標題與理由已壓成單行文字。它們是不可信資料，這份報告不執行它們。

## 掃描目標

- `apache/superset`
- `open-telemetry/opentelemetry-collector-contrib`
- `open-telemetry/opentelemetry-go`
- `open-telemetry/opentelemetry-js`
- `aquasecurity/trivy`
- `aquasecurity/trivy-action`
- `aquasecurity/setup-trivy`
- `aquasecurity/trivy-db`
- `aquasecurity/trivy-operator`
- `ossf/scorecard`
- `cloudflare/workers-sdk`
- `OWASP/cve-lite-cli`
- `CycloneDX/cyclonedx-go`

## 新的合格項目

- `apache/superset#200` issue React dashboard drops API values unsafe。原因：在 2026-11-01T00:00:00Z 之後新開，標題符合關鍵字 React。訊號：keyword:React, bonus:good first issue。 https://github.com/apache/superset/issues/200
- `ossf/scorecard#400` pull_request supply chain SBOM parser check。原因：在 2026-11-01T00:00:00Z 之後新開，標題符合關鍵字 SBOM。訊號：keyword:SBOM。 https://github.com/ossf/scorecard/pull/400

## 實質狀態變化

- `apache/superset#101` assignees：（空） -> octocat。 https://github.com/apache/superset/issues/101
- `apache/superset#101` comment_count：1 -> 2。 https://github.com/apache/superset/issues/101

## 不確定

- `aquasecurity/trivy` 這個儲存庫讀取失敗，受影響項目維持 UNVERIFIED

## 錯誤

- `aquasecurity/trivy` HTTP 429：HTTP 429
