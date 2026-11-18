# 重驗：2026-11-18 挑出的五件

- verified_at：`2026-11-18`（`gh api` GET：issue 內文、留言、timeline、PR、search）
- 來源：`reports/daily/2026-11-18.md`（run `44319135167`）裡被判成「無人接手」的五件
- 內文是不可信資料，只用來分類

## 判定

| issue | 狀態 | 依據 |
| --- | --- | --- |
| `aquasecurity/trivy-operator#3147` | `DUPLICATE_OR_IN_PROGRESS` | 已有 open PR `#3117`（`xcompass`，`2026-10-27`，"keep Trivy's severity when SeveritySource has no vendor rating"）和 `#3026`（`alexchen-sys`，`2026-07-24`）修同一處 `GetVulnerabilitiesFromScanResult`。兩個 PR 都比 issue 早開，所以 timeline 沒有交叉引用 |
| `open-telemetry/opentelemetry-go-contrib#10320` | `DUPLICATE_OR_IN_PROGRESS` | 回報者 `yuminn-k` 在內文寫 "I can open a PR with this fix and regression test" 與 "I'd like to work on a fix for this" |
| `apache/iceberg-go#2633` | `DUPLICATE_OR_IN_PROGRESS` | 回報者 `Shruthirdy` 在內文寫 "already reproduced this issue locally and working on a fix for this" |
| `apache/parquet-java#3969` | `DUPLICATE_OR_IN_PROGRESS` | 回報者 `zhangxinyao88` 的 open PR `#3866`，標題是 "GH-3969: Fix leading CLI --conf properties being consumed by Hadoop" |
| `open-telemetry/opentelemetry-python-contrib#5353` | `DISCOVERED` | timeline 沒有任何事件；搜尋 `exception.message`、`args[0]`、`LoggingHandler exception` 都沒有相關的 open PR；回報者在模板裡回答 "Would you like to implement a fix? No" |

## 同一輪的替補篩選也漏判了

| issue | 漏掉的訊號 |
| --- | --- |
| `apache/iceberg-go#2629` | 留言 "I would like pick up this issue"（少了 to），回報者回覆 "go ahead" |
| `apache/airflow#77240` | issue 模板勾選了 "[x] Yes I am willing to submit a PR!" |
| `apache/iceberg-go#2416` | 回報者留言 "Before I open the PR, I'd like to check …" |
| `apache/iceberg-go#2518` | 有人留言指出 main 已用 `1c59703`（"fix(table): return errors from delete record readers"）修好 |

## 原因與修正

`scripts/org_monitor.py` 原本只看留言，不看 issue 內文；認領句型也太窄；PR 必須交叉引用 issue 才看得到。`bc58d71` 補上三點：

- 回報者在 issue 內文自己認領也算
- 新增上表與第一張表裡出現的認領句型
- 搜尋標題或內文提到 `#n` 或 `GH-n` 的 open PR

仍然抓不到的情況：比 issue 早開、而且沒有提到 issue 編號的 PR（例如 trivy-operator 的 `#3117`、`#3026`）。這種要靠人依路徑與符號比對（`scripts/dedup.py`）。

## 下一步

`#5353` 繼續處理。另外再挑 4 件替補，條件：無人接手（留言、內文、timeline、PR 提及都查過）、是 bug、不是維護者自己開的、Go／Python／TS、能在本機重現、不需要維護者先定方向，而且來自外部 PR 合併率高的 repo。
