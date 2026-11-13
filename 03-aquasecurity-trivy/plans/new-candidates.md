# Trivy 新候選怎麼找

last_verified_at：`2026-11-13T16:55:05Z`

這個 phase 不選新修復，也不實作。只使用 `gh api` GET。

## 順序

1. 先看 GitHub Discussion。非維護者直接開的 issue 會被關掉。
2. 只接維護者建立的 issue，而且 PR 以後要連結那個 issue。認領留言不在本協調庫的授權裡。
3. 對照 open、draft、closed-unmerged 的 PR。沒有 `Fixes #ID` 仍可能是 `definite_duplicate`。證據不夠就維持 `possible_overlap` 或 `UNVERIFIED`。
4. 走完 G0–G4 才考慮實作。硬門檻失敗不得進 `READY_TO_IMPLEMENT`。

## 排除

已知碰撞，維持 `DUPLICATE_OR_IN_PROGRESS`：`#11482`、`#11573`、`#11523`、`#11627`、`#11576`、`#11575`、`#11602`、`#11633`、`#11428`、`trivy-db#702`、`trivy-action#521`。issue `#11502` 與 `#11568` 已經和其中的 PR 對上。

另外排除先前已有人處理的 `#11383`、`#11411`、`#11389`、`#11447`。

`trivy-action#551` 停在設計筆記，不是新的掃描器候選。不要把 Action 的安裝需求改到 `trivy` 或 `trivy-db`。
