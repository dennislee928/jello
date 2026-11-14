# OpenTelemetry Collector Contrib 上游規則

這份筆記只適用 `open-telemetry/opentelemetry-collector-contrib` 的 `main`。外部 checkout 是 `/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`。本協調庫不建置 collector。

## 政策檔

`CONTRIBUTING.md` 與 `AGENTS.md`。Code Owner 要先同意範圍，才能把候選往實作推。使用者面變更用 `make chlog-new` 與 `make chlog-validate`；執行前在外部 checkout 確認 target 仍在。PR 標題用元件範圍，例如 `[processor/k8sattributes]`。

人撰寫說明與留言。AI 產出的主要 commit 用 `Assisted-by:`，不用 `Co-authored-by:`，以符合 EasyCLA。

`k8sattributesprocessor` 的 code owners 是 `@TylerHelmuth`、`@ChrsMark`、`@odubajDT`、`@jinja2`，以及 `@open-telemetry/collector-contrib-approvers`。名單以當下的 `CODEOWNERS` 為準，下面的 SHA 區塊只證明政策檔被讀過，不取代 CODEOWNERS。

## 本次驗證

last_verified_at: 2026-11-13T16:42:51Z

<!-- policy-shas:start -->
| 儲存庫 | 分支 | 路徑 | blob SHA |
| --- | --- | --- | --- |
| `open-telemetry/opentelemetry-collector-contrib` | `main` | `AGENTS.md` | `0e2335037978da4d790a87fd9c8960b6a3bda4b8` |
| `open-telemetry/opentelemetry-collector-contrib` | `main` | `CONTRIBUTING.md` | `d0ba48866c71dc9a06d0db05b4688d67d27a3e32` |
<!-- policy-shas:end -->

## 與 semantic-conventions 的界線

`open-telemetry/semantic-conventions` `#4100` 是 HPA 語意約定的合併紀錄，用來核對 collector 的 `go.mod` 是否已經參考含那些符號的 semconv 版本。convention 儲存庫不在日掃目標裡。符號沒出現在 collector 目前依賴的產生碼時，`#52509` 維持 `BLOCKED`。

## 種子

`#52509`：`processor/k8sattributes`。blocking dependency 是產生符號與 Code Owner 同意，兩者缺一就停。

`#50908`：檔案清單已讀，21 個檔集中在 HPA label / annotation 擷取，沒有 semantic-conventions 產生檔。對 `#52509` 記 `possible_overlap`，不是 `definite_duplicate`。`#52631` 是週報 issue，沒有 PR diff。交叉引用存在只代表要讀，不代表已經重複。

investigation_verified_at: 2026-11-13T16:55:05Z

processor `go.mod` 沒有 semantic-conventions require。`attributes.go` 用手寫 label helper，沒有 HPA 產生符號。`CODEOWNERS` 列了 owner，同意未出現。`#52509` 維持 `BLOCKED`。本目錄不改 semconv 產生器，也不起草 processor 補丁。

## OpenTelemetry Go 與 JS SDK

investigation_verified_at: 2026-11-14T11:07:34Z

`open-telemetry/opentelemetry-go` 與 `open-telemetry/opentelemetry-js` 在 `2026-11-14` 加入日掃。選它們的理由是外部 PR 合併率：最近 100 個 closed PR 中，外部作者（排除 bot）分別 39 / 44（中位 3.9 天）與 49 / 59（中位 0.8 天）。這是 proxy，不是保證。兩者目前沒有尚無 assignee 的 `good first issue`；`opentelemetry-go` 的 `help wanted` 只剩 2 個 2024 年的 issue。

兩個 repo 共通：

- CLA：OpenTelemetry 社群指南（`community/guides/contributor/README.md`）要求一次性簽署 CLA。簽署是人的事，代理不做。
- GenAI policy（`community/policies/genai.md`）：維護者可以自行決定隱藏或關閉全部或部分由生成式 AI 產生的 issue、PR 與留言；推動貢獻的人要為內容負責。這和本協調庫「PR 說明與回覆由人撰寫」一致，不能放鬆。
- 資安問題走私下通報，不開公開 issue 或 PR（含 draft）。

### open-telemetry/opentelemetry-go

- 讀 `AGENTS.md`、`.github/copilot-instructions.md`、`CONTRIBUTING.md`。`AGENTS.md` 要求最小改動、保留 API 相容與規格相容、依賴最少。
- 使用者可見的變更要寫 `CHANGELOG.md` 的 `## [Unreleased]`。
- 命令：用 `make test`，不直接 `go test`；送出前 `make precommit`，之後 `git status` 不應有變更。效能類 PR 要附 `go test -bench` 輸出。

### open-telemetry/opentelemetry-js

- 先讀 OpenTelemetry 社群貢獻指南。commit 建議 Conventional Commits（`.commitlintrc.yml`）。
- `CHANGELOG.md` 或 `experimental/CHANGELOG.md` 需要條目，不需要時用 `Skip Changelog` 標籤（由維護者加）。
- 命令：`npm ci`、`npm run compile`、`npm run test`。建置的 Node 版本以根目錄 `package.json` 的 `devEngines.runtime` 為準（CONTRIBUTING 寫 CI 用 Node ^26.3.0）。
- 根目錄沒有 `AGENTS.md`。

| 儲存庫 | 分支 | 路徑 | blob SHA |
| --- | --- | --- | --- |
| `open-telemetry/opentelemetry-go` | `main` | `CONTRIBUTING.md` | `6268ed06d1ae511bedb9ea2875334565bf0f0907` |
| `open-telemetry/opentelemetry-go` | `main` | `AGENTS.md` | `2cfed84fbb19c45f7cca2fa74e420b2af98e7244` |
| `open-telemetry/opentelemetry-js` | `main` | `CONTRIBUTING.md` | `8e46802cefc73fc8bb6281a4d00dabd1f7eec012` |
| `open-telemetry/opentelemetry-js` | `main` | `AGENTS.md` | 404 |
| `open-telemetry/community` | `main` | `policies/genai.md` | `78b7d2982f279e2f5e191180a6535506d913301c` |
| `open-telemetry/community` | `main` | `guides/contributor/README.md` | `60719199c3a5baac5218275571d99a786d3b557b` |

### 不收錄

`open-telemetry/opentelemetry-collector` 的 `good first issue` 在 `2026-11-14` 讀到的樣本（`#16370`）寫明保留給 KubeCon NA 2026 ContribFest，活動前開的 PR 會被關閉。`open-telemetry/opentelemetry-operator` 的 8 個 `good first issue` 都已經有 open PR（`#5847`、`#5926`–`#5932`）。兩者都不加入日掃。
