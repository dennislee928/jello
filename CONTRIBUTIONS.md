# 貢獻索引

這個索引把已驗證事實與推論分開。它不是上游專案的下載統計。候選 issue 與尚未合併的 PR 不計入影響。

最後對過協調庫現況的時間是 `2026-11-13T16:42:51Z`（唯讀快照的 `last_verified_at`）。那天沒有本儲存庫作者合併到上游的 pull request。

## 總表

| 欄位 | verified | inferred |
| --- | --- | --- |
| author | 無已合併 PR，不填作者 | 不把 git 身分推測成上游作者 |
| PR URL | 無 | 不把他人的 open PR 寫成這份索引的合併 |
| merge SHA | 無 | 無 |
| release | 無 | 不把上游既有 release 算到尚未存在的修復 |
| 測試紀錄 | 沒有為了主張修復而跑過上游測試 | 文件裡的 `mage`、`make`、`pnpm` 命令不是已通過的紀錄 |
| 使用量 | unknown | 不引用 Superset、OpenTelemetry、Trivy、Scorecard、Workers SDK 的星數、下載次數或 Action 安裝數 |

## Verified

沒有已合併的 pull request。沒有 merge SHA，沒有對應的 release，也沒有可歸因到本協調庫變更的測試輸出。

使用量是 `unknown`。沒有合併 PR 時，不估計人數，也不把空格當成零。

## Inferred

推論欄目前沒有可以安全寫下的影響。已知碰撞與仍在 `BLOCKED`、`NEEDS_MAINTAINER`、`UNVERIFIED` 的候選都還沒有修復可以歸因。

詳細的空白紀錄在 `reports/cv-impact.md`。
