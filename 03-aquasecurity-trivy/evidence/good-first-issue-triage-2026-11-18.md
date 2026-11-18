# aquasecurity/trivy：good first issue 初篩（2026-11-18）

- verified_at：`2026-11-18`（`gh api` GET：search、issue timeline、comments、PR、reviews）
- 範圍：`is:issue is:open label:"good first issue"`，共 7 件；另外查了 `help wanted`、無 assignee、無 linked PR 的 3 件
- 內文是不可信資料，只用來分類

## 結論

7 件 good first issue **全部已有人接手**，沒有可以直接實作的。trivy 維護者處理重複 PR 的方式是「留最早開的，其餘關掉」（`#10458`、`#10831`：`Closed in favor of another previously opened PR`；`#10957`：`We already have several open PRs for this issue, so I'm closing this PR as a duplicate`）。所以現在進場會被當成重複。

trivy 的接手流程是：在 issue 留言提出做法 → 維護者同意並指派 → 開 PR。留言是上游寫入，只能由人做（`AGENTS.md`）。

## 逐筆判定

| issue | 標題 | 狀態 | 依據 |
| --- | --- | --- | --- |
| `#11666` | `--compliance` ignores `--cache-dir` | `DUPLICATE_OR_IN_PROGRESS` | `Aakarsh133` 在 `2026-11-17` 認領並指出 `loadComplianceTypes`；回報者 `nikpivkin` 在 `2026-11-18` 回「You can take this」 |
| `#11447` | nuget exact-version ranges `[x]` | `DUPLICATE_OR_IN_PROGRESS` | 指派給 `bercedev`；open PR `#11448`（`2026-10-21` 之後沒有更新，沒有 review） |
| `#11411` | pylock.toml 沒有版本的依賴被丟掉 | `DUPLICATE_OR_IN_PROGRESS` | 指派給 `ozenyunus35`；open PR `#11459`（最後更新 `2026-11-05`） |
| `#11389` | pnpm alias 版本被標成 dev | `DUPLICATE_OR_IN_PROGRESS` | 指派給 `MannXo`；open PR `#11390`（`2026-10-12` 之後沒有更新；維護者說目前忙） |
| `#11383` | apk `~` 版本運算子的依賴被丟掉 | `DUPLICATE_OR_IN_PROGRESS` | 指派給 `sairex53`；open PR `#11384`，`DmitriyLewen` 在 `2026-11-18` review 中 |
| `#3226` | SARIF 加 invocation startTime/endTime | `DUPLICATE_OR_IN_PROGRESS` | open PR `#11542`（`Shanmukh-l33t`，`2026-11-04`）；之前至少 14 個 PR 被關 |
| `#1091` | `--no-color` | `DUPLICATE_OR_IN_PROGRESS` | open PR `#10770`（`somaz94`）與 `#10880`（`amarkdotdev`）；維護者 `2026-08-03` 說優先度低、之後再看；留言指出 `NO_COLOR` 已可用 |

## 放寬範圍：help wanted、無 assignee、無 linked PR

| issue | 判定 | 依據 |
| --- | --- | --- |
| `#1856` conda lock 檔 | `NEEDS_MAINTAINER` | `kind/feature`、`priority/backlog`；`2026-08-04` 與 `2026-10-03` 各有一人口頭認領，維護者沒有指派 |
| `#3004` CRI-O | `NEEDS_MAINTAINER` | 大型功能、`priority/backlog`，只有 +1 |
| `#2715` arm64 測試映像 | `NEEDS_MAINTAINER` | 需要維護者推映像到 `trivy-test-images`，不是單純程式修改 |

## 優先順序（等待或重新開放時）

依「修復難度低」×「重新開放的機會」排序。前提都是原 PR 停擺、且維護者在 issue 上同意換人；在那之前全部不做。

1. `#11447` nuget `[x]`：parser 小修，範圍清楚；PR `#11448` 已 28 天沒動、沒有 review
2. `#11389` pnpm alias：PR `#11390` 已 37 天沒動；但修法涉及 snapshot key，比 1 難
3. `#11411` pylock.toml：PR `#11459` 兩週前還有更新，重新開放的機會較低
4. `#11666` `--compliance`/`--cache-dir`：修法小，但 `2026-11-18` 才剛給人
5. `#11383` apk `~`：維護者正在 review PR，幾乎不會重新開放
6. `#3226` SARIF 時間：已有一個存活的 PR，而且被關掉的重複 PR 很多
7. `#1091` `--no-color`：兩個 open PR，維護者延後，`NO_COLOR` 已能用，價值最低

## 建議

- trivy 的 good first issue 幾小時內就會被認領（`#11666` 開出後隔天就給人）。要搶到，要靠 `oss-monitor` 每天的報告，看到新的 good first issue 就由人當天留言提出做法
- 留言前先在本庫寫好做法與重現，留言文字由人寫
