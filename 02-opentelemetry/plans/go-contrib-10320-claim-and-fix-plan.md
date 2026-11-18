DRAFT

# go-contrib #10320：認領要求與備援修復計畫

- verified_at：`2026-11-18`（`gh api` GET）
- 判定：`DUPLICATE_OR_IN_PROGRESS`（回報者自己認領），**不留言認領**
- OTel 禁止張貼 AI 撰寫的留言，所以這裡只有要點

## 認領要求（issue 與規則）

- 回報者 `yuminn-k` 在內文寫了 "I can open a PR with this fix and regression test" 和 "I'd like to work on a fix for this, if the approach sounds good to the code owners"。也就是先等 code owner 同意，再由他自己開 PR
- issue 目前沒有留言、沒有 assignee
- `AGENTS.md`（blob `fe314480`）：先寫會失敗的單元測試再修；完成前跑 `make precommit`；CHANGELOG 那一行放 PR 編號，不放 issue 編號
- OTel 的 GenAI 政策：要揭露 AI 協助，描述與回覆用自己的話寫

## 留言要點

- **現在不留言**。回報者已經表明要做，也在等 code owner
- 只有在 code owner 同意、但回報者長時間沒有開 PR（例如超過 30 天），而且回報者同意讓出時，才考慮接手。到那時由人留言，要涵蓋：
  - 先問回報者是否還要做
  - 引用 issue 已有的重現測試與一行修法，不要重複分析

## 備援修復計畫（只在接手時才用）

- 根因：`propagators/aws/xray/propagator.go` 的 `extract()` 只對最後一段做 `strings.TrimSpace`，其他段直接交給 `strings.Cut(part, kvDelimiter)`；`" Parent"` 對不到 `parentIDKey`
- 修法：`key, value, ok := strings.Cut(strings.TrimSpace(part), kvDelimiter)`。最後一段原本的 `TrimSpace` 可以保留或移除，結果相同
- 測試：照 issue 的 4 組 header 寫成 table test，放進 `propagator_test.go`，斷言 `IsValid()` 與 `IsSampled()`；修改前後兩組要分別失敗、通過
- 其他：CHANGELOG `Fixed` 段加一行，以 PR 編號結尾；跑 `make precommit`

## 接手時的認領留言要點（只在條件成立時用，由人撰寫，OTel 不收 AI 撰寫的留言）

使用條件：code owner 已同意做法、回報者 `yuminn-k` 長時間沒開 PR，而且回報者回覆同意讓出。條件不成立時不要留。

1. 先問 `yuminn-k` 是否還打算做；在對方回覆之前不要接手
2. 對方同意讓出後，說明要接手，並沿用 issue 裡的重現測試與一行修法（`strings.Cut(strings.TrimSpace(part), kvDelimiter)`），不另做分析
3. 說明會補 table test（issue 的 4 組 header）與 CHANGELOG `Fixed` 一行，並跑 `make precommit`
4. 揭露有 AI 協助（OTel GenAI 政策），留言本身用自己的話寫
