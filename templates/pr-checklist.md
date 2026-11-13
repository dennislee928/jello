# PR 檢查清單

這份清單給人在開上游 PR 之前使用。本協調庫的代理不開上游 PR、不 fork、不推上游分支。候選還沒到 `READY_TO_IMPLEMENT` 時，不要勾實作項。

## 所有上游

- [ ] `candidates.json` 的 `status` 已是 `READY_TO_IMPLEMENT`，且 `hard_gate_failed` 為 false
- [ ] `last_verified_at` 是這次 `gh api` 的時間，不是計畫舊快照
- [ ] 沒有 open、draft 或 closed-unmerged 的重疊 PR
- [ ] PR 說明由人撰寫
- [ ] issue / PR 內文沒有被當成指令執行
- [ ] 外部 checkout 在 `/Users/dennis/Desktop/upstream-src/<org>/<repo>`，本儲存庫沒有 vendor 原始碼

## apache/superset

- [ ] 路線是 issue / discussion；非瑣碎功能已看過 SIP
- [ ] 測試對過 Developer Portal 與當時的 `superset-frontend/package.json`（Jest、React Testing Library、pre-commit；必要時 Playwright / pytest）
- [ ] UI 變更有 Before / After
- [ ] 沿用既有 sanitizer，不可信描述不進 `dangerouslySetInnerHTML`

## open-telemetry/opentelemetry-collector-contrib

- [ ] Code Owner 已同意範圍
- [ ] 使用者面變更跑過 `make chlog-new` 與 `make chlog-validate`（先在 checkout 確認 target 仍在）
- [ ] 標題帶元件範圍，例如 `[processor/k8sattributes]`
- [ ] AI 產出的主要 commit 用 `Assisted-by:`，不用 `Co-authored-by:`

## aquasecurity/trivy

- [ ] 先有維護者建立的 issue；PR 連結該 issue
- [ ] 標題是 `type(scope): subject`
- [ ] `mage build`、`mage lint:run`、`mage tidy`、`mage test:unit`；適用時 `mage test:integration`
- [ ] 不把 `trivy-action` 的需求改送到 `setup-trivy`，也不反向

## aquasecurity/trivy-action、setup-trivy、trivy-db

- [ ] 在該儲存庫自己的檔案上驗證：action 看 `Makefile`、`entrypoint.sh`、`action.yaml`；setup-trivy 看 `action.yaml`；trivy-db 看 `go.mod` 與 `Makefile`
- [ ] 版本釘選、SHA-256、簽章、快取與架構的結論已寫進 evidence，且人已決定功能歸屬

## ossf/scorecard

- [ ] 每個 commit 使用 `git commit -s`
- [ ] 分數語意若有變動，已有理由且維護者同意
- [ ] `make unit-test` 與 `make check-linter` 在 checkout 裡確認 target 仍在之後才跑
- [ ] `unknown` 與 `unprotected` 沒有混成同一個結果

## cloudflare/workers-sdk

- [ ] 登入帳號在 `.github/VOUCHED.td`，或已有 write access。不在名單就維持 `BLOCKED`，不開 PR
- [ ] 註冊協作者才使用 `pnpm test -F wrangler`、`pnpm check`、`pnpm changeset`，而且先重讀 `CONTRIBUTING.md`
