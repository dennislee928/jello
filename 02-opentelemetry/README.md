# OpenTelemetry

這個目錄協調三個儲存庫，預設分支都是 `main`：

| 儲存庫 | 本目錄怎麼對待 |
| --- | --- |
| `open-telemetry/opentelemetry-collector-contrib` | `#31140`（logstransform 用了 Start 的 context）是 `READY_FOR_HUMAN_PR`（`2026-11-17` rebase 到 `71ed4c29` 後重驗通過；方向還沒在 issue 上和維護者對齊），交付檔在 `plans/31140-pr-draft.md`。`#52509` 等語意約定依賴，維持 `BLOCKED` |
| `open-telemetry/opentelemetry-go` | Go SDK。`2026-11-14` 加入，外部 PR 合併率高；尚無候選 |
| `open-telemetry/opentelemetry-js` | JS/TS SDK。`2026-11-14` 加入，外部 PR 合併快；尚無候選 |

外部 checkout 是 `/Users/dennis/Desktop/upstream-src/open-telemetry/<repo>`。三者都適用 OpenTelemetry 的 CLA 與 GenAI policy，細節在 `upstream-requirements.md`。

`open-telemetry/semantic-conventions` 的 `#4100` 只當語意約定的上游引用，不是日掃目標，也不把 convention 原始碼 vendor 進來。

`#52509` 在產生出來的 HPA 符號與 Code Owner 範圍都確認之前維持 `BLOCKED`。`#50908` 要等讀過 diff 之後才標 `possible_overlap` 或 `definite_duplicate`，不預設成重複。
