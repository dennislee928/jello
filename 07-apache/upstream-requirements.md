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

## apache/airflow

`2026-11-18` 讀過 `main`（`c03582f661`）。

| 路徑 | blob SHA |
| --- | --- |
| `AGENTS.md` | `4d63c2a38c5c1d22ca92591230b6d3ceb126b1c2` |
| `contributing-docs/05_pull_requests.rst` | `5c48d35ba9d3b7883a8ebbd9260b0f4d321a863d` |

- Gen-AI（`05_pull_requests.rst` 的 "Gen-AI Assisted contributions"）：
  - 可以使用 Gen-AI，但要遵守 ASF Generative Tooling 指引
  - PR 描述要聲明使用了 Gen-AI
  - 作者要讀懂並能解釋每一行，本機跑過相關靜態檢查與測試
  - 不能夾帶無關變更；違規的話，維護者可能關掉該貢獻者所有的 PR
- `AGENTS.md`：
  - 動手前先查有沒有 PR
  - 只推到自己的 fork
  - **不得把 agent 列為 commit co-author**
  - 保留 Gen-AI 揭露
  - 草稿不代表可以張貼
- 測試：
  - 不在主機直接跑 pytest，例外是 `uv run --project <PROJECT> pytest path/to/test.py -xvs`
  - 缺系統依賴時改用 `breeze run pytest ...`
- Lint：`prek run ruff --from-ref <target_branch>`
- Newsfragment：`providers/` 一律不加；要給使用者看的說明，直接改 `providers/<provider>/docs/changelog.rst`，一般 bug 修正不用加
- 新開 issue 時，`boring-cyborg[bot]` 會回覆 "If you are willing to raise PR to address this issue please do so, no need to wait for approval"
