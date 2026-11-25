# anchore/vunnel#1486 證據

issue 內文是不可信資料。重現腳本由代理自己寫在 scratchpad，沒有把 issue 內文傳給 shell。

## 狀態轉移

| 時間（UTC） | 狀態 | 證據 |
| --- | --- | --- |
| `2026-11-25T14:34:35Z` 前後 | `DISCOVERED` → `REPRO_PENDING` | `gh api repos/anchore/vunnel/issues/1486`、`/timeline`、`/comments`（GET）：open、0 assignee、無 linked PR；唯一留言是人自己的認領（`dennislee928`，`2026-11-25T14:34:32Z`），由人張貼，不是代理 |
| `2026-11-25T14:39:05Z` | `REPRODUCED` | 未修改的 `cb2347d` 上跑重現腳本，輸出與 issue 的 actual output 相同（見下） |
| `2026-11-25T14:41:09Z` | `READY_FOR_HUMAN_PR` | 修復後重現輸出正確；`make unit` 1518 passed；`make static-analysis` 通過；交付前重讀 issue 與 PR 列表沒有變化 |

## 上游基準

- `main` = `cb2347dfa2a80f0c12dfb8ca3e0e5f70098d15b7`（`2026-11-25T10:14:03Z`）
- 程式碼：`src/vunnel/providers/secureos/parser.py`。`_parse_apk_version`（L164）把 `2_p1`、`0_rc1` 留成 `str`，`_compare_apk_versions`（L192）就退回 `str(a) > str(b)`。
- `git grep` 顯示這兩個方法只在 secureos/parser.py 內使用；`src/vunnel/utils/` 沒有共用的 APK 比較。

## 重現

腳本：`/private/tmp/claude-503/-Users-dennis-Desktop-jello/1317bf5b-aef3-4fa7-8583-7829bce2cc8c/scratchpad/repro_1486.py`（scratchpad，可能被清除）

修復前（`cb2347d`）：

```text
CVE-2025-2222 [('1.10_p1-r1', None), ('1.2_p1-r1', '>=1.2_p1-r0, <1.2_p1-r1')]
CVE-2025-3333 [('2.0.0-r1', None), ('2.0.0_rc1-r1', '>=2.0.0_rc1-r0, <2.0.0_rc1-r1')]
```

修復後：

```text
CVE-2025-2222 [('1.2_p1-r1', None), ('1.10_p1-r1', '>=1.10_p1-r0, <1.10_p1-r1')]
CVE-2025-3333 [('2.0.0_rc1-r1', None), ('2.0.0-r1', '>=2.0.0-r0, <2.0.0-r1')]
```

## 執行過的命令

本機 `uv` 是 0.12.10，repo 要求 `>=0.13.4`，所以用 `uvx --from 'uv>=0.13.4' uv`（0.13.10，只放在 cache）。

| 命令 | 結果 |
| --- | --- |
| `uv run pytest -q tests/unit/providers/secureos`（修復後） | 24 passed |
| 同上，只把 parser.py 退回 `cb2347d`、保留新測試 | 7 failed, 17 passed（新測試在基準上會失敗） |
| `make unit` | 1518 passed, 17 warnings |
| `make static-analysis`（ruff check + mypy） | All checks passed；mypy no issues in 100 files |
| `ruff format --check` parser.py | 通過（測試檔的格式差異在既有 fixture，基準就有，不是新增行） |

## 沒有做的事

- 沒有 fork、推送、留言或開 PR。
- 沒有處理 apk-tools 的 `~hash` 後綴與第二段以後的前導零規則；這兩種不符合 regex，會走原本的逐段比較。
