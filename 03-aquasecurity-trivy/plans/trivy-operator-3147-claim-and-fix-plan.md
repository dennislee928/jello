DRAFT

# trivy-operator #3147：認領要求與備援修復計畫

- verified_at：`2026-11-18`（`gh api` GET）
- 判定：`DUPLICATE_OR_IN_PROGRESS`，**不留言認領**

## 認領要求（issue 與規則）

- issue 沒有 assignee，也沒有留言。回報者只寫了建議修法，沒有認領
- `CONTRIBUTING.md`（blob `22cf3a81`）沒有認領流程，只有「Issues and Discussions」的開 issue 規則。aquasecurity 的 repo 用 CLA assistant
- 但已經有兩個 open PR 在修同一處 `pkg/vulnerabilityreport/io.go` 的 `GetVulnerabilitiesFromScanResult`：
  - `#3117`（`xcompass`，`2026-10-27`，2 個檔案，+87/−4，"keep Trivy's severity when SeveritySource has no vendor rating"）
  - `#3026`（`alexchen-sys`，`2026-07-24` 開、`2026-10-15` 更新，2 個檔案，+164/−4，"fallback to highest vendor severity when SeveritySource is missing"）
- 兩個 PR 都還沒有 review。trivy 系的維護者處理重複 PR 的方式是保留最早的、其餘關掉（見 `03-aquasecurity-trivy/evidence/good-first-issue-triage-2026-11-18.md`）

## 留言要點

- **現在不留言**。再開第三個 PR 只會被當成重複
- 能做、而且不算搶的事：在 issue 補一則事實留言，說明 `#3117` 與 `#3026` 都在修這件，方便維護者把三者連起來。要不要留由人決定，留言由人寫
- 只有在兩個 PR 都被關掉、或作者明說不做時，才考慮認領。到那時留言要涵蓋：
  - 根因位置：`io.go` 第 153–154 行，`sr.VendorSeverity[sr.SeveritySource].String()` 在 `SeveritySource` 為空時得到 `UNKNOWN`
  - 打算採用哪一種行為（見下方）

## 備援修復計畫（只在接手時才用）

- 兩個 PR 的行為不一樣，要先請維護者選：
  - `#3117`（以及 issue 的建議）：直接用 `sr.Severity`，也就是 Trivy 已經依 vendor 優先序與 `--vuln-severity-source` 算好的值
  - `#3026`：取 vendor 嚴重度中最高的。這和 Trivy CLI 的結果可能不一致
- 建議 `#3117` 的方向，因為 issue 的期望就是「operator 的報告與 Trivy 一致」
- 測試：在 `pkg/plugins/trivy/testdata/fixture` 加一筆 `SeveritySource` 為空、`Severity: HIGH` 的 fixture，斷言報告裡是 `HIGH`；`SeveritySource` 有值的 case 結果要不變
- 命令：`go test ./pkg/vulnerabilityreport/... ./pkg/plugins/trivy/...`、`make lint`（以 repo 的 Makefile 為準）
