# Aqua Security Trivy

這個目錄同時協調四個儲存庫，規則不互通：

| 儲存庫 | 本目錄怎麼對待 |
| --- | --- |
| `aquasecurity/trivy` | 掃描器本體。已知碰撞 PR 只當去重 fixture |
| `aquasecurity/trivy-action` | GitHub Action。`#551` 只做設計筆記 |
| `aquasecurity/setup-trivy` | 另一個 Action。`#40` 與 `#43` 用來對照下載路徑 |
| `aquasecurity/trivy-db` | 漏洞資料庫。`#702` 是已知碰撞 |

外部 checkout 分別是 `/Users/dennis/Desktop/upstream-src/aquasecurity/trivy`、`trivy-action`、`setup-trivy`、`trivy-db`。不要為了協調庫去建置 Trivy。

已知碰撞維持 `DUPLICATE_OR_IN_PROGRESS`，不選為修復。新候選要先走 Discussion 與維護者建立的 issue，並排除既有碰撞編號。
