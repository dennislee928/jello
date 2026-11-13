# OpenTelemetry Collector Contrib 上游規則

這份筆記只適用 `open-telemetry/opentelemetry-collector-contrib` 的 `main`。外部 checkout 是 `/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`。本協調庫不建置 collector。

## 政策檔

`CONTRIBUTING.md` 與 `AGENTS.md`。Code Owner 要先同意範圍，才能把候選往實作推。使用者面變更用 `make chlog-new` 與 `make chlog-validate`；執行前在外部 checkout 確認 target 仍在。PR 標題用元件範圍，例如 `[processor/k8sattributes]`。

人撰寫說明與留言。AI 產出的主要 commit 用 `Assisted-by:`，不用 `Co-authored-by:`，以符合 EasyCLA。

`k8sattributesprocessor` 的 code owners 是 `@TylerHelmuth`、`@ChrsMark`、`@odubajDT`、`@jinja2`，以及 `@open-telemetry/collector-contrib-approvers`。名單以當下的 `CODEOWNERS` 為準，下面的 SHA 區塊只證明政策檔被讀過，不取代 CODEOWNERS。

## 本次驗證

last_verified_at: null

<!-- policy-shas:start -->
尚未以 `gh api` 重抓政策檔 blob SHA。
<!-- policy-shas:end -->

## 與 semantic-conventions 的界線

`open-telemetry/semantic-conventions` `#4100` 是 HPA 語意約定的合併紀錄，用來核對 collector 的 `go.mod` 是否已經參考含那些符號的 semconv 版本。convention 儲存庫不在八個日掃目標裡。符號沒出現在 collector 目前依賴的產生碼時，`#52509` 維持 `BLOCKED`。

## 種子

`#52509`：`processor/k8sattributes`。blocking dependency 是產生符號與 Code Owner 同意，兩者缺一就停。

`#50908`：仍需讀 diff 與檔案清單後才判斷和 `#52509` 是 `possible_overlap` 還是 `definite_duplicate`。另讀 `#52631` 的檔案清單。交叉引用存在只代表要讀，不代表已經重複。

本目錄不改 semconv 產生器，也不在符號未確認時起草 processor 補丁。
