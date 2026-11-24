# 證據：apache/superset #46423

- status：`DUPLICATE_OR_IN_PROGRESS`
- last_verified_at：`2026-11-21T10:26:04Z`
- issue：open，無 assignee，無 label，建立於 `2026-11-21T04:35:35Z`，作者 `SEPURI-SAI-KRISHNA`
- issue_updated_at：`2026-11-21T05:06:01Z`
- 重疊 PR：[#46425](https://github.com/apache/superset/pull/46425)，open、非 draft，labels `size/M`、`doc`。作者與 issue 相同，建立於 `2026-11-21T05:05:58Z`（issue 開出後約 30 分鐘）
- overlap：`definite_duplicate`。GraphQL `closingIssuesReferences` 為 `[46423]`，PR 內文有 `Fixes #46423`
- 變更檔：`superset/mcp_service/chart/tool/get_chart_data.py`（+36/-7）、`tests/unit_tests/mcp_service/chart/tool/test_get_chart_data.py`（+50）、`docs/admin_docs/configuration/mcp-server.mdx`（+3）
- PR base：`9661a7b3bee7638a28a0dae6ec5c776d51b303a7`。PR head：`3424f053b85a539fb8b60e6616b0ddce5e6184de`
- 外部 checkout：沒有建立。沒有建 `=1+1` 測試資料，沒有跑測試，沒有補丁。已有修復 PR，不需要再重現

## 這次實際下的請求

`gh api --method GET repos/apache/superset/issues/46423` 與 `pulls/46425`：第一次是 HTTP 404，但原因是代理自己的指令錯誤（zsh 的 `set -- $r` 不拆字，編號變成空字串，URL 錯了），不是 GitHub 異常。2026-11-21 用正確 URL 重讀：#46423 open、updated_at `2026-11-21T05:06:01Z`；#46425 open、非 draft。與搜尋和 GraphQL 結果一致。

`gh api --method GET search/issues`，查 `repo:apache/superset MCP excel formula`、`repo:apache/superset 46423`：成功，列出 #46423 與 #46425。

`gh api graphql`（唯讀 query，無 mutation）：`issueOrPullRequest(number:46423)`、`issueOrPullRequest(number:46425)` 的 state、title、files，以及 #46425 的 `headRefOid`、`baseRefOid`、`closingIssuesReferences`、body。全部成功。

core rate limit 開始時是 4987/5000。

## 不是重複的搜尋命中

#45406（closed）是圖表 XLSX 匯出前置空白的公式，不是 MCP `get_chart_data`。#45817、#45332 是匯出格式與篩選設定，不碰公式轉義。#41133、#43232、#45456、#26721 是搜尋雜訊。
