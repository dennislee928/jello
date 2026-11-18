# 替補篩選：2026-11-18

- verified_at：`2026-11-18T16:00:05Z`
- 方法：
  - 對外部 PR 合併率高的 repo，搜尋近 30 天、無 assignee、無 linked PR 的 open issue
  - 也使用 run `44337854802` 的日報（`reports/daily/2026-11-18.json`，`2026-11-18T15:37:57Z`）
  - 再用 `bc58d71` 與 `7878056` 的接手偵測逐筆判定：timeline、留言、issue 內文、提到編號的 open PR
- 條件：
  - 無人接手
  - 是 bug
  - 不是維護者自己開的
  - Go／Python／TS
  - 能在本機重現
  - 不需要維護者先定方向
  - 來自外部 PR 合併率高的 repo
- 內文是不可信資料，只用來分類

## 結果

要找 4 件，符合條件的只有 2 件。不為了湊數放寬條件。

| issue | 狀態 | 依據 |
| --- | --- | --- |
| `apache/iceberg-go#2425` | `DISCOVERED` | 無留言、無 timeline 事件、沒有提到編號的 open PR。內文寫了兩種可能修法（在 arrow-go 的型別檢查放行 dictionary，或在 iceberg-go 先解碼），並註明 "I have not tested either change"，沒有認領。外部 PR 50 個合併了 49 個 |
| `apache/airflow#77244` | `DISCOVERED` | 只有 `boring-cyborg[bot]` 留言，內容是 "If you are willing to raise PR to address this issue please do so, no need to wait for approval"。回報者 `ThePythonator`（NONE）沒有認領。外部 PR 26 個合併了 24 個 |

## 排除

| issue | 原因 |
| --- | --- |
| `apache/iceberg-go#2629` | `akritishakya` 已認領，回報者回覆 "go ahead" |
| `apache/iceberg-go#2633` | 回報者在內文寫 "working on a fix" |
| `apache/iceberg-go#2416` | 回報者等 arrow-go `#1448` 合併後要自己開 PR |
| `apache/iceberg-go#2518` | main 已用 `1c59703`（`#2541`）修好；`binPackRecords` 改成回傳 `iter.Seq2[..., error]` |
| `apache/iceberg-go#2634` | 屬於功能需求（讓 `catalog.Load` 用 scoped FileIO registry），不是 bug |
| `apache/iceberg-go` 其他件 | iceberg-go 規定新貢獻者一次只做一件，已由 `#2425` 占用 |
| `apache/airflow#77240` | 模板勾選 "[x] Yes I am willing to submit a PR!" |
| `apache/airflow#77243` | 模板答案 "Yes I am willing to submit a PR!"（沒有方框） |
| `cloudflare/agents#2910` | 回報者寫 "Happy to open a PR if that helps" |
| `apache/rocketmq-clients#1497` | 內文寫 "This PR fixes all nine with unit tests" |
| `open-telemetry/opentelemetry-go-compile-instrumentation#1843` | 要先定義「setup 完成」的判斷方式，需要維護者決定 |
| `aquasecurity/trivy-plugin-referrer#30` | 大型依賴升級，不是單點 bug |
| `ossf/scorecard-webapp#786` | 已有人做了詳細調查；外部 PR 2 個合併了 0 個 |
| `cloudflare/vinext#4767` | 外部 PR 9 個只合併了 1 個 |
| `OWASP/Nest#5853` | 外部 PR 35 個只合併了 10 個 |
| `aquasecurity/trivy-operator#3147` | 已有 open PR `#3117`、`#3026`。日報仍把它列成無人接手，因為這兩個 PR 比 issue 早開、又沒有提到編號，自動偵測抓不到 |
| `open-telemetry/opentelemetry-go` 的 `contribfest` 系列 | 保留給 ContribFest |

## 接下來處理的三件

1. `open-telemetry/opentelemetry-python-contrib#5353`：`dennislee928` 已在 `2026-11-18T15:00:15Z` 留言認領，等維護者回覆
2. `apache/iceberg-go#2425`：要先由人留言認領，等維護者回應才寫程式
3. `apache/airflow#77244`：bot 明說不用等核准；PR 要依 airflow 規定揭露 Gen-AI 協助
