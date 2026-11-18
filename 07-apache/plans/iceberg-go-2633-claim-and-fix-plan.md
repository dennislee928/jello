DRAFT

# iceberg-go #2633：認領要求與備援修復計畫

- verified_at：`2026-11-18`（`gh api` GET；程式碼取自本機 checkout `3d1d676`）
- 判定：`DUPLICATE_OR_IN_PROGRESS`（回報者自己認領），**不留言認領**

## 認領要求（issue 與規則）

- 回報者 `Shruthirdy` 在內文寫了 "I already reproduced this issue locally and working on a fix for this"
- `CONTRIBUTING.md`（blob `43c79524`）的 "Picking Up Issues"：
  - 先查有沒有 PR
  - 留言認領，等維護者回應
  - 新貢獻者一次只做一件
  - 同一件 issue 有兩個 PR 時，保留先認領的那個
- 回報者在 issue 內文就認領了，比任何後來的留言都早

## 留言要點

- **現在不留言**。照 iceberg-go 的規則，後來的人做了也不會被採用
- 只有在回報者明說不做、或維護者把 issue 開放出來時才考慮。到那時留言要涵蓋：
  - 確認回報者已放棄
  - 說明要做的範圍：只放寬 `UpdateColumn`，`RenameColumn` 不動

## 備援修復計畫（只在接手時才用）

- 根因：`table/update_schema.go` 的 `updateColumn`（第 475 行）只用 `u.findField(fullName)` 找欄位，所以找不到同一次 `UpdateSchema` 新加、只存在 `u.adds` 與 `u.addedNameToID` 裡的欄位。`MoveColumn` 沒有這個問題，因為 `findFieldForMove`（第 652 行）會退回去查 `addedNameToID`
- 修法：比照 Java 的 `findForUpdate`。讓 `updateColumn` 找不到時，改去查同一次更新裡新加的欄位，並把 doc、type、required、write-default 的變更套到 `u.adds` 裡的那個欄位。`renameColumn` 繼續只用 `findField`，所以仍然回傳錯誤，和 Java 一致
- 測試：
  - 比照 Java 的 `testUpdateAddedColumnType` 與 `testUpdateAddedColumnDoc`
  - 加一個「rename 新加欄位仍然失敗」的 case
- 命令：`make test`、`make lint`；commit 要有 `Signed-off-by`

## 接手時的認領留言要點（只在條件成立時用，由人撰寫）

使用條件：回報者 `Shruthirdy` 明說不做，或維護者在 issue 上表示開放給別人；而且你在 iceberg-go 沒有其他進行中的 issue（新貢獻者一次一件）。條件不成立時不要留。

1. 開頭："I'd like to work on this"（`CONTRIBUTING.md` 的建議格式），並說明看到回報者已不做（附連結）
2. 範圍：讓 `UpdateColumn` 能更新同一次 `UpdateSchema` 新加的欄位（比照 Java `findForUpdate`），`RenameColumn` 維持回傳錯誤
3. 測試：比照 Java 的 `testUpdateAddedColumnType`、`testUpdateAddedColumnDoc`，再加一個 rename 新欄位仍失敗的 case
4. 說明會等維護者回應才開始寫程式；commit 會加 `Signed-off-by`
