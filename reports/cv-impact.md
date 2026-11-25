# CV 影響

這份是目前的影響紀錄，不是範本。範本在 `templates/cv-impact-record.md`。索引在 `CONTRIBUTIONS.md`。

last_verified_at：`2026-11-24T12:27:50Z`

## 識別

- author：`dennislee928`
- org / repo：`apache/superset`
- PR URL：https://github.com/apache/superset/pull/46141
- merge SHA：`578451c5c82d08d78a1daa28a17cd75376809d06`
- release：尚未發版（不在 `7.0.0rc3`）
- last_verified_at：`2026-11-24T12:27:50Z`

## 測試紀錄

| 命令 | 工作目錄 | 結果 |
| --- | --- | --- |
| 無紀錄 | 無 | 本協調庫沒有保存 `#46141` 的上游測試輸出；PR 由上游 CI 驗過（標籤 `merge-if-green`），但這不是本地命令紀錄 |

本協調庫的 `python3 -m unittest discover -s tests` 只檢查協調庫自己的去重與日報，不是上游修復的測試紀錄。

## Verified

| 欄位 | 值 | 證據 |
| --- | --- | --- |
| author | `dennislee928` | `GET repos/apache/superset/pulls/46141` |
| PR URL | `apache/superset#46141` "fix(bubble): preserve null labels in tooltip titles" | 同上 |
| merge SHA | `578451c`，`2026-11-18T02:28:30Z`，base `master` | 同上 |
| release | 無 | `compare 578451c...7.0.0rc3` 為 `diverged`；rc3 沒有對應 cherry-pick（`reports/evidence/recheck-2026-11-24-roi-five.md`） |
| 測試紀錄 | 無上游命令輸出 | 見上 |
| 使用量 | unknown | 尚未進任何 release |
| 調查重讀 | `2026-11-13T16:55:05Z` | 當時仍無 `MERGED` 或 `RELEASED` |
| Superset `#46196` 重查 | `2026-11-14T10:24:51Z` | 已由他人合併的 `#41453` 修好，不歸因到本協調庫 |

## Inferred

| 欄位 | 推論 | 為什麼還不是事實 |
| --- | --- | --- |
| release | 可能隨下一個從 `master` 切出的版本發出 | 7.0 線若不 cherry-pick 就不會帶到；要等 tag 出來再用 `compare` 確認 |
| 使用量 | 不推論 | 上游下載數、星數屬於整個專案，不屬於這筆修復；正式版出來前不建立基準 |

## 使用量

unknown
