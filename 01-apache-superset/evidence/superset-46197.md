# 證據：apache/superset #46197

- status：`REPRO_PENDING`
- last_verified_at：`2026-11-13T16:55:05Z`
- `emitCrossFilters`：dashboard `Chart.tsx` 只反映 `crossFiltersEnabled`
- `setDataMask`：cross-filter 路徑會帶 `filterState` 與 `extraFormData`；`ownState` 路徑另走 `updateTableOwnState`，內容只有 `ownState`
- 測試：`TableChart.test.tsx` 的 cross-filter 案例使用 `emitCrossFilters: true`
- 結論：原始碼分得開這兩條 `setDataMask`，但分不開「單一 chart 關閉」與 dashboard 旗標。需要 UI 重現

blob SHA 記在 `plans/46197.md`。沒有複製原始碼。
