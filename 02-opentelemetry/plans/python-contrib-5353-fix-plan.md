# python-contrib #5353：修復計畫

- base：`main` `7a554d4e`（`2026-11-18`）
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-python-contrib`
- 前提：維護者在 issue 上同意方向，之後才送 PR（`AGENTS.md`）。本機可以先重現、先準備

## 根因

兩處都用 `str(value.args[0])` 當作 `exception.message`：

| 檔案 | 位置 |
| --- | --- |
| `instrumentation/opentelemetry-instrumentation-logging/src/opentelemetry/instrumentation/logging/handler.py` | `LoggingHandler._get_attributes`，第 181 行 |
| `instrumentation/opentelemetry-instrumentation-structlog/src/opentelemetry/instrumentation/structlog/__init__.py` | `StructlogProcessor._get_attributes`，第 182 行 |

`Span.record_exception` 用的是 `str(exception)`。例外的訊息不在第一個參數時，log 和 span 的值就會不一致，例如 `OSError(2, "...")` 在 log 上會變成 `2`。

## 改動

- 兩處都把 `str(value.args[0])` 換成 `str(value)`
- 保留原本的 guard `if value is not None and value.args:`。所以 `ValueError()` 這種沒有參數的例外，仍然不寫入這個屬性，行為不變。要不要改成跟 span 一樣寫入空字串，留給維護者決定（見 claim-outline 的問題 2）
- 不碰 `exception.type` 與 `exception.stacktrace`

## 回歸測試

| 套件 | 檔案 | 新測試 |
| --- | --- | --- |
| logging | `tests/test_handler.py` | `OSError(2, "No such file or directory")` → `exception.message == "[Errno 2] No such file or directory"`；`ValueError("bad value", 42)` → `"('bad value', 42)"` |
| structlog | `tests/test_structlog.py` | 同樣的兩個例子，走 `exc_info=True` 的路徑 |

既有測試用的是單一參數的例外（`"test error"`、`"division by zero"`），換成 `str(value)` 後結果一樣，應該都會繼續通過。

## changelog

- 新增 `.changelog/<PR 編號>.fixed`，一行，以套件名開頭。PR 編號要等開了 PR 才知道，由人建立
- 兩個套件合在一個 PR 的話，用兩個 fragment，或一行同時列出兩個套件；依維護者的回覆決定

## 命令

```sh
uv sync --frozen --all-packages
uv run tox -e py312-test-instrumentation-logging
uv run tox -e py312-test-instrumentation-structlog-latest
uv run tox -e lint-instrumentation-logging
uv run tox -e lint-instrumentation-structlog
uv run pre-commit run ruff --all-files
```

## 風險與待決事項

- 範圍：`AGENTS.md` 規定一個 PR 只做一件邏輯變更，兩個套件可能要拆成兩個 PR
- 依賴這個屬性值的使用者：`OSError` 類例外的 `exception.message` 會改變。這是在修 bug，但屬於行為變更，changelog 要寫清楚
- 不改 `opentelemetry-python` 的 SDK handler
