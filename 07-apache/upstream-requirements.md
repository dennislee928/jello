# Apache 上游規則（Superset 以外）

`01-apache-superset/` 只放 Superset。其他 Apache repo 的規則放在這裡，每個 repo 各自驗證。外部 checkout 放在 `/Users/dennis/Desktop/upstream-src/apache/<repo>`。

## apache/iceberg-go

`2026-11-18` 讀過 `main`（`3d1d676`）。

| 路徑 | blob SHA |
| --- | --- |
| `AGENTS.md` | `66e21ea1ac8e450559426d58f6d05003a772d364` |
| `CONTRIBUTING.md` | `43c795246b1dcbe24d6136c51478a02faeca1895` |

- 認領（`CONTRIBUTING.md` 的 "Picking Up Issues"）：
  1. 先查有沒有 open PR
  2. 在 issue 留言認領，**等維護者回應後才開始寫程式**
  3. 還沒有 PR 被合併過的新貢獻者，**一次只做一件**
  4. 同一件 issue 有兩個 PR 時，通常保留先認領的那個
- PR：
  - 內文寫 `Fixes #N`，一件 issue 一個 PR
  - 推送前跑 `make test` 與 `make lint`（`make lint-install` 可安裝 linter）
  - 每個 commit 都要 `Signed-off-by`（DCO）
  - CI 用 `apidiff` 比對對外 API；刻意的不相容變更，標題要加 `!`
  - 回應 review 時推新 commit，不要 force-push
- AI 規則：`AGENTS.md` 只講安全模型（`SECURITY-THREAT-MODEL.md`），沒有 AI 撰寫條款。照本庫規則，留言與 PR 描述由人寫
- 留言與 PR 描述只能由人張貼（本庫 `AGENTS.md`）
