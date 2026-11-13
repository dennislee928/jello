# Workers SDK 資格再確認

last_verified_at：`2026-11-13T16:55:05Z`

狀態維持 `BLOCKED`。沒有選實作 issue。只使用 `gh api` GET。

`CONTRIBUTING.md` blob `a111550aec4e1a918dd7de4bfa055faa32d4eff9` 寫明 pull request 只限註冊協作者：有 repository write access，或被維護者註冊的人。工具是 Vouch。未註冊者要先在 issue 討論，而不是先開 PR。

`.github/VOUCHED.td` blob 仍是 `07e70847237830bfe929b0c7480e5e5a38a729ad`。以完整登入字串比對，`dennislee928` 不在檔內。

因此不挑 wrangler issue，也不起草 PR。`pnpm test -F wrangler`、`pnpm check`、`pnpm changeset` 在資格仍被封鎖時不執行。
