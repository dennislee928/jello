# collector-contrib #53341：留言大綱與修復計畫

- issue：https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/53341
- base：`main` `093cbfd996`（`2026-11-19`）
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-collector-contrib`（sparse，已加入 `receiver/datadogreceiver`）
- 元件：`receiver/datadog`，alpha，`distributions: [contrib]`，code owners 是 `boostchicken`、`MovieStoreGuy`
- 現況：沒有認領、沒有 PR；標了 `waiting-for-code-owners`
- 前提：
  1. collector-contrib 的 `AGENTS.md` 規定方向要先在 issue 上和 code owner 談定
  2. 首次貢獻者在第一個 PR（`#53246`）合併前，只能有一個 ready for review 的 PR，所以這件先開 **draft**

## 留言大綱（人自己擴寫；OTel 不收 AI 撰寫的留言）

1. 想做這件，請 code owner 確認方向
2. 確認根因：`internal/translator/series.go` 的 `TranslateSeriesV1` 只檢查 `len(points) != 2`，接著就 `int64(*points[0])`、`*points[1]`；JSON 的 `null` 解碼成 nil 指標，所以會 panic
3. 預計做法：沿用迴圈裡既有的慣例，`points[0]` 或 `points[1]` 是 nil 時就跳過這個 point，和長度不對時一樣
4. 要問 code owner：
   - 跳過就好，還是要記一筆 debug log 或計數？（現有的 `len != 2` 是直接跳過）
   - 同一個 series 裡其他正常的 point 照常處理，對嗎？
5. 測試：在 `series_test.go` 的 `TestTranslateSeriesV1` 加 case，覆蓋時間戳為 null、值為 null、兩者都正常；再視情況在 receiver 層補一個 `/api/v1/series` 帶 null 時回 2xx、不 panic 的測試
6. 說明 `#53246` 合併前會先開 draft

## 修復計畫（code owner 同意後才實作）

### 改動

`receiver/datadogreceiver/internal/translator/series.go`，`TranslateSeriesV1` 的 point 迴圈：

```go
if len(points) != 2 || points[0] == nil || points[1] == nil {
	continue // The datapoint is missing a timestamp and/or value, so this point should be skipped
}
```

只動這一處。V2 與 V3 用的是 protobuf，型別不是指標，不受影響（實作時要再確認）。

### 測試

- `internal/translator/series_test.go`：
  - 用既有的 helper（第 28 行一帶，把 `[]float64` 轉成 `[][]*float64`）
  - 新增手動組的 `[][]*float64{{nil, &v}, {&ts, nil}, {&ts, &v}}`
  - 斷言只產生 1 個 data point、值正確、沒有 panic
- 先在未修改的 `main` 上確認新測試會 panic 或失敗（3/3），再套修正
- 可選：`receiver_test.go` 對 `/api/v1/series` 送 `{"series":[{"metric":"m","type":"gauge","points":[[1700000000,null]]}]}`，斷言 HTTP 狀態碼為 2xx

### changelog

`make chlog-new` 建 `.chloggen/53341-datadogreceiver-null-series-point.yaml`：
- `change_type: bug_fix`
- `component: receiver/datadog`
- `issues: [53341]`
- note 寫使用者看得到的效果：null 值的 point 會被跳過，不再 panic

### 命令

```sh
cd receiver/datadogreceiver
go test -race -count=1 ./...
go vet ./...
make lint
cd ../.. && make chlog-validate
```

### commit 與 PR

- commit 用 `Assisted-by:`，不要用 `Co-authored-by:`（EasyCLA）
- PR 描述由人寫、自己勾 Authorship；先開 draft
