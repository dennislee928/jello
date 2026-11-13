# 重現紀錄

在外部 checkout 重現。路徑是 `/Users/dennis/Desktop/upstream-src/<org>/<repo>`。不要把上游樹複製進本儲存庫。做不到的步驟就停，狀態保持 `REPRO_PENDING`。

## 識別

- org / repo：
- issue_number：
- 外部 checkout SHA：
- last_verified_at：

## 環境

記載實際使用的命令。文件與工作樹不一致時，記下缺口，不要改跑另一套沒寫在上游文件裡的指令。

## 步驟

1.
2.
3.

## 預期

寫可觀察的介面或 API 結果。對 Superset #46197，斷言是沒有 cross-filter 的 `filterState` / `extraFormData`，不是 `setDataMask` 零呼叫。

## 實際

只寫觀察到的事實。不要把推測寫成已重現。

## 結論

- 已重現：狀態改 `REPRODUCED`，並指向 evidence 檔。
- 需要執行中的 UI 才能判定：維持 `REPRO_PENDING`。
- 與既有 PR 重疊：改 `DUPLICATE_OR_IN_PROGRESS`。
