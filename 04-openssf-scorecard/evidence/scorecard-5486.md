# 證據：ossf/scorecard #5486

- status：`DUPLICATE_OR_IN_PROGRESS`
- last_verified_at：`2026-11-21T10:26:04Z`
- issue：open，無 assignee，無 label，0 則留言，建立於 `2026-11-18T22:38:33Z`，作者 `vishnums2k5`
- issue_updated_at：`2026-11-18T22:38:33Z`
- 重疊 PR：[#5487](https://github.com/ossf/scorecard/pull/5487)，open、非 draft。作者與 issue 相同，建立於 `2026-11-18T22:38:44Z`（issue 開出後 11 秒）
- overlap：`definite_duplicate`。GraphQL `closingIssuesReferences` 為 `[5486]`，PR 內文有 `Fixes #5486`
- 變更檔：`clients/gitlabrepo/searchCommits.go`（+6/-2）、`clients/gitlabrepo/searchCommits_test.go`（+109）
- PR base：`b62c617675f5dd81ba2bf89a065040559f92f8d7`。PR head：`2e5917a435077b01e65cd79c28c602ce0c5b7ca5`
- 外部 checkout：沒有建立。沒有做 GitLab API fixture，沒有跑測試，沒有補丁。已有修復 PR，不需要再重現

## 這次實際下的請求

`gh api --method GET repos/ossf/scorecard/issues/5486` 與 `pulls/5487`：第一次是 HTTP 404，但原因是代理自己的指令錯誤（zsh 的 `set -- $r` 不拆字，編號變成空字串，URL 錯了），不是 GitHub 異常。2026-11-21 用正確 URL 重讀：#5486 open、updated_at `2026-11-18T22:38:33Z`；#5487 open、非 draft。與搜尋和 GraphQL 結果一致。

`gh api --method GET search/issues`，查 `repo:ossf/scorecard gitlab panic commit`、`repo:ossf/scorecard 5486`、`repo:ossf/scorecard is:pr gitlab created:>2026-10-15`：成功。

`gh api graphql`（唯讀 query，無 mutation）：#5486、#5487 的 state、title、files，以及 #5487 的 `headRefOid`、`baseRefOid`、`closingIssuesReferences`、body。全部成功。

## GitLab handler 的擁擠程度

同時 open 的 GitLab 修復 PR：#5483、#5485、#5453、#5454（同為 `vishnums2k5`），#5489、#5490（`cvas22`），#5339（`XY-code1`），draft #5410。這些改的是 issues、merge request、release、CI 路徑與 Vulnerabilities，沒有一筆碰 `searchCommits.go`，記成相鄰工作，不算重複。
