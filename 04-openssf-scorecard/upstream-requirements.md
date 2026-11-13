# OpenSSF Scorecard 上游規則

這份筆記只適用 `ossf/scorecard` 的 `main`。外部 checkout 是 `/Users/dennis/Desktop/upstream-src/ossf/scorecard`。本協調庫不跑 Scorecard 的二進位，也不改分數。

## 政策檔

`CONTRIBUTING.md`、`AGENTS.md`、`SECURITY.md`。每個上游 commit 要 `git commit -s`。改變分數結果需要充分理由並經維護者同意；[Changing score results](https://github.com/ossf/scorecard/blob/main/CONTRIBUTING.md) 寫明分數變動不能只靠單方面判斷。

`AGENTS.md` 要求 `make unit-test` 與 `make check-linter`。這兩個 target 要先在外部 checkout 確認仍存在，再考慮執行。文件與 Makefile 不一致時，記下實際缺口，不改用另一套沒記載的指令。

## 本次驗證

last_verified_at: 2026-11-13T16:42:51Z

<!-- policy-shas:start -->
| 儲存庫 | 分支 | 路徑 | blob SHA |
| --- | --- | --- | --- |
| `ossf/scorecard` | `main` | `AGENTS.md` | `adea0b1be7485871fb981331dd8a9f1cdf4997c8` |
| `ossf/scorecard` | `main` | `CONTRIBUTING.md` | `5567b477885534fbc831d212bcf2ab04857b74ae` |
| `ossf/scorecard` | `main` | `SECURITY.md` | `45773d1a3ef892ea92fbf772d168230c90c8a91a` |
<!-- policy-shas:end -->

## #2161 的範圍

`#2161` 是 Branch-Protection check。timeline 上 2022 年的 `ossf/scorecard-action#895` 不是這個 issue 的修復 PR。`#5455` 的 diff 已讀：它修 `#5450`，把 unknown 收成 inconclusive，沒有覆蓋已刪除的 release branch、其他 default branch 改名，或 API 權限錯誤。不能把它記成 `#2161` 的 `definite_duplicate`。

investigation_verified_at: 2026-11-13T16:55:05Z

閱讀範圍是 `checks/raw/branch_protection.go`、其測試、`checks/evaluation/branch_protection.go`，以及 `#5455` 的 diff。只挑一個可控案例寫預期行為，例如已刪除的 release branch。不要在同一則筆記裡把「分支已刪除」「預設分支改名」「token 權限不足」「分支真的沒有保護」收成同一個分數。

狀態保持 `NEEDS_MAINTAINER`。不改 score semantics。
