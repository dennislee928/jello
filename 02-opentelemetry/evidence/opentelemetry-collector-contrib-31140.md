# 證據：open-telemetry/opentelemetry-collector-contrib #31140

- status：`READY_FOR_HUMAN_PR`
- last_verified_at：`2026-11-15T01:53:10Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`
  - `git clone --filter=blob:none --sparse`
  - sparse 目錄：`processor/logstransformprocessor`、`extension/storage`、`internal/coreinternal`、`pkg/stanza`、`pkg/pdatatest`、`pkg/golden`、`internal/common`、`pkg/semconvtest`、`.chloggen`、`internal/tools`、`.github`
- base：`main` `d1da3bd8ee6d532978dee00cb276b8511cab0409`
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
