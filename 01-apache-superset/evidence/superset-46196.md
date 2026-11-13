# 證據：apache/superset #46196

- status：`REPRO_PENDING`
- last_verified_at：`2026-11-13T16:55:05Z`
- 選單 / `aria-label`：`slice.description`
- 展開內容：只在 `slice.description_markdown` 有值時渲染
- API 對應：`description_markdown` 抄自 `description_markeddown`，不是 `description`
- 渲染：沿用既有、註解寫明經過 nh3 的 markdown 路徑
- 禁止：不要把不可信的 `description` 放進 `dangerouslySetInnerHTML`

還沒有 live chart 的 API 樣本，所以不寫修復。
