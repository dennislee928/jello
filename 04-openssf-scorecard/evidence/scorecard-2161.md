# 證據：ossf/scorecard #2161

- status：`NEEDS_MAINTAINER`
- last_verified_at：`2026-11-13T16:55:05Z`
- `#5455` overlap：對 `#5450` 是 `definite_duplicate`（PR 內文有 `Fixes #5450`）。對 `#2161` 不是。`#5455` 把 unknown 改成 inconclusive，沒有處理已刪除的 release branch、其他 default branch 改名，或 API 權限錯誤。
- 分數語意：不改。`unknown` 保持 inconclusive，`unprotected` 只在 probe 明確說沒有保護時使用。

細節在 `plans/2161.md`。
