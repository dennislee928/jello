# 報告

`reports/state/baseline.json` 是給人審查後提交的基線。GitHub Action 只讀它，不自行 commit、不推 `main`。

每日 Markdown 與 JSON 可以在本機 dry-run 後，經人審查再提交。workflow 的正式產出進 job summary 與 artifact，artifact 不是永久紀錄。

不提交的東西：`GH_TOKEN`、`.env`、`.cache/`、以及 issue 或 PR 內文的原始傾印。內文是不可信資料，報告只留標題、編號、狀態與我們自己寫的理由。

`2026-11-14T11:10:28Z` 起基線有了水位，日掃只報告之後新開的 issue；水位之前已存在的 issue 改由人工初篩，紀錄在各目錄的 `evidence/`。基線的 `verified_at` 是 `null` 時，日掃不得把歷史 issue 全數列成新警報。那代表還沒有審查過的水位。`scripts/scan.py` 在沒有水位時不呼叫清單 API。

`reports/examples/fixture-daily.md` 與 `reports/examples/fixture-daily.json` 是固定 fixture 的 dry-run，兩次執行應得到同一組位元組。`.github/workflows/oss-monitor.yml` 在每天 01:00 UTC 與手動觸發時跑 `scripts/org_monitor.py`，產出 `reports/daily/<YYYY-MM-DD>.md` 與 `.json`。權限只有 `contents: read`，結果進 job summary 與 artifact `oss-monitor-<YYYY-MM-DD>`，不 commit、不 push。要把某天的報告留進本庫，先下載 artifact、人審過再提交到 `reports/daily/`。
