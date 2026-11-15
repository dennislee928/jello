DRAFT

給人用的交付檔。代理與 workflow 都不得張貼、推送或開 PR。

上游 `AGENTS.md`（`opentelemetry-collector-contrib`，`d1da3bd8`）規定：

- PR 描述不能由 AI 撰寫，每一節都要由人寫，原樣使用。
- AI 不能替人勾 `I, a human, wrote this pull request description myself`。
- 不能在 issue 或 PR 貼 AI 產生的留言。

所以下面的 PR 模板各節**刻意留空**。事實整理在後面的「參考事實」一節，供人自己寫描述時參考，不是 PR 文字。

## 位置

- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`
- 本機分支：`fix-logstransform-start-context-31140`，base 是 `d1da3bd8ee6d532978dee00cb276b8511cab0409`
- 改動**尚未 commit**：
  - `processor/logstransformprocessor/processor.go`
  - `processor/logstransformprocessor/processor_test.go`
  - `.chloggen/31140-logstransform-converter-context.yaml`（新檔）

## 建議的 PR 標題（人可改）

```
[processor/logstransform] Keep converting logs after the Start context is cancelled
```

## PR 模板（上游原文，各節由人填寫）

```markdown
<!--Ex. Fixing a bug - Describe the bug and how this fixes the issue.
Ex. Adding a feature - Explain what this achieves.-->
#### Description

<!-- Issue number (e.g. #1234) or full URL to issue, if applicable. -->
#### Link to tracking issue
Fixes

<!--Describe what testing was performed and which tests were added.-->
#### Testing

<!--Describe the documentation added.-->
#### Documentation

<!--Authorship attestation. See AGENTS.md for details. AI agents must not check this box on behalf
of the user; the human author must check it themselves before the PR is ready for review.-->
#### Authorship

- [ ] I, a human, wrote this pull request description myself.
```

## 參考事實（不是 PR 文字）

- issue：[#31140](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/31140)，由 `BinaryFissionGames` 在 2024-02-08 建立，標 `bug`、`processor/logstransform`、`never stale`。沒有 assignee。
- 問題：`Start(ctx)` 把 ctx 傳給 `startConverterLoop`，`converterLoop` 在 `<-ctx.Done()` 時 return。collector `component.Component` 的文件說，長期執行的工作不要用傳給 `Start` 的 context。這個 context 一被取消，logs 就不再往下傳，也沒有錯誤訊息。
- 修法：
  - loop 改用 `context.WithCancel(context.Background())`。
  - `sync.WaitGroup` 是區域變數，用 `wg.Go`。
  - shutdown 先 `wg.Wait()` 再 `cancel()`。`FromPdataConverter.Stop()` 會關閉 `entriesChan`，loop 會 drain 完再 return，所以 shutdown 時不丟資料。
  - `Start` 的 ctx 參數改成 `_`。
- 回歸測試：`TestProcessorKeepsConvertingAfterStartContextIsCancelled`。Start 之後取消 context，送一筆 log，斷言 sink 收到。
- 先前的 PR，都由 stale bot 關閉，都不是被否決：
  - [#47841](https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/47841)（`SAY-5`）：`atoulme` 要求程式更簡單、用 `wg.Go`，changelog 寫出使用者價值。
  - [#50150](https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/50150)（`darkknight8670`）：code owner `dehaansa` 問為什麼把 WaitGroup 放進 struct。
- 這版怎麼回應那些 review：
  - WaitGroup 留在區域變數，並用 `wg.Go`。
  - changelog 的 note 寫使用者看得到的效果，`subtext` 留空（上游 AGENTS.md 要求簡短）。
  - Copilot 在 #50150 建議「先 cancel 再 wait」，這裡**不採用**。理由是那會讓 loop 在 drain 之前就走 `ctx.Done()` 分支離開，關機時可能丟掉還在 channel 裡的 log。
  - Copilot 說 `wg.Go` 無法編譯也不正確：模組是 `go 1.26.0`，本機 `go1.27.1` 編譯並測試通過。
- 實際跑過的命令與結果：`evidence/opentelemetry-collector-contrib-31140.md`。

## 建議的 commit message（人可改寫）

上游要求用 `Assisted-by:` 揭露 AI 協助，**不要**用 `Co-authored-by:`，否則 EasyCLA 檢查會失敗。

```
[processor/logstransform] Keep converting logs after the Start context is cancelled

Assisted-by: Claude Opus 5.5
```

## 開 PR 前（只有人能做）

1. 簽 OpenTelemetry CLA（EasyCLA）。commit 的 email 要和簽 CLA 的帳號一致。
2. 上游 AGENTS.md 要求實作方向先在 issue 上和維護者對齊。兩個舊 PR 都已有維護者 review，方向沒有被否決；要不要先在 #31140 留言，由人決定，代理不能代為留言。
3. 讀過 diff，自己寫 commit message 和 PR 描述各節，自己勾 Authorship。
4. 在描述裡致謝 #47841 與 #50150 的作者。這是人的選擇，代理只提供連結。
5. fork、推送分支、開 PR 都由人操作。
6. 開了 PR 之後，把網址寫回 `02-opentelemetry/candidates.json`，狀態改 `PR_OPEN`。
