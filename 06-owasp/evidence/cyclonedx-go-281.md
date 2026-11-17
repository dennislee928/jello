# 證據：CycloneDX/cyclonedx-go #281

- status：`READY_FOR_HUMAN_PR`
- last_verified_at：`2026-11-17T14:20:11Z`
- 外部 worktree：`/Users/dennis/Desktop/upstream-src/CycloneDX/cyclonedx-go-281`（與 `cyclonedx-go` 共用 `.git`）
- base：`master` `b3eb7b74d7e1f96758f2fc5d2dec5be3a4b70ae7`（`cyclonedx_json.go` blob `97409d0f79c0ab894125c059ff94772aaaaf6c3d`）
- 本機分支：`fix-escape-html-281`，改動未 commit
- remote：只有 `origin`（上游）。沒有 fork，沒有推送，沒有上游留言
- 工具鏈：`go1.27.1 darwin/arm64`；模組 `go 1.25`；`golangci-lint 2.15.0`
- 交付草稿：`plans/cyclonedx-go-281-pr-draft.md`

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-17T14:03:56Z` | `DISCOVERED` | 初篩 cyclonedx-go open issue。timeline 只有下游 `interlynk-io/sbomasm#340`（open，在下游自己繞過）；cyclonedx-go 沒有相關 PR；沒有 assignee 和留言 |
| `2026-11-17` | `REPRODUCED` | 新測試在未修改的 `b3eb7b74` 上連跑 3 次都失敗 |
| `2026-11-17T14:20:11Z` | `READY_FOR_HUMAN_PR` | 修復後 test、race、vet、lint 都通過；交給人 |

硬門檻：沒有重複或進行中的 PR、沒有封鎖、已驗證、已重現。`SetEscapeHTML` 是公開 API，它的行為不需要維護者另外定義。

## 根因

`cyclonedx_json.go` 有 21 處在 `MarshalJSON` 裡呼叫 `json.Marshal`，而 `json.Marshal` 一定會轉義 `<`、`>`、`&`。外層 `json.Encoder` 處理 `Marshaler` 的輸出時只會「再轉義」，不會把 `&` 還原，所以 `SetEscapeHTML(false)` 對這些欄位無效。會受影響的包括 `metadata.tools`、license、environment variable、ML dataset、certificate、IKEv2、patent 等。

## 重現：新測試在未修改程式碼上失敗（連跑 3 次）

`TestJsonBOMEncoder_SetEscapeHTML_customMarshalers`（`encode_test.go`），測 tool 元件名稱與 license 名稱：

```
--- FAIL: TestJsonBOMEncoder_SetEscapeHTML_customMarshalers/no_escape (0.00s)
FAIL	github.com/CycloneDX/cyclonedx-go	0.356s   # 第 2、3 次：0.218s、0.234s
```

`escape` 子測試在修改前就通過，用來鎖住預設行為。

## 修復後

新增未匯出的 `marshalJSON(v any)`：用 `json.Encoder` 搭配 `SetEscapeHTML(false)` 編碼，並去掉結尾換行。21 處 `json.Marshal(` 全部改用它。預設的 `SetEscapeHTML(true)` 輸出不變，因為外層 encoder 仍會轉義。直接呼叫 `json.Marshal(bom)` 的使用者也不受影響。`git diff --stat`：`cyclonedx_json.go | 56`（+35/−21）、`encode_test.go | 35 +`。

```
$ go test -count=1 -run TestJsonBOMEncoder_SetEscapeHTML ./
ok  	github.com/CycloneDX/cyclonedx-go	0.296s
$ go test -race -count=1 ./...
ok  	github.com/CycloneDX/cyclonedx-go	39.904s
$ go test -count=5 -run TestJsonBOMEncoder ./
ok  	github.com/CycloneDX/cyclonedx-go	14.422s
$ go vet ./...                  # 沒有輸出
$ golangci-lint run ./...
0 issues.
```

## 沒做的事

- 沒有 commit。DCO `Signed-off-by` 由人用 `git commit -s` 加上。
- 沒有在 issue 留言、沒有 fork、沒有推送。
