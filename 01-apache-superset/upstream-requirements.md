# apache/superset 上游規則

這份筆記只適用 `apache/superset` 的 `master`。命令是否仍可執行，要在 `/Users/dennis/Desktop/upstream-src/apache/superset` 對過當時的文件才算數。本協調庫不 clone、也不建置這個樹。

## 政策檔

根目錄的 `AGENTS.md`、`SECURITY.md`、`CONTRIBUTING.md`。`CONTRIBUTING.md` 轉到 [Developer Portal](https://superset.apache.org/developer_portal/)。貢獻路線是 issue 或 discussion。非瑣碎功能走 SIP，不在這個協調庫裡起草 SIP。

## 本次驗證

last_verified_at: 2026-11-13T16:42:51Z

<!-- policy-shas:start -->
| 儲存庫 | 分支 | 路徑 | blob SHA |
| --- | --- | --- | --- |
| `apache/superset` | `master` | `AGENTS.md` | `5215a70bf032e0503c4ea3e8d0ee28f8976c46ef` |
| `apache/superset` | `master` | `CONTRIBUTING.md` | `d715949be7177f3922faa22abb5197f1efe70624` |
| `apache/superset` | `master` | `SECURITY.md` | `8e5b8a6076fdc65d81473d43bb0de60a9074104b` |
<!-- policy-shas:end -->

## 測試與 PR

測試以 Developer Portal 與當時的 `superset-frontend/package.json` 為準：Jest、React Testing Library、pre-commit，必要時 Playwright 或 pytest。PR 說明由人撰寫。UI 變更留 Before / After。既有 sanitizer 保持不變。

不可信的 chart、dataset 或 column 描述不得寫進 `dangerouslySetInnerHTML`。Markdown 若要顯示，走上游既有的安全渲染路徑。

## 種子候選的調查範圍

`#46197` 要分開看 chart 的 `emitCrossFilters` 與 dashboard 的 `crossFiltersEnabled`。相關檔案是 `superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx`、它的測試，以及 `superset-frontend/src/dashboard/components/gridComponents/Chart/Chart.tsx`。斷言對象是沒有 cross-filter 時的 `filterState` / `extraFormData`，不是「`setDataMask` 完全沒被呼叫」。`setDataMask` 仍可能送出 `ownState`。需要執行中的 UI 才能下結論時，狀態維持 `REPRO_PENDING`。

`#46196` 要核對 Chart、Dataset、Column 三種 description、API 欄位、`isExpanded`，以及 `description` 與 `description_markdown` 是否走不同路徑。選單若讀 `slice.description`、展開內容若只讀 `description_markdown`，把差異記成證據，不要先寫補丁。

搜尋字串 `46197` 若命中舊 PR，先當成搜尋雜訊。timeline 沒有 cross-reference 也不能當成沒有重複工作。

## 調查重讀

investigation_verified_at: 2026-11-13T16:55:05Z

指定檔案已用 `gh api` GET 讀過。`#46197` 與 `#46196` 都是 `REPRO_PENDING`。`emitCrossFilters` 只反映 dashboard 的 `crossFiltersEnabled`；`setDataMask` 的 `ownState` 路徑另外存在。`description` 與 `description_markdown` 在 hydrate 時分開。沒有補丁，也沒有把不可信描述放進 `dangerouslySetInnerHTML`。紀錄在 `plans/46197.md` 與 `plans/46196.md`。
