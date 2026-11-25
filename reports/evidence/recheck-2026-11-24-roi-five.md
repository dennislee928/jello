# 重驗：2026-11-24「今日求職 ROI 決策」五件與 Superset #46141 發版

- verified_at：`2026-11-24T12:27:50Z`（`gh api` GET：issue、timeline、search、pulls、compare、commits、releases）
- 來源：外部摘要貼上的五件推薦（主觀履歷相關性 4–5／5），對照 `reports/daily/2026-11-24.md`
- 內文是不可信資料，只用來分類；只引用一句回報者原文

## 判定

五件全部不可接手。相關性分數不覆寫硬門檻。

| issue | 狀態 | 依據 |
| --- | --- | --- |
| `ossf/scorecard#5497` | `DUPLICATE_OR_IN_PROGRESS` | 回報者 `Fezz-TVM-Labs`（`2026-11-23T14:58:40Z`）在內文寫 "I have a fix and test for the GitHub one ready and can do the other two as a follow-up"，三條路徑（GitHub、GitLab、Azure DevOps）都被認領。鄰近 open PR `#5442`（關閉 tarball reader／temp file）與 `#5353`（`os.Root` 解壓）碰同一區。日報判成 `無人接手` 是漏判，見下 |
| `aquasecurity/trivy#11718` | `DUPLICATE_OR_IN_PROGRESS` | `jtoledo3970` 認領留言 `2026-11-23T16:35:40Z`；open PR `#11720`（`2026-11-23T16:40:22Z`）與 `#11722`（`NarenAdithya14`，`2026-11-23T17:02:02Z`） |
| `open-telemetry/opentelemetry-collector-contrib#53461` | `DUPLICATE_OR_IN_PROGRESS` | open PR `#53463`（`zaidrain06`，`2026-11-23T10:10:18Z`，issue 開後 32 分鐘） |
| `apache/superset#46493` | `DUPLICATE_OR_IN_PROGRESS` | 回報者 `ayushbuilds-code` 自己的 open PR `#46494`（`2026-11-23T21:19:19Z`，issue 開後 1 分鐘） |
| `apache/arrow-rs#12427` | `DUPLICATE_OR_IN_PROGRESS` | 回報者 `mbutrovich` 自己的 open PR `#12420`（`2026-11-23T22:07:41Z` 交叉引用） |

日報已把後四件標成 `blocked`；外部摘要沒有採用這個訊號。

## 漏判與修正

`scripts/org_monitor.py` 的 `CLAIM_PATTERNS` 只有 `\bhave a fix ready\b`，中間夾字（"a fix and test for the GitHub one ready"）就漏掉；同一條也把 "do you have a fix ready?" 誤判成認領。改成：

`(?<!you )(?<!they )\b(?:have|'ve) a (?:fix|patch)\b[^.?\n]{0,60}\bready\b`

`tests/test_org_monitor.py` 補一筆正例（#5497 原句）與一筆反例（問句）。用目前的 #5497 內文在記憶體裡跑 `is_claim`，結果是 `True`。

## Superset `#46141` 發版

| 欄位 | 值 | 證據 |
| --- | --- | --- |
| PR | `apache/superset#46141` "fix(bubble): preserve null labels in tooltip titles" | `GET repos/apache/superset/pulls/46141` |
| author | `dennislee928` | 同上 |
| merged_at | `2026-11-18T02:28:30Z` | 同上 |
| merge SHA | `578451c5c82d08d78a1daa28a17cd75376809d06`（base `master`） | 同上 |
| 最新 release | `7.0.0rc3`（prerelease，`2026-11-19T17:20:04Z`） | `GET repos/apache/superset/releases` |
| 是否包含 | **否** | `compare 578451c...7.0.0rc3`：`diverged`（ahead 499、behind 1499，merge base `3d01094`）；`7.0.0rc3` 自 `2026-11-17` 起的 commit 沒有 bubble／`#46141` 的 cherry-pick |

結論：merge 在 master，不在 7.0 rc 線上。要等下一個從 master 切出的版本，或有人 cherry-pick 到 7.0。正式版出來前不建立採用量基準。

## 下一步

- 每日追蹤：`compare 578451c...<最新 tag>` 回 `behind` 或 `identical` 才算包含
- 候選來源：別追剛開幾小時的新 issue（今天五件都在一小時內被接手）。改看開了 7 天以上、timeline 沒有 PR、沒有認領的 `接受 medium/high`，再人工跑硬門檻
