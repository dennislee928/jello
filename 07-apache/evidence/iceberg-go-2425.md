# 證據：apache/iceberg-go #2425

- status：`DUPLICATE_OR_IN_PROGRESS`（main 已修好）
- last_verified_at：`2026-11-18T17:00:00Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/apache/iceberg-go`
- 本機分支：`repro-dictionary-filter-2425`，只加了測試，沒有 commit
- remote：只有 `origin`。沒有 fork、沒有推送、沒有上游留言
- 工具鏈：`go1.27.1`；模組 `go 1.26.3`

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-18T16:00:05Z` | `DISCOVERED` | 沒有留言、沒有 timeline 事件、沒有提到 #2425 的 PR |
| `2026-11-18T17:00:00Z` | `DUPLICATE_OR_IN_PROGRESS` | 新測試在 main `3d1d676` 上通過；在回報時的 `8ef0a092` 上失敗。找出的修正點是 `daed1f9` |

## 測試

在 `table/table_test.go` 的 `TableWritingTestSuite` 加入 `TestRowFilterOnDictionaryEncodedStringColumn`：

1. 寫一個存入 Arrow schema 的 Parquet 檔，欄位 `s` 是 `dictionary<int32, utf8>`，值是 `["a","b","a"]`
2. 用 `AddDataFilesByPath` 加入 table
3. 用 `EqualTo(s, "a")` 掃描，預期 2 列

用 `memory.NewCheckedAllocator` 確認沒有記憶體洩漏。v1、v2、v3 三種格式都會跑。

## 結果

| commit | arrow-go | 結果 |
| --- | --- | --- |
| `8ef0a092`（issue 回報時的 main） | `v18.8.0` | FAIL：`invalid: referenced field %!s(<nil>) was dictionary<values=utf8, indices=int32, ordered=false>, but should have been utf8`（與 issue 相同） |
| `daed1f9~1` | `v18.8.0` | FAIL |
| `daed1f9`（`chore(deps): bump arrow-go to v18.9.0 (#2632)`，`2026-11-17`） | `v18.9.0` | ok |
| `3d1d676`（目前的 main） | `v18.9.0` | ok，三種格式都通過，`-count=1` 連跑 3 次 |

## 原因

arrow-go v18.9.0 改了 `arrow/compute/exprs/exec.go` 的 `execFieldRef`：如果欄位是 dictionary、而且值是 binary 類型，就改用 dictionary 的值型別去比對預期型別（新增 `valueType := dictType.ValueType`）。這就是 `plans/iceberg-go-2425-fix-plan.md` 的方案 B，已由上游完成。iceberg-go 只要升級依賴就修好了。

## 還能做的事（由人決定）

- 在 issue 留言，說明 main 已因 `#2632` 修好，附上重現步驟與 `8ef0a092` 及 `3d1d676` 的對照，請維護者確認後關閉。留言由人撰寫
- 補一個只加回歸測試的 PR，避免以後再壞。要先問維護者要不要，因為 iceberg-go 規定要先認領並等維護者回應
- 不需要再寫修復
