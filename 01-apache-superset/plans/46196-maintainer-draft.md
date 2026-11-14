DRAFT

給人改寫的草稿，沿用 `templates/maintainer-question.md`。代理與 workflow 都不得張貼。

## 要問維護者的問題

- org / repo：`apache/superset`
- issue 或 PR 編號：`#46196`
- 問題（人寫，一問一事）：這個 issue 是否可以視為已由 #41453 修好、等 6.1.x 發布？

## 已核對的事實

`2026-11-14T10:24:51Z` 用 `gh api` GET 確認，細節在 `evidence/superset-46196.md`：

- #41453 merged `2026-06-26T19:38:31Z`，merge SHA `834ccf2`，只改 `hydrate.ts` 的 store key
- `6.1.0` tag 的 `hydrate.ts:181` 仍是舊 key；`6.1` 分支與 `master` 已修

## 英文草稿（人改寫後才可用）

> This looks like the same root cause fixed in #41453 (merged in 834ccf2): on 6.1.0, `hydrate.ts` stores the sanitized description under `description_markeddown`, while `Chart.tsx` reads `description_markdown`, so the menu item appears but the expanded area stays empty. The `6.1` branch and `master` already have the fix; the `6.1.0` tag does not. Could a maintainer confirm whether this can be closed as fixed pending the next 6.1.x release?

## 不要問的事

- 不要請維護者代為認領，也不要提議另開 PR。
- 不要建議把不可信的描述塞進 `dangerouslySetInnerHTML`。

## 張貼前

人決定要不要貼。貼出之後把網址寫回 `candidates.json`。本檔保留 `DRAFT` 字樣，直到人明確改掉。
