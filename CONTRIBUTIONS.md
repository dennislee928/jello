# 貢獻索引

這個索引把已驗證事實與推論分開。它不是上游專案的下載統計。候選 issue 與尚未合併的 PR 不計入影響。

最後對過協調庫現況的時間是 `2026-11-13T16:42:51Z`；`2026-11-24T12:27:50Z` 補登已合併的 `apache/superset#46141`（見 `reports/evidence/recheck-2026-11-24-roi-five.md`）（唯讀快照的 `last_verified_at`）。調查重讀是 `2026-11-13T16:55:05Z`。`2026-11-14T02:09:58Z` 又核對了 `apache/superset` `#46197`：重疊的是他人的 open PR `#46202`，不是本協調庫的合併。`2026-11-14T10:24:51Z` 核對 `#46196`：根因已由他人合併的 `#41453`（`834ccf2`）修好，同樣不是本協調庫的合併。這幾次都沒有本儲存庫作者合併到上游的 pull request。

## 總表

| 欄位 | verified | inferred |
| --- | --- | --- |
| author | `dennislee928`（GitHub API 的 PR author） | 不把 git 身分推測成上游作者 |
| PR URL | https://github.com/apache/superset/pull/46141 | 不把他人的 open PR 寫成這份索引的合併 |
| merge SHA | `578451c5c82d08d78a1daa28a17cd75376809d06`（`2026-11-18T02:28:30Z`，`master`） | 無 |
| release | 尚未發版：不在 `7.0.0rc3`（`compare` 為 `diverged`） | 不把 rc 或上游既有 release 算到這筆修復 |
| 測試紀錄 | 沒有為了主張修復而跑過上游測試 | 文件裡的 `mage`、`make`、`pnpm` 命令不是已通過的紀錄 |
| 使用量 | unknown | 不引用 Superset、OpenTelemetry、Trivy、Scorecard、Workers SDK 的星數、下載次數或 Action 安裝數 |

## Verified

一筆已合併：`apache/superset#46141` "fix(bubble): preserve null labels in tooltip titles"，merge SHA `578451c`，`2026-11-18T02:28:30Z` 合進 `master`。截至 `2026-11-24T12:27:50Z` 沒有包含它的 release（最新 `7.0.0rc3` 不含）。本協調庫沒有它的上游測試輸出紀錄。

使用量是 `unknown`。尚未進正式版，不估計人數，也不把空格當成零。

## Inferred

推論欄目前沒有可以安全寫下的影響。已知碰撞，以及仍在 `BLOCKED`、`NEEDS_MAINTAINER`、`REPRO_PENDING`、`UNVERIFIED` 的候選，都還沒有修復可以歸因。讀過上游檔案不是合併，也不產生使用量。

詳細的空白紀錄在 `reports/cv-impact.md`。
