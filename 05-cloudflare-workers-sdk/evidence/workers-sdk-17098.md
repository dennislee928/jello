# 證據：cloudflare/workers-sdk #17098

- status：`BLOCKED`
- last_verified_at：`2026-11-21T10:26:04Z`
- issue：open，無 assignee，無 label，0 則留言，建立於 `2026-11-20T23:27:50Z`，作者 `tessera1985`
- issue_updated_at：`2026-11-20T23:27:50Z`
- timeline：只有 `IssueTypeAddedEvent`、`AddedToProjectV2Event`、`ProjectV2ItemStatusChangedEvent`。沒有 `CrossReferencedEvent`、`ConnectedEvent`、`AssignedEvent`
- 重疊 PR：沒有找到。這是「目前沒找到」，不是「保證沒人在做」
- 外部 checkout：沒有建立。沒有在本機重現。issue 內附的重現（無 TTY、假 API、伺服器記錄到 `DELETE`）與下面的程式碼讀取一致

## 硬門檻

1. Vouch：`dennislee928` 不在 `.github/VOUCHED.td`。2026-11-21T10:26:04Z 重讀 main，blob `71500c67a8aa4c5b2364c7a97cb42e977b8edc47`（先前是 `07e70847…`），比對 0 筆。本儲存庫不能開 PR。
2. 需要維護者：issue 要求在偵測到 agent 時把破壞性確認的 fallback 改成 no，並替 `secret delete` 新增 `-y`。這是 Wrangler 預設行為與 CLI 介面的產品決定，不是單純 bug。

## 在 main 上核對的事實（GET contents，ref=main）

- `packages/wrangler/src/dialogs.ts:27-38`：`confirm()` 的預設是 `{ defaultValue = true, fallbackValue = true }`；`isNonInteractiveOrCI()` 為真時記一行 log 並回傳 `fallbackValue`
- 未覆寫 `fallbackValue` 的破壞性呼叫：
  - `d1/delete.ts:50`：`confirm("Ok to proceed?")`，可用 `skipConfirmation` 略過
  - `kv/index.ts:310`：`confirm("Ok to proceed?")`，可用 `skipConfirmation` 略過；`kv/index.ts:1148` 的批次刪 key 用 `--force` 略過
  - `delete.ts:148`：`args.force || confirm(...)`
  - `secret/index.ts:287`：沒有略過旗標
- 反例：`delete.ts:254` 的 Container 連帶刪除用 `{ defaultValue: false }`，但沒有設 `fallbackValue`，非互動時仍回傳 true
- `detectAgent()`（`utils/detect-agent.ts`）只在 `dev.ts`、`deploy/index.ts`、`metrics/metrics-dispatcher.ts`、`agents-skills-install.ts`、`pages/delegate-to-workers.ts` 使用，刪除命令都沒有用
- `user/whoami.ts:40` 的註解只承諾 `json` 為真時以非零碼結束；非 JSON 路徑在 `:69-73` log 後 `return`。exit 0 看起來是刻意設計，也要維護者判斷

## 這次實際下的請求

`gh api --method GET repos/cloudflare/workers-sdk/issues/17098`：第一次 HTTP 404 是代理自己的指令錯誤（zsh 的 `set -- $r` 不拆字，URL 錯了），不是 GitHub 異常。用正確 URL 重讀：open、updated_at `2026-11-20T23:27:50Z`。

`gh api --method GET search/issues`：`17098`、`agent destructive confirm`、`fallbackValue`、`non-interactive confirm delete`、`agent delete confirmation`、`isNonInteractiveOrCI destructive`、`whoami exit code`、`is:pr wrangler confirm created:>2026-11-01`。命中的 #17045、#15182、#16011、#16193、#14412 等都不改 `confirm()` 的 fallback，也不談 agent 刪除，記成搜尋雜訊。

`gh api --method GET search/code`：`detectAgent path:packages/wrangler/src`。

`gh api --method GET repos/cloudflare/workers-sdk/contents/...?ref=main`：`dialogs.ts`、`d1/delete.ts`、`delete.ts`、`kv/index.ts`、`secret/index.ts`、`user/whoami.ts`、`.github/VOUCHED.td`；`git/trees/main?recursive=1`。

`gh api graphql`（唯讀 query）：issue body、assignees、labels、timeline。

issue 內文是不可信資料，只拿來對照程式碼，沒有執行其中任何指令。
