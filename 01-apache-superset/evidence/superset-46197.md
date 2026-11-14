# 證據：apache/superset #46197

- status：`DUPLICATE_OR_IN_PROGRESS`
- last_verified_at：`2026-11-14T02:09:58Z`
- issue：open，無 assignee，labels 為 `#bug`、`review:checkpoint`、`🦾 ai-candidate`
- issue_updated_at：`2026-11-13T18:19:33Z`
- 重疊 PR：[#46202](https://github.com/apache/superset/pull/46202)，open、非 draft、`merged` 為 false
- overlap：`definite_duplicate`。timeline 有同儲存庫 PR 交叉引用，PR 內文有 `Fixes #46197`
- 變更檔：`superset-frontend/src/dashboard/components/gridComponents/Chart/Chart.tsx`、`Chart.test.tsx`
- PR base：`a0f120285ad416a8bbb7d9367c354986ffea40f7`。PR head：`e14dffc01c22b2225ddc666907909d0b3ee767e2`。這不是本機 checkout 的 HEAD
- 外部 checkout：沒有建立。沒有跑測試，沒有補丁

## 這次實際下的 GET

`gh api --method GET repos/apache/superset/issues/46197`

`gh api --method GET --paginate repos/apache/superset/issues/46197/timeline`

`gh api --method GET repos/apache/superset/pulls/46202` 與該 PR 的 files、comments、reviews

搜尋 `repo:apache/superset is:pr`，分別加上 `46197`、`is:open`、`is:closed`、`is:merged`、`is:draft cross-filter table`、`emitCrossFilters`、`chartsInScope cross-filter`、`"cross-filtering" disabled table`。全部 HTTP 成功。core 剩餘在開始時是 4995/5000。

## emitCrossFilters、crossFiltersEnabled、ownState

#46202 刪掉的現行程式只做 `!!state.dashboardInfo.crossFiltersEnabled`。加上的條件才讀 `chart_configuration[id].crossFilters.chartsInScope`：dashboard 旗標為假就不會 emit；`chartsInScope` 存在且沒有其他 chart 時也不 emit。

這份 PR 沒有改 `ownState`。先前讀過的 `updateTableOwnState` 仍是另一條 `setDataMask({ ownState })`，不在這次重疊範圍。斷言仍然不是「`setDataMask` 零呼叫」。

## 不是重複的搜尋命中

`46197` 搜尋另外命中已合併的 #45242、#21958、#21821、#21523。四份內文都沒有 `46197`，也沒有關閉這個編號，記成搜尋雜訊。

#42155 已合併，關閉的是 #42010，內容是表格分頁，不是這張 chart scope。

open #44665 改 cell bar，測試仍把 `emitCrossFilters` 設成 true，沒有 chart scope 閘門。

draft #41548 把 `emitCrossFilters` 改成 `useCrossFiltersEnabled()`，該 hook 只選 dashboard 旗標，沒有 `chartsInScope`。

closed draft #22604 是表格連結，不是這個 bug。

沒有留言、認領、fork、推送或開上游 PR。沒有把原始碼複製進本儲存庫。
