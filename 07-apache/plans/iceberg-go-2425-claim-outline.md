DRAFT

# iceberg-go #2425：認領留言要點

依本庫規則，留言由人撰寫，代理不張貼，所以這裡只列要點。iceberg-go 的 `CONTRIBUTING.md` 要求先在 issue 留言認領，等維護者回應之後才開始寫程式；還沒有 PR 被合併過的新貢獻者一次只做一件。

## 留言要涵蓋的事實

- 認領：想做這件；還沒有在 iceberg-go 合併過的 PR，所以目前只做這一件
- 重現：等 Phase 4 跑完再填，只寫實際跑過的結果，包括 base SHA、如何產生 dictionary 欄位的檔案、錯誤訊息
- 根因位置（issue 已指出，可以確認）：
  - `table/arrow_scanner.go` 的 `filterRecords` 把 file batch 直接交給 arrow-go 的 `exprs.ExecuteScalarExpression`
  - arrow-go 的 `exprs/exec.go` 有型別檢查：string 運算式接受 `large_utf8`，但不接受值為 `utf8` 的 dictionary

## 要問維護者的問題（方向要由維護者決定）

issue 提出兩條路，請維護者選：
1. 在 iceberg-go 套用 filter 之前，先把 dictionary 欄位解碼成 value type。改動在本 repo，馬上就能修，代價是多一次解碼
2. 在 arrow-go 的型別檢查放行「值型別相符的 dictionary」，做法類似 arrow-go `#440` 對 `large_utf8` 的處理。要先改 arrow-go、等它發版，iceberg-go 再升級依賴

另外要確認：修好之後，`NotEqualTo`、`In`、`IsNull` 這些 predicate 也要涵蓋 dictionary 欄位嗎？

## 不要做的事

- 維護者回應前，不寫正式修復，只做重現
- 不同時認領 iceberg-go 的其他 issue
