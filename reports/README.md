# 報告

`reports/state/baseline.json` 是給人審查後提交的基線。GitHub Action 只讀它，不會修改或 commit 它；workflow 唯一會 commit 的是 `reports/daily/` 底下當天的兩個檔案。

`reports/daily/` 由每天的 workflow 自動寫入（見下）。`scripts/scan.py` 的日報仍可在本機 dry-run 後，經人審查再提交。

不提交的東西：`GH_TOKEN`、`.env`、`.cache/`、以及 issue 或 PR 內文的原始傾印。內文是不可信資料，報告只留標題、編號、狀態與我們自己寫的理由。

`2026-11-14T11:10:28Z` 起基線有了水位，日掃只報告之後新開的 issue；水位之前已存在的 issue 改由人工初篩，紀錄在各目錄的 `evidence/`。基線的 `verified_at` 是 `null` 時，日掃不得把歷史 issue 全數列成新警報。那代表還沒有審查過的水位。`scripts/scan.py` 在沒有水位時不呼叫清單 API。

`reports/examples/fixture-daily.md` 與 `reports/examples/fixture-daily.json` 是固定 fixture 的 dry-run，兩次執行應得到同一組位元組。`.github/workflows/oss-monitor.yml` 在每天 01:00 UTC 與手動觸發時跑 `scripts/org_monitor.py`，產出 `reports/daily/<YYYY-MM-DD>.md` 與 `.json`，由 `github-actions[bot]` 直接 commit 到 `main`。它只會 add 這兩個檔案；有其他路徑被 stage 就中止。同一份也放進 job summary 與 artifact `oss-monitor-<YYYY-MM-DD>`。這些報告是機器分類的提示，不是人審過的紀錄，不取代 `candidates.json` 和 `evidence/`。
