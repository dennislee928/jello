# iceberg-go #2425：修復計畫

- base：`main` `3d1d676`（`2026-11-18`），依賴 `arrow-go/v18 v18.9.0`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/apache/iceberg-go`
- 前提：人先在 issue 留言認領，維護者回應並選定方向後才寫正式修復（`CONTRIBUTING.md`）。在那之前只做重現

## 根因（issue 的說明，Phase 4 要驗證）

- `table/arrow_scanner.go` 的 `filterRecords` 先對 file batch 套 filter，之後才做投影
- arrow-go 的 `exprs.ExecuteScalarExpression` 檢查欄位型別：string 運算式接受 `utf8` 與 `large_utf8`，但不接受值為 `utf8` 的 dictionary。所以 Parquet 內嵌的 Arrow schema 是 dictionary 型別時（例如 PyIceberg 從 pandas `Categorical` 寫出的檔案），row filter 會失敗

## 回歸測試（先在未修改的程式碼上重現）

在 `table/table_test.go` 的 `TableWritingTestSuite` 新增一個 case，用既有的 helper：

1. 用 `memory.NewCheckedAllocator` 建一個 Arrow table：`id int64`，`s dictionary<int32, utf8>`，值是 `["a","b","a"]`
2. 用 `writeParquetWithStoredSchema` 寫入，讓 Parquet 存入 Arrow schema
3. 建一個 iceberg schema 為 `id long`、`s string` 的 table，用 `AddDataFilesByPath` 加入檔案
4. `Scan(table.WithRowFilter(iceberg.EqualTo(iceberg.Reference("s"), "a"))).ToArrowTable`，預期 2 列、`id` 為 `[1, 3]`

如果 `AddDataFilesByPath` 本身就拒絕 dictionary 型別，就改用 `AddDataFiles` 搭配手動建的 `DataFile`，並把這點記進 evidence。

## 修法（兩條路，由維護者選）

| 方案 | 改哪裡 | 優點 | 缺點 |
| --- | --- | --- | --- |
| A：iceberg-go 先解碼 | 在 `filterRecords` 或建立 filter 的地方，用 `compute.Cast`／`array.Dictionary` 的值，把 filter 會用到的 dictionary 欄位解碼成 value type | 只改本 repo，馬上能修 | 每個 batch 多一次解碼，只該在 filter 用到的欄位做 |
| B：arrow-go 放行 dictionary | arrow-go `exprs/exec.go` 的欄位型別檢查，接受值型別相符的 dictionary（類似 arrow-go `#440` 對 `large_utf8` 的處理） | 修在根源，comparison kernel 本來就會解碼 dictionary | 要先在 arrow-go 合併、發版，iceberg-go 再升級；跨 repo、時間長 |

在維護者決定前，預設準備方案 A：只解碼 filter 參照到的欄位，而且只在型別是 dictionary 時才做。

## 命令

```sh
go test ./table/ -run 'TestTableWriting.*Dictionary' -count=1
make test
make lint        # 沒裝的話先 make lint-install
dev/check-api-compat.sh   # 如果動到對外 API
```

## 風險與待決事項

- 方向（A 或 B）要維護者選
- 效能：方案 A 不能讓沒有 dictionary 欄位的掃描變慢
- 範圍：其他 predicate（`NotEqualTo`、`In`、`IsNull`、`StartsWith`）走同一條路徑；要測到哪些，跟維護者確認
- DCO：每個 commit 都要 `Signed-off-by`
