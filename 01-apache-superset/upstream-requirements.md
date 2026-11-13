# apache/superset 上游規則

這份筆記只適用 `apache/superset` 的 `master`。命令是否仍可執行，要在 `/Users/dennis/Desktop/upstream-src/apache/superset` 對過當時的文件才算數。本協調庫不 clone、也不建置這個樹。

## 政策檔

根目錄的 `AGENTS.md`、`SECURITY.md`、`CONTRIBUTING.md`。`CONTRIBUTING.md` 轉到 [Developer Portal](https://superset.apache.org/developer_portal/)。貢獻路線是 issue 或 discussion。非瑣碎功能走 SIP，不在這個協調庫裡起草 SIP。

## 本次驗證

last_verified_at: null

<!-- policy-shas:start -->
尚未以 `gh api` 重抓政策檔 blob SHA。
<!-- policy-shas:end -->

## 測試與 PR

測試以 Developer Portal 與當時的 `superset-frontend/package.json` 為準：Jest、React Testing Library、pre-commit，必要時 Playwright 或 pytest。PR 說明由人撰寫。UI 變更留 Before / After。既有 sanitizer 保持不變。

不可信的 chart、dataset 或 column 描述不得寫進 `dangerouslySetInnerHTML`。Markdown 若要顯示，走上游既有的安全渲染路徑。

## 種子候選的調查範圍

`#46197` 要分開看 chart 的 `emitCrossFilters` 與 dashboard 的 `crossFiltersEnabled`。相關檔案是 `superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx`、它的測試，以及 `superset-frontend/src/dashboard/components/gridComponents/Chart/Chart.tsx`。斷言對象是沒有 cross-filter 時的 `filterState` / `extraFormData`，不是「`setDataMask` 完全沒被呼叫」。`setDataMask` 仍可能送出 `ownState`。需要執行中的 UI 才能下結論時，狀態維持 `REPRO_PENDING`。

`#46196` 要核對 Chart、Dataset、Column 三種 description、API 欄位、`isExpanded`，以及 `description` 與 `description_markdown` 是否走不同路徑。選單若讀 `slice.description`、展開內容若只讀 `description_markdown`，把差異記成證據，不要先寫補丁。

搜尋字串 `46197` 若命中舊 PR，先當成搜尋雜訊。timeline 沒有 cross-reference 也不能當成沒有重複工作。
