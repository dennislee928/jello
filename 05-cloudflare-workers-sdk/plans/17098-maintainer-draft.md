DRAFT

這份檔案是給人改寫的草稿。第一行 `DRAFT` 表示尚未張貼。代理與 workflow 都不得把這份草稿貼到上游 issue、discussion 或 pull request。

另一個前提：`dennislee928` 還不在 `.github/VOUCHED.td`。維護者同意方向也不能直接開 PR，要先處理 vouch。

## 要問維護者的問題

- org / repo：cloudflare/workers-sdk
- issue 或 PR 編號：#17098
- 問題（人寫，一問一事）：
  1. When `detectAgent().isAgent` is true, should destructive confirmations (`d1 delete`, `kv namespace delete`, `delete`, `secret delete`) fall back to "no" and exit non-zero, while CI keeps the current "yes"? Or should the fix live in `confirm()` itself, for example a `destructive` option?
  2. Is adding `-y/--skip-confirmation` to `wrangler secret delete` acceptable as part of the same change?
  3. Separately: is plain `wrangler whoami` exiting 0 when not logged in intended? Only `--json` is documented to exit non-zero.

## 已核對的事實

截至 2026-11-21T10:26:04Z，main 分支：

- `packages/wrangler/src/dialogs.ts:27-38`：`fallbackValue` 預設為 `true`，`isNonInteractiveOrCI()` 時直接回傳
- `d1/delete.ts:50`、`kv/index.ts:310`、`delete.ts:148`、`secret/index.ts:287` 都沒有覆寫 `fallbackValue`
- `utils/detect-agent.ts` 已在 `deploy/index.ts` 使用，刪除命令沒有用
- `user/whoami.ts:40` 只對 `json` 承諾非零結束碼
- 沒找到交叉引用的 PR

## 推論（另段）

改 `confirm()` 的全域預設會影響所有非互動呼叫，風險大於逐一在破壞性命令傳 `fallbackValue`。這是給人參考的推論，不是事實。

## 不要問的事

- 不要請維護者代為認領。
- 不要在分數語意還沒同意時，問「我直接改分數可以嗎」。
- 不要建議把不可信的描述塞進 `dangerouslySetInnerHTML`。

## 張貼前

人決定要不要貼、貼在哪個討論串。貼出之後把狀態與網址寫回 `candidates.json`，並拿掉這份副本的草稿用途。本檔保留 `DRAFT` 字樣，直到人明確改掉。
