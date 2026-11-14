# OWASP 上游規則

兩個儲存庫各自驗證。外部 checkout 根目錄是 `/Users/dennis/Desktop/upstream-src/`。本協調庫不執行它們的 build 或測試；命令只在外部 checkout 對過文件後才跑。

## OWASP/cve-lite-cli

- 授權：MIT。CONTRIBUTING 寫明貢獻是自願、無償；提議付費安排的 issue 或 PR 不會被接受。
- 選題：`good first issue` 或 `help wanted`。CONTRIBUTING 寫「You do not need permission to start」，留言告知是禮貌、不是保留。兩人做同一件事時，「first working pull request is the one that lands」。
- 留言：CONTRIBUTING 的第 2 步要在 issue 留言。這是上游寫入，由人決定，代理不做。
- PR：內文寫 `Closes #NNN`；範圍只限該 issue，不重構無關程式碼；新工具函式放 `src/utils/`；TypeScript strict、named exports、不用 default export；Node built-in 用 `node:` 前綴。
- 送出前的本機序列（CONTRIBUTING 原文）：`npm ci`、`npm run lint:tests`、`npm run build`、`node scripts/typecheck-changed-tests.mjs upstream/main`、`node dist/index.js advisories sync`、`npm test`。type-check 需要指向 `OWASP/cve-lite-cli` 的 `upstream` remote。失敗的測試不會被合併。
- case study 有獨立的收件條件，不當作修復候選。
- AI 規則：根目錄沒有 `AGENTS.md`，CONTRIBUTING 沒有 AI 條款。沒有條款不代表允許代理撰寫 PR；本協調庫仍由人撰寫 PR 說明與回覆。
- 資安問題：依 `SECURITY.md`，不開公開 issue。

## CycloneDX/cyclonedx-go

- 預設分支是 `master`。儲存庫沒有自己的 `CONTRIBUTING.md` 或 `SECURITY.md`；README 指向組織層的 [CycloneDX/.github CONTRIBUTING](https://github.com/CycloneDX/.github/blob/master/CONTRIBUTING.md)。
- DCO：每個 commit 都要 `Signed-off-by`（`git commit -s`）。
- PR：預期附相關測試，CI 會在所有支援的 Go 版本上跑。能用標準函式庫做的事，不新增依賴。一個 issue 一個 bug。
- 命令（`Makefile`）：`make build`（`go build -v`）、`make test`（`go test -v -cover`）、`make lint`（`golangci-lint run`）、`make generate`。
- AI 規則：組織層 CONTRIBUTING 沒有 AI 條款。同上，不視為允許代理撰寫。

## 本次驗證

last_verified_at: 2026-11-14T11:07:34Z

| 儲存庫 | 分支 | 路徑 | blob SHA |
| --- | --- | --- | --- |
| `OWASP/cve-lite-cli` | `main` | `CONTRIBUTING.md` | `543f8b6268b6ac41eb241fbfb196f562815c6133` |
| `OWASP/cve-lite-cli` | `main` | `SECURITY.md` | `8fd1cc15ab2c2859662f4d4c804a9f60917f8c47` |
| `OWASP/cve-lite-cli` | `main` | `AGENTS.md` | 404 |
| `CycloneDX/cyclonedx-go` | `master` | `README.md` | `04c9c9b5d998b08855d4f2d850fbbc2383ec053b` |
| `CycloneDX/cyclonedx-go` | `master` | `Makefile` | `0ddb887c0594c417c26bd2670af0999000c93657` |
| `CycloneDX/cyclonedx-go` | `master` | `CONTRIBUTING.md`、`SECURITY.md` | 404 |
| `CycloneDX/.github` | `master` | `CONTRIBUTING.md` | `7d521fcfa6905c64af2d4d44b2ce0d8959a81cc7` |
