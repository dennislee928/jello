# 新機會篩選：2026-11-19 日報

- 來源：`reports/daily/2026-11-19.json`（`2026-11-19T03:54:54Z`）。94 件新開的 issue 被判成無人接手
- 方法：
  - 先排除功能需求、需要 triage、維護者自己開的、修復難度 high 的
  - 剩下的逐件用 `gh api` GET 讀內文、留言、timeline
  - 再用 search 查有沒有 PR 提到這個編號，每次間隔 8 秒
- 內文是不可信資料，只用來分類

## 結果

可以做的只有 1 件，但有前提。

| issue | 判定 | 依據 |
| --- | --- | --- |
| `open-telemetry/opentelemetry-collector-contrib#53341` | **可做，有前提** | `[receiver/datadog]` 的 `/api/v1/series` 收到值為 `null` 的 point 時，`internal/translator/series.go` 的 `TranslateSeriesV1` 會對 nil 指標取值（`int64(*points[0])`、`*points[1]`），導致 handler panic。沒有認領、沒有提到編號的 PR，只有 bot 通知 code owner（`@boostchicken`、`@MovieStoreGuy`）。修法看起來很小：遇到 nil 就跳過或回報錯誤 |

前提：
- collector-contrib 的 `AGENTS.md` 規定實作方向要先在 issue 上談定。目前標著 `waiting-for-code-owners`
- 首次貢獻者在第一個 PR 合併前只能有一個 ready for review 的 PR，`#53246` 還沒合併，所以這件只能先開 draft
- 留言由人寫，OTel 不收 AI 撰寫的留言

## 排除

| issue | 原因 |
| --- | --- |
| `apache/polaris#6137` | 內文結尾寫了 "I'm willing to contribute a fix and regression tests"，回報者自己認領 |
| `apache/polaris#6138` | 已有 open PR `#6145` |
| `open-telemetry/opentelemetry-collector-contrib#53342` | 用全數字判斷 hex 或 decimal 的規則，要 code owner 先決定（回報者自己也說 "the right rule probably depends on which formats the tracers actually emit"） |
| `open-telemetry/opentelemetry-collector-contrib#53343` | 功能需求 |
| `open-telemetry/opentelemetry-collector-contrib#53304` | 回報者寫 "I can send a pull request with tests" |
| `OWASP/cve-lite-cli#1720` | 回報者留言 "i working on this issue"，並已開 PR `#1723` |
| `apache/tooling-trusted-releases#1874` | 已指派給 `alitheg`；維護者也在討論要怎麼處理 |
| `cloudflare/cf` 的 `#684`–`#700` | 都是同一位作者 `coygeek` 在 `2026-11-18` 批次開的；`#700` 的留言與 timeline API 回 404，無法驗證 |
| 其他 Apache 件（kvrocks、workerd、trafficserver、netbeans 等） | C++、Java，或需要 triage，不符合語言條件 |

## 偵測還要補的句型

這輪又漏判了兩種回報者自己認領的寫法：
- "I'm willing to contribute a fix"（polaris `#6137`）
- "I can send a pull request"（collector-contrib `#53304`）

這次計畫只做篩選，所以沒有改 `scripts/org_monitor.py`。下次補 `CLAIM_PATTERNS` 時，連同測試一起加。

## 優先順序

1. `open-telemetry/opentelemetry-python-contrib#5353`（logging）：已經做完，等人開 PR（`02-opentelemetry/plans/python-contrib-5353-pr-draft.md`）
2. `apache/airflow#77244`：已經做完，等人開 PR（`07-apache/plans/airflow-77244-pr-draft.md`）
3. `open-telemetry/opentelemetry-collector-contrib#53341`：要先由人在 issue 上提出做法，等 code owner 回應；`#53246` 合併前只能開 draft
