# anchore

| 儲存庫 | 預設分支 | 本目錄怎麼對待 |
| --- | --- | --- |
| `anchore/vunnel` | `main` | Grype 漏洞資料的 provider 集合（Python）。外部 PR review 慢，合併多半來自維護者 |

外部 checkout 是 `/Users/dennis/Desktop/upstream-src/anchore/vunnel`。原始碼不放進本儲存庫。

這個目錄是 `2026-11-25` 為 `#1486` 手動加入的，還沒列進 `config/targets.json`，所以日掃不會覆寫 `candidates.json`。

`#1486`（secureos 的 APK 版本比較）在 `2026-11-25T14:41:09Z` 是 `READY_FOR_HUMAN_PR`。交付檔是 `plans/vunnel-1486-pr-draft.md`，證據在 `evidence/vunnel-1486.md`。
