# 證據：apache/airflow #77244

- status：`READY_FOR_HUMAN_PR`
- last_verified_at：`2026-11-18T17:50:00Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/apache/airflow`（`git clone --filter=blob:none`。原本是 sparse；uv workspace 需要全部成員，所以改成完整 checkout）
- base：`main` `c03582f661`
- 本機分支：`fix-odbc-driver-warning-77244`，改動未 commit
- remote：只有 `origin`。沒有 fork、沒有推送、沒有上游留言
- 工具鏈：
  - `uvx uv@latest`（`uv 0.13.9`）：airflow 要求 `uv >= 0.13.4`，本機的 `uv 0.12.10` 沒有更新
  - CPython 3.11.16
  - `brew install unixodbc`（2.3.14），`pyodbc` 需要它

## 測試環境

`uv run --project providers/odbc` 沒有裝 `devel-common` 的 caplog helper 需要的 `airflow_shared`，所以要把 `shared/*` 以 editable 一起裝進來：

```sh
W=(); for d in shared/*/; do [ -f ${d}pyproject.toml ] && W+=(--with-editable ${d%/}); done
uvx uv@latest run --project providers/odbc "${W[@]}" pytest providers/odbc/tests/unit/odbc/hooks/test_odbc.py -q -p no:cacheprovider
```

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-18T16:00:05Z` | `DISCOVERED` | 只有 bot 留言；沒有提到 #77244 的 PR |
| `2026-11-18T17:30:00Z` | `REPRODUCED` | 新測試的 3 個 case 在未修改的 `c03582f661` 上連跑 3 次都失敗 |
| `2026-11-18T17:50:00Z` | `READY_FOR_HUMAN_PR` | 修復後 odbc 測試、ruff、ruff format 都通過；交給人 |

## 基線（未修改的程式碼）

```
35 passed, 1 warning
```

## 重現

新增 `test_driver_without_extra_does_not_warn`，參數化 3 個 case，連線 extra 都沒有 `driver`：

- `driver-from-hook-params`：`hook_params=dict(driver="Blah driver")`
- `driver-from-default-driver`：`OdbcHook.default_driver = "Default driver"`
- `no-driver-at-all`

```
E   AssertionError: assert 'via connect... not be used' not in 'You have su...operators.\n'
FAILED ...::test_driver_without_extra_does_not_warn[driver-from-hook-params]
FAILED ...::test_driver_without_extra_does_not_warn[driver-from-default-driver]
FAILED ...::test_driver_without_extra_does_not_warn[no-driver-at-all]
# 3 次都一樣
```

失敗訊息裡有實際抓到的警告文字，證明 `caplog` 有抓到 log，這個「不得出現」的斷言不會在沒抓到時誤判通過。

## 修復

`providers/odbc/src/airflow/providers/odbc/hooks/odbc.py` 的 `OdbcHook.driver` 只改一行：`else:` → `elif extra_driver:`。現在只有「extra 有 `driver`，但 `allow_driver_in_extra` 沒開」時才會警告；其餘邏輯都不變。`git diff --stat`：`odbc.py | 2 +-`、`test_odbc.py | 15 +`。

一開始寫成巢狀 `if`，但整段警告要多縮排一層、diff 變大，後來改成這個一行的版本。

## 修復後

```
$ uvx uv@latest run --project providers/odbc "${W[@]}" pytest providers/odbc/tests/unit/odbc/hooks/test_odbc.py -q -p no:cacheprovider
38 passed, 1 warning                       # 基線 35 + 新增 3
$ ... pytest ... -k driver                 # 3 次
14 passed, 24 deselected                   # 3 次都一樣；既有的 test_driver_extra_raises_warning_by_default 等仍通過
$ uvx prek run ruff --files <兩個檔案>
Passed
$ uvx prek run ruff-format --files <兩個檔案>
Passed
```

## 沒有跑的

- `prek run mypy-providers`：hook 要靠 breeze（Docker），本機沒有裝 breeze，所以沒跑。這次只是把 `else` 換成 `elif extra_driver:`，沒有型別上的變化
- breeze 的完整 provider 測試套件，CI 會跑

