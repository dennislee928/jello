# CV 影響紀錄

一筆已合併變更一份。沒有 merge SHA 就不要填影響人數。使用量未知就寫 `unknown`，不要留空讓讀者當成零，也不要把上游專案的下載次數、星數或 Action 安裝數算到這筆修復上。

複製這份模板到 `reports/cv-impact.md` 的下一筆，或在有合併 PR 之後另存 `reports/cv/<merge-sha>.md`。現況範本見 `reports/cv-impact.md`。

## 識別

- author：
- org / repo：
- PR URL：
- merge SHA：
- release：
- last_verified_at：

## 測試紀錄

只寫實際跑過的命令、工作目錄與結果。命令若只出現在上游文件、還沒在 `/Users/dennis/Desktop/upstream-src/<org>/<repo>` 跑過，不要寫成已通過。

| 命令 | 工作目錄 | 結果 |
| --- | --- | --- |
|  |  | 未執行 |

## Verified

只寫能指回 PR URL、merge SHA、release note 或測試輸出的事實。

| 欄位 | 值 | 證據 |
| --- | --- | --- |
| author |  |  |
| PR URL |  |  |
| merge SHA |  |  |
| release |  |  |
| 測試紀錄 |  |  |
| 使用量 | unknown |  |

## Inferred

推論與事實分開。這一段可以寫假設，但不能改寫上一節的數字。沒有獨立證據的採用數、下載數、使用者數，都不要寫進來充當事實。

| 欄位 | 推論 | 為什麼還不是事實 |
| --- | --- | --- |
| 使用量 | 不推論 | 上游下載數不屬於這筆修復 |

## 使用量

unknown
