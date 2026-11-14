# 證據：apache/superset #46196

- status：`DUPLICATE_OR_IN_PROGRESS`（前一個狀態 `REPRO_PENDING`，`2026-11-13T16:55:05Z`）
- last_verified_at：`2026-11-14T10:24:51Z`
- issue：open，無 assignee，0 則留言，labels 為 `#bug`、`🦾 ai-candidate`
- issue_updated_at：`2026-11-13T18:19:17Z`（`🦾 ai-candidate` 標籤事件）
- 回報者版本：`6.1.0`
- 重疊 PR：[#41453](https://github.com/apache/superset/pull/41453) `fix(chart): chart description not showing`，`merged` 為 true，merged_at `2026-06-26T19:38:31Z`，merge SHA `834ccf2613dd6bc9fca235c74ea0dd9b30628311`
- overlap：`definite_duplicate`。PR 內文沒有 `Fixes #46196`，#46196 的 timeline 也沒有交叉引用。判定依據是路徑、符號與症狀
- 變更檔：`superset-frontend/src/dashboard/actions/hydrate.ts`，+1 / −1
- 外部 checkout：沒有建立。沒有跑測試，沒有補丁

## 根因對照

#41453 的內文寫：dashboard hydrate 把 nh3 消毒過的 HTML 存在 `description_markeddown`，`Chart.tsx` 讀的是 `description_markdown`，所以 `isExpanded && slice.description_markdown` 永遠不成立；選單由另一個有值的 `slice.description` 控制，所以仍出現。這和 #46196 的描述相同：「`Show Description` 選項存在，切換後什麼都沒有」。

前一輪 `plans/46196.md` 讀到的 master blob（`977954cc…`）已經是修好後的對應，所以當時只看 master 看不出版本差。

## `hydrate.ts` 在各 ref

| ref | 行 | 內容 | 結果 |
| --- | --- | --- | --- |
| `master` | 205 | `description_markdown: slice.description_markeddown` | 已修 |
| `6.1` 分支 | 181 | `description_markdown: slice.description_markeddown` | 已修（compare `834ccf2...6.1`：diverged，ahead 260，行已改，屬 cherry-pick） |
| `6.1.0` tag | 181 | `description_markeddown: slice.description_markeddown` | 未修（compare `834ccf2...6.1.0`：diverged，ahead 239 / behind 1769） |

`6.1` 分支與 `6.1.0` tag 的判斷只靠 compare 和檔案內容，沒有找出 cherry-pick 的 commit SHA。下一個 6.1.x 是否發布、何時發布，都不知道。

## 這次實際下的 GET

`gh api repos/apache/superset/issues/46196`、`.../issues/46196/timeline`、`.../issues/46196/events`

`gh api repos/apache/superset/pulls/41453` 與其 files、`issues/41453` 內文

`gh api repos/apache/superset/compare/834ccf2...6.1.0`、`.../compare/834ccf2...6.1`

`gh api repos/apache/superset/contents/superset-frontend/src/dashboard/actions/hydrate.ts`，ref 為 `master`、`6.1`、`6.1.0`

`gh api repos/apache/superset/branches`、`git/refs/tags`

搜尋 `repo:apache/superset is:pr description_markdown`，以及 `is:pr "chart description" created:>2026-09-01`。前者命中 #41453；其餘命中（#43769、#42479、#32958、#23547 與第二組結果）是搜尋雜訊，沒有改 `hydrate.ts` 的 description key。全部 HTTP 成功。

## 不做的事

不寫補丁，不開 PR，不留言。#41453 是他人的工作，不計入 `CONTRIBUTIONS.md`。不要把不可信的 `description` 放進 `dangerouslySetInnerHTML`。
