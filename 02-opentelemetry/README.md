# OpenTelemetry

這個目錄協調 `open-telemetry/opentelemetry-collector-contrib`（分支 `main`）。外部 checkout 是 `/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`。

`open-telemetry/semantic-conventions` 的 `#4100` 只當語意約定的上游引用，不是日掃的第九個儲存庫，也不把 convention 原始碼 vendor 進來。

`#52509` 在產生出來的 HPA 符號與 Code Owner 範圍都確認之前維持 `BLOCKED`。`#50908` 要等讀過 diff 之後才標 `possible_overlap` 或 `definite_duplicate`，不預設成重複。
