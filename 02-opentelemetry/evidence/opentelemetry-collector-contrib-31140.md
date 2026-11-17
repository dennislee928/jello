# 證據：open-telemetry/opentelemetry-collector-contrib #31140

- status：`PR_OPEN`（[#53246](https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/53246)）
- last_verified_at：`2026-11-17T15:37:27Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`
  - `git clone --filter=blob:none --sparse`
  - sparse 目錄：`processor/logstransformprocessor`、`extension/storage`、`internal/coreinternal`、`pkg/stanza`、`pkg/pdatatest`、`pkg/golden`、`internal/common`、`pkg/semconvtest`、`.chloggen`、`internal/tools`、`.github`
- base：`main` `71ed4c2993`（`2026-11-17` rebase；原本是 `d1da3bd8ee6d532978dee00cb276b8511cab0409`）
- 本機分支：`fix-logstransform-start-context-31140`，改動未 commit
- remote：只有 `origin`（上游）。沒有 fork，沒有推送，沒有上游留言
- 工具鏈：`go1.27.1 darwin/arm64`；模組 `go 1.26.0`
- 交付草稿：`plans/31140-pr-draft.md`

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-14T11:30Z` 左右 | `DISCOVERED` | bug 掃描；timeline 只交叉引用 closed-unmerged 的 `#47841`、`#50150`；搜尋沒有 open、draft 或 merged 的重疊 |
| `2026-11-15` | `REPRODUCED` | 回歸測試在未修改的 `d1da3bd8` 上連跑 3 次都失敗 |
| `2026-11-15T01:53:10Z` | `READY_FOR_HUMAN_PR` | 修復後測試、race、vet、lint、chlog-validate 都通過；交給人 |
| `2026-11-17T14:20:11Z` | `READY_FOR_HUMAN_PR`（重驗） | rebase 到 `71ed4c2993` 後重新重現、重跑全部檢查，都通過；見「2026-11-17 重新驗證」 |
| `2026-11-17T15:32:22Z` | `PR_OPEN` | 人開了 #53246（head `fa8b316c81`，base `main`），已自動請 `dehaansa` review。EasyCLA 為 failure（尚未簽）。歡迎 bot 提醒：首次貢獻者在第一個 PR 合併前，最多只能有一個 ready for review 的 PR |
| `2026-11-17T15:37:27Z` | `PR_OPEN` | 人從 GitHub 把 main 合進分支（merge commit `99afabc622`）。EasyCLA 轉為 success。`fa8b316c81` 的 CI workflow 都是 `action_required`，因為首次貢獻者要等維護者核准才會跑；Copilot review 因配額不足沒跑 |

## 未修改程式碼上的基線

`processor.go` 的 blob 是 `be7d9d2d49536e2e0245b423d03d3d5172955123`，和規劃時讀到的 `main` `e0e1cb64` 相同。

```
$ go test -count=1 ./...            # 在 processor/logstransformprocessor
ok  	.../processor/logstransformprocessor	0.902s
```

## 重現：新測試在未修改程式碼上失敗（連跑 3 次）

```
$ go test -count=1 -run 'TestProcessorKeepsConvertingAfterStartContextIsCancelled' ./
--- FAIL: TestProcessorKeepsConvertingAfterStartContextIsCancelled (2.10s)
        	Error:      	Condition never satisfied
FAIL	.../processor/logstransformprocessor	2.373s   # 第 2、3 次：2.346s、2.360s
```

## 修復後

```
$ go test -count=1 -run 'TestProcessorKeepsConvertingAfterStartContextIsCancelled' ./   # 3 次
ok  ... 0.619s / 0.456s / 0.449s
$ go test -race -count=1 ./...
ok  ... 2.056s
$ go test -race -count=20 ./
ok  ... 10.555s
$ go vet ./...                       # 沒有輸出，exit 0
$ gofmt -l .                         # 沒有輸出
$ make test                          # 在 component 目錄
DONE 12 tests, 1 skipped in 2.046s   # 跳過的是既有的 TestLogsTransformProcessor（上游 issue #9761），不是這次改的
$ make lint                          # exit 0；license check、misspell、golangci-lint 都沒有 issue
$ make chlog-validate                # 在 repo 根目錄
PASS: all files in .../.chloggen/ are valid
$ git diff --check                   # 沒有輸出
```

`TestProcessorShutdownWithSlowOperator`（關機 drain）在 `-race -count=20` 下仍然通過。

第一次跑 `make test` 時 `internal/tools` 不在 sparse 裡，結果是 `go: open .../internal/tools/go.mod: no such file or directory`，那次不算。補上目錄後才有上面的結果。

沒有跑的：整個 repo 的 `make` 目標，以及 integration、E2E 測試。

## 改動

`processor.go` +12 / −9，`processor_test.go` +27，新增 `.chloggen/31140-logstransform-converter-context.yaml`（`bug_fix`，`processor/logstransform`，`issues: [31140]`，`subtext` 留空）。

## 分數

- acceptance 4：code owner 兩度參與 review，範圍小，可測。
- impact 2：issue 本身寫「doesn't seem to actually lead to any negative effects」。collector 實務上很少取消 Start 的 context，這是合約與健壯性的修正，不主張使用量或影響人數。

## 2026-11-17 重新驗證

### 有效性（`gh api` GET）

- `#31140` 仍是 open，最後更新於 `2024-04-16T13:40:28Z`。timeline 的交叉引用只有 `#31192`、`#47841`、`#50150`，三個都已關閉。沒有新的 PR。
- 用關鍵字 `logstransform` 搜尋 open PR：0 筆。
- 從 `d1da3bd8` 到現在，上游只有 `4cfe6068`（`2026-11-17`）動到這個元件，而且只改了 `go.sum`。
- 上游 `AGENTS.md`（`0e233503`）、`CONTRIBUTING.md`（`d0ba4886`）、`.github/pull_request_template.md`（`62ce8f66`）的 blob 和 `d1da3bd8` 時一樣。
- `metadata.yaml`：stability 是 `development: [logs]`，`distributions: []`，code owner 是 `dehaansa`。這個元件沒有進任何官方發行版，所以影響面小，impact 維持 2。

### rebase 與重跑

改動先備份到 scratchpad，再 `git fetch origin main` 和 `git rebase --autostash origin/main`。rebase 後的 `git diff` 和備份一樣（只差 index 行）。

```
# 只 stash processor.go（保留新測試），連跑 3 次
--- FAIL: TestProcessorKeepsConvertingAfterStartContextIsCancelled (2.10s)
        Error:      Condition never satisfied          # 2.366s / 2.370s / 2.380s
# 還原修復後
$ go test -race -count=1 ./...         ok  1.706s
$ go test -race -count=20 ./           ok  10.140s
$ go vet ./...                         exit 0
$ make test                            DONE 12 tests, 1 skipped
$ make lint                            exit 0
$ make chlog-validate                  PASS（repo 根目錄）
```

### PR 條件

| 條件 | 狀態 |
| --- | --- |
| 回歸測試修復前失敗、修復後通過；race、vet、lint | 滿足（`71ed4c2993`） |
| `.chloggen` 條目且 `chlog-validate` 通過 | 滿足 |
| 和上游 main 沒有衝突 | 滿足 |
| EasyCLA；commit 用 `Assisted-by:`，不用 `Co-authored-by:` | 未完成，只有人能做 |
| PR 描述各節由人寫，Authorship 由人勾 | 未完成，只有人能做 |
| 上游 `AGENTS.md`：實作方向要先在 issue 上和維護者對齊 | **未滿足**。`#47841`、`#50150` 有 review 而且方向沒被否決，但 `#31140` 本身沒有維護者確認方向。要不要先在 issue 留言，由人決定，代理不能代留 |

所以技術上可以送出了，流程上還差三件只有人能做的事。
