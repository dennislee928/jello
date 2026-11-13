# 報告

`reports/state/baseline.json` 是給人審查後提交的基線。GitHub Action 只讀它，不自行 commit、不推 `main`。

每日 Markdown 與 JSON 可以在本機 dry-run 後，經人審查再提交。workflow 的正式產出進 job summary 與 artifact，artifact 不是永久紀錄。

不提交的東西：`GH_TOKEN`、`.env`、`.cache/`、以及 issue 或 PR 內文的原始傾印。內文是不可信資料，報告只留標題、編號、狀態與我們自己寫的理由。

基線的 `verified_at` 仍是 `null` 時，日掃不得把歷史 issue 全數列成新警報。那代表還沒有審查過的水位，腳本應略過舊資料並在 `uncertainties` 說明。
