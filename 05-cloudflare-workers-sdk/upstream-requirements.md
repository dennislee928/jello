# Cloudflare Workers SDK 上游規則

這份筆記只適用 `cloudflare/workers-sdk` 的 `main`。外部 checkout 是 `/Users/dennis/Desktop/upstream-src/cloudflare/workers-sdk`。本協調庫不跑 `pnpm`，也不挑 wrangler issue。

## 政策檔

`CONTRIBUTING.md` 與 `.github/VOUCHED.td`。貢獻門檻是 Vouch：沒有 write access，且登入帳號不在 `VOUCHED.td`，新 PR 會被自動關閉。要核對的帳號是 `dennislee928`。比對時用完整登入字串，不用顯示名稱，也不把組織成員身分當成已註冊。

已註冊協作者的文件命令是 `pnpm test -F wrangler`、`pnpm check`、`pnpm changeset`。這些命令在帳號仍被封鎖時不執行。即使以後註冊了，也要先重讀 `CONTRIBUTING.md` 再跑。

## 本次驗證

last_verified_at: null

<!-- policy-shas:start -->
尚未以 `gh api` 重抓 `CONTRIBUTING.md` 與 `.github/VOUCHED.td` 的 blob SHA。
<!-- policy-shas:end -->

## 現在不做的事

不選 implementation issue，不開 discussion 問「可以先做哪個 good first issue」，不把 Workers 的 API 變更寫進其他四個目錄。`acceptance_score` 在資格確認前保持低分，`impact_score` 維持未知，不估使用者數。

狀態是 `BLOCKED`，直到 `VOUCHED.td` 的本次重抓證明 `dennislee928` 在名單裡，或人另外取得 write access。兩件事都還沒發生時，不要把封鎖改成 `UNVERIFIED` 來表示「也許可以做」。API 讀不到該檔時才改 `UNVERIFIED`。
