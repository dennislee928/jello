# 證據：open-telemetry/opentelemetry-python-contrib #5353

- status：`PR_OPEN`（[#5357](https://github.com/open-telemetry/opentelemetry-python-contrib/pull/5357)，只做 logging）
- last_verified_at：`2026-11-19T12:48:30Z`
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-python-contrib`（`git clone --filter=blob:none`）
- base：`main` `ced050a9`（`2026-11-19` 從 `7a554d4e` rebase 過來）
- 本機分支：`fix-exception-message-5353`。改動未 commit：`handler.py`、`test_handler.py`、`.changelog/5353.fixed`
- remote：只有 `origin`（上游）。沒有 fork，沒有推送；上游留言只有 `dennislee928` 自己寫的認領留言
- 工具鏈：`uv 0.12.10`、`uvx --with tox-uv tox`、Python 3.12
- 計畫：`plans/python-contrib-5353-fix-plan.md`；留言要點：`plans/python-contrib-5353-claim-outline.md`

## 狀態轉移

| 時間（UTC） | 狀態 | 依據 |
| --- | --- | --- |
| `2026-11-18T16:00:05Z` | `DISCOVERED` | timeline 沒有事件，沒有提到 #5353 的 PR；人在 `15:00:15Z` 留言認領 |
| `2026-11-18T16:40:00Z` | `REPRODUCED` | 新測試在未修改的 `7a554d4e` 上，兩個套件各連跑 3 次都失敗 |
| `2026-11-19T10:30:10Z` | `READY_TO_IMPLEMENT` | 維護者 `xrmx`：「please open a PR for logging instrumentaton first and once merged go with the structlog one」；issue 指派給 `dennislee928` |
| `2026-11-19T12:48:30Z` | `READY_FOR_HUMAN_PR` | logging 的修改後測試、lint、ruff、typecheck、towncrier 預覽都通過；交給人 |
| `2026-11-19T13:10:51Z` | `PR_OPEN` | 人開了 #5357（head `643d9ab8`，作者 `dennislee928`）。changelog fragment 仍是 `5353.fixed`，要改成 `5357.fixed` |

硬門檻：維護者已在 issue 上同意，並指定先做 logging、合併後再做 structlog。structlog 的測試改動已經從這個分支拿掉，留待下一個 PR。

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

## 修改（只做 logging）

- `instrumentation/opentelemetry-instrumentation-logging/src/opentelemetry/instrumentation/logging/handler.py`：`LoggingHandler._get_attributes` 裡的 `str(value.args[0])` 換成 `str(value)`，保留 `value.args` 的 guard（`ValueError()` 仍然不寫這個屬性）
- `tests/test_handler.py`：
  - 新增 `test_log_record_exception_message_uses_str_of_exception`
  - **修改既有的 `test_log_record_exception_with_object_payload`**：這個例外自訂了 `__str__`，原本斷言 `exception.message == "CustomException message"`（第一個參數），現在改成 `"CustomException stringified"`，也就是 `Span.record_exception` 會給的值。這是刻意的行為變更，PR 描述要提
- `.changelog/5353.fixed`：towncrier 要求檔名整個是數字，暫時用 issue 編號占位，**開 PR 後要改成 PR 編號**

第一次跑完整測試時，上面那個既有測試失敗（`'CustomException stringified' != 'CustomException message'`），因此找到這個要一起改的斷言。

## 修改後

```
$ uvx --with tox-uv tox -e py312-test-instrumentation-logging      # 3 次
85 passed, 3 warnings, 2 subtests passed
$ uvx --with tox-uv tox -e lint-instrumentation-logging
congratulations :)
$ uvx ruff check <兩個檔案>              All checks passed!
$ uvx ruff format --check <兩個檔案>     2 files already formatted
$ uvx --with tox-uv tox -e typecheck      typecheck: OK
$ uvx towncrier build --draft --version Unreleased
- `opentelemetry-instrumentation-logging`: report `str(exception)` as
  `exception.message` instead of its first argument ([#5353](...))   # 開 PR 後改成 PR 編號
```

## 下一步

- 人讀 diff、寫 PR 描述（模板各節由人寫，自己勾 Authorship）、fork、推送、開 PR
- logging 的 PR 合併後，再用同樣做法處理 structlog（測試寫法見本檔「重現」一節）
