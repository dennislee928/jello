DRAFT

# python-contrib #5353：認領留言要點

只給要點。python-contrib 的 `AGENTS.md` 禁止張貼 AI 撰寫的留言，所以這裡沒有可以直接貼的文字。留言由人自己寫，代理不張貼。

## 現況

- `dennislee928` 已在 `2026-11-18T15:00:15Z` 留言認領，請維護者指派或同意，並說明打算把兩處的 `str(value.args[0])` 改成 `str(exc)`
- `2026-11-19T10:30:10Z` 維護者 `xrmx` 回覆：先開 logging 的 PR，合併後再做 structlog；issue 已指派給 `dennislee928`。問題 1（拆不拆 PR）已有答案：拆
- `AGENTS.md` 要求實作方向先在 issue 上談定，所以在維護者回覆前不送 PR

## 維護者回覆後，追加留言可以涵蓋的事實

- 重現結果：等 Phase 4 跑完再填，包括 `OSError(2, "No such file or directory")` 修改前後的 `exception.message`
- 範圍：
  - `instrumentation/opentelemetry-instrumentation-logging/.../handler.py`：`LoggingHandler._get_attributes`
  - `instrumentation/opentelemetry-instrumentation-structlog/.../__init__.py`：`StructlogProcessor._get_attributes`
  - SDK 那個已 deprecated 的 `LoggingHandler` 在 `opentelemetry-python`，不在這個 repo，不放進這次的 PR
- 對齊依據：`Span.record_exception` 用的是 `str(exception)`

## 要問維護者的問題

1. 兩個套件合在一個 PR，還是拆成兩個？`AGENTS.md` 規定一個 PR 只做一件邏輯變更。這兩處是同一個 bug，但屬於兩個套件
2. `ValueError()` 這種沒有參數的例外，`str(exc)` 會是空字串。要照 span 的做法寫入空字串，還是像現在一樣不寫這個屬性？
3. opentelemetry-python 的 SDK handler 要不要另開 issue 或 PR？

## 不要做的事

- 不要貼這份檔案的內容，也不要貼 AI 整理的分析
- 維護者回覆之前，不送 PR
