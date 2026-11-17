# 證據：CycloneDX/cyclonedx-go #291

- status：`READY_FOR_HUMAN_PR`
- last_verified_at：`2026-11-17T14:20:11Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/CycloneDX/cyclonedx-go`（`git clone --filter=blob:none`）
- base：`master` `b3eb7b74d7e1f96758f2fc5d2dec5be3a4b70ae7`（`convert.go` blob `b63adb21721f86d03aab8a18198b03f440309dc8`）
- 本機分支：`fix-extref-downgrade-291`，改動未 commit
- remote：只有 `origin`（上游）。沒有 fork，沒有推送，沒有上游留言
- 工具鏈：`go1.27.1 darwin/arm64`；模組 `go 1.25`；`golangci-lint 2.15.0`（CI 用 `latest`）
- 交付草稿：`plans/cyclonedx-go-291-pr-draft.md`

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-17T14:03:56Z` | `DISCOVERED` | 初篩 cyclonedx-go open issue。timeline 只有下游 `anchore/syft#5246`、`#5493`（closed）與本庫 issue `#298` 的引用；open PR 清單沒有碰 `supportsExternalReferenceType` 的 PR；沒有 assignee 和留言 |
| `2026-11-17` | `REPRODUCED` | 新測試在未修改的 `b3eb7b74` 上連跑 3 次都失敗 |
| `2026-11-17T14:20:11Z` | `READY_FOR_HUMAN_PR` | 修復後 test、race、vet、lint 都通過；交給人 |

硬門檻：沒有重複或進行中的 PR、沒有封鎖、不需要先由維護者決定（schema 已經寫明各版本支援哪些類型）、已驗證、已重現。

## 範圍比 issue 寫的大

issue 回報的是 1.6 新增的 4 個類型。我用 repo 內附的 `schema/bom-1.x.schema.json` 與 `bom-1.1.xsd` 列出每個版本的 externalReference 類型，結果同一個函式還漏了另外 3 個：

| 類型 | schema 起始版本 | `b3eb7b74` 的判定 |
| --- | --- | --- |
| `release-notes` | 1.4 | 視為 1.1 起都支援 |
| `poam`、`security-contact` | 1.5 | 視為 1.1 起都支援 |
| `digital-signature`、`electronic-signature`、`rfc-9116`、`source-distribution` | 1.6 | 視為 1.1 起都支援（issue 回報的部分） |

上游的規則是「一個 issue 一個 bug」。這 7 個都是 `supportsExternalReferenceType` 的同一個錯誤，所以放在同一個修復裡。要不要把範圍縮回 issue 寫的 4 個，由人決定。

## 未修改程式碼上的基線

```
$ go test -count=1 ./...
ok  	github.com/CycloneDX/cyclonedx-go	36.954s
```

## 重現：新測試在未修改程式碼上失敗（連跑 3 次）

`Test_convertExternalReferences_typesNewerThanTargetSpec`（`convert_test.go`）。3 次都是同樣 25 個斷言失敗，例如：

```
Messages:   	type digital-signature in spec 1.1 … 1.5
Messages:   	type poam in spec 1.1 … 1.4
Messages:   	type release-notes in spec 1.1 … 1.3
Messages:   	type rfc-9116 in spec 1.1 …
```

## 修復後

`convert.go` 只改 `supportsExternalReferenceType`：加上 `release-notes` → 1.4、`poam`／`security-contact` → 1.5、4 個 1.6 類型 → 1.6。`git diff --stat`：`convert.go | 6 +`、`convert_test.go | 27 +`。

```
$ go test -count=1 -run Test_convertExternalReferences_typesNewerThanTargetSpec ./
ok  	github.com/CycloneDX/cyclonedx-go	0.258s
$ go test -race -count=1 ./...
ok  	github.com/CycloneDX/cyclonedx-go	40.282s
$ go vet ./...                  # 沒有輸出
$ golangci-lint run ./...
0 issues.
```

既有的 snapshot 測試（cupaloy）都沒變。

## 沒做的事

- 沒有 commit。DCO 要求每個 commit 都有 `Signed-off-by`，由人用 `git commit -s` 提交。
- 沒有在 issue 留言、沒有 fork、沒有推送。
