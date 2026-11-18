# 證據：open-telemetry/opentelemetry-python-contrib #5353

- status：`REPRODUCED`
- last_verified_at：`2026-11-18T16:40:00Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-python-contrib`（`git clone --filter=blob:none`）
- base：`main` `7a554d4e`
- 本機分支：`fix-exception-message-5353`。只加了測試，**沒有改產品程式碼**，也沒有 commit
- remote：只有 `origin`（上游）。沒有 fork，沒有推送；上游留言只有 `dennislee928` 自己寫的認領留言
- 工具鏈：`uv 0.12.10`、`uvx --with tox-uv tox`、Python 3.12
- 計畫：`plans/python-contrib-5353-fix-plan.md`；留言要點：`plans/python-contrib-5353-claim-outline.md`

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-18T16:00:05Z` | `DISCOVERED` | timeline 沒有事件，沒有提到 #5353 的 PR；人在 `15:00:15Z` 留言認領 |
| `2026-11-18T16:40:00Z` | `REPRODUCED` | 新測試在未修改的 `7a554d4e` 上，兩個套件各連跑 3 次都失敗 |

硬門檻：「需要維護者」仍然沒過。python-contrib 的 `AGENTS.md` 要求實作方向先在 issue 上談定，但維護者還沒回覆。所以不進 `READY_TO_IMPLEMENT`，也還沒有實作修復。

## 基線（未修改的程式碼）

```
$ uvx --with tox-uv tox -e py312-test-instrumentation-logging
84 passed, 3 warnings
$ uvx --with tox-uv tox -e py312-test-instrumentation-structlog-latest
36 passed
```

## 重現（只加測試，連跑 3 次）

新增的測試：

- `instrumentation/opentelemetry-instrumentation-logging/tests/test_handler.py`：`test_log_record_exception_message_uses_str_of_exception`
- `instrumentation/opentelemetry-instrumentation-structlog/tests/test_structlog.py`：`test_exception_message_uses_str_of_exception`

兩個測試都用 subTest 跑兩個例子：`OSError(2, "No such file or directory")` 與 `ValueError("bad value", 42)`。

```
$ uvx --with tox-uv tox -e py312-test-instrumentation-logging -- -k exception_message_uses_str
E   AssertionError: '2' != '[Errno 2] No such file or directory'
E   AssertionError: 'bad value' != "('bad value', 42)"
2 failed, 1 passed, 84 deselected          # 3 次都一樣；1 passed 是 subTest 外層的父測試

$ uvx --with tox-uv tox -e py312-test-instrumentation-structlog-latest -- -k exception_message_uses_str
E   AssertionError: '2' != '[Errno 2] No such file or directory'
E   AssertionError: 'bad value' != "('bad value', 42)"
2 failed, 1 passed, 36 deselected          # 3 次都一樣
```

結果和 issue 的表格一致：log 的 `exception.message` 是 `str(value.args[0])`，不是 `str(exc)`。

## 下一步

- 等維護者在 issue 上回覆方向，以及 claim-outline 裡的三個問題
- 回覆後才把 fix-plan 的改動套到兩處，再跑 fix-plan 列的 tox、lint、ruff，並補 changelog fragment
