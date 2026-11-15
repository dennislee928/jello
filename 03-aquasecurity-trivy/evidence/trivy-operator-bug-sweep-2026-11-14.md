# 證據：aquasecurity/trivy-operator bug 掃描

- last_verified_at：`2026-11-14T11:23:23Z`
- 方法：
  - 列出沒有 assignee 的 `kind/bug`、`bug`，以及全部沒有 assignee 的 open issue（145 個）。
  - 排除 `triage/*` 的結案類標籤、`kind/feature`、`kind/documentation`，以及已有 open 或 merged PR 的。
- 只用 `gh api` GET。沒有留言，沒有補丁。

2026-05 之後沒有 PR 的只有 3 個：

| issue | 判定 |
| --- | --- |
| `#3061` | 資安通報（RCE，GHSA 沒有回覆）。走私下通報，不碰 |
| `#3050` | 透過 NAT gateway 的流量成本。屬設定問題，也受 Trivy server 不快取 java-db 的限制（`aquasecurity/trivy#3560`），不是範圍明確的修復 |
| `#3027` | 0.30.0 起 private registry 出現 `x509: certificate signed by unknown authority`，`insecureRegistries` 無效。stack 的 `scanjob.go:103` 只是讀取 scan container 的結果，錯誤來自 job 裡的 Trivy，可能是 Trivy 版本升級帶來的。要重現得有 kind 叢集加自簽 CA 的 registry；3.5 個月沒有維護者回覆。記成 `REPRO_PENDING`，這輪不做 |

`#2736` 與 `#2896` 的初篩見 `trivy-operator-triage-2026-11-14.md`。
