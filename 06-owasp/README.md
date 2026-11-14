# OWASP

這個目錄協調兩個 OWASP 專案的儲存庫，規則不互通：

| 儲存庫 | 預設分支 | 本目錄怎麼對待 |
| --- | --- | --- |
| `OWASP/cve-lite-cli` | `main` | npm 依賴的 SCA CLI。starter issue 多、外部 PR 合併快，但「先做出可用 PR 的人勝出」，撞車風險高 |
| `CycloneDX/cyclonedx-go` | `master` | CycloneDX SBOM 的 Go 函式庫。CycloneDX 是 OWASP 旗艦專案，但 GitHub org 是 `CycloneDX`，不是 `OWASP` |

外部 checkout 是 `/Users/dennis/Desktop/upstream-src/OWASP/cve-lite-cli` 與 `/Users/dennis/Desktop/upstream-src/CycloneDX/cyclonedx-go`。原始碼不放進本儲存庫。

## 為什麼選這兩個

`2026-11-14` 用 `gh api` GET 取最近 100 個 closed PR，只算外部作者（`author_association` 為 CONTRIBUTOR、FIRST_TIME_CONTRIBUTOR、FIRST_TIMER、NONE，排除 bot）：

| 儲存庫 | 外部 PR 合併 | 合併中位天數 |
| --- | --- | --- |
| `OWASP/cve-lite-cli` | 63 / 79 | 2.9 |
| `CycloneDX/cyclonedx-go` | 14 / 17 | 4.1 |

這是接受度的 proxy，不是保證。同一輪也量過 `OWASP/threat-dragon`（3 / 10）、`OWASP/Nest`（12 / 41）、`OWASP/wrongsecrets`（9 / 11，但主要是 Java 與 HTML），這輪不收。星數與下載數只算生態系層級的 proxy，不歸因到單一修復。

目前沒有 `READY_TO_IMPLEMENT` 候選。`2026-11-14T11:15:59Z` 初篩 `cve-lite-cli` 的 18 個 starter issue，全部是 `DUPLICATE_OR_IN_PROGRESS`（`evidence/cve-lite-cli-triage-2026-11-14.md`）。這個 repo 撞車快：新 issue 常在一兩天內就有 PR，所以要靠日掃的新 issue，不要靠舊清單。`cyclonedx-go` 只有兩個舊的 starter issue，尚未初篩。規則在 `upstream-requirements.md`。
