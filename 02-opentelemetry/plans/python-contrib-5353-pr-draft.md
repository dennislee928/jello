DRAFT

這是給人用的交付檔。代理與 workflow 都不得張貼、推送或開 PR。python-contrib 的 `AGENTS.md` 規定 PR 描述照模板寫、要簡短，而且不得張貼 AI 撰寫的留言。所以模板各節**留空**，由人自己寫；下面只列參考事實。

## 位置

- 外部 checkout：`/Users/dennis/Desktop/upstream-src/open-telemetry/opentelemetry-python-contrib`
- 本機分支：`fix-exception-message-5353`，base 是 `ced050a9`
- 改動**尚未 commit**：
  - `instrumentation/opentelemetry-instrumentation-logging/src/opentelemetry/instrumentation/logging/handler.py`（1 行）
  - `instrumentation/opentelemetry-instrumentation-logging/tests/test_handler.py`（新增 1 個測試，修改 1 個既有斷言）
  - `.changelog/5353.fixed`（新檔，**開 PR 後改名成 `<PR 編號>.fixed`**）
- 範圍：只有 logging。維護者 `xrmx` 要求 structlog 等這個 PR 合併後另開
- 執行過的命令與結果：`evidence/opentelemetry-python-contrib-5353.md`

## 建議的 PR 標題（人可改）

```
opentelemetry-instrumentation-logging: use str(exception) for exception.message
```

## PR 模板（上游原文，各節由人填寫）

```markdown
# Description

Fixes #5353

## Type of change

- [ ] Bug fix (non-breaking change which fixes an issue)

# Checklist:

- [ ] I am a human and not a bot
- [ ] I have run `tox -e precommit`
- [ ] I have run `tox -e typecheck`
- [ ] I have run the relevant tests and linting tox environments
- [ ] This requires the following PR in core:
```

勾選框只能由人勾。代理已經跑過 precommit、typecheck、測試與 lint，結果都通過（見 evidence）。人要勾之前，最好自己再跑一次。

## Reference facts (not PR text — write the description yourself)

- **Bug:** `LoggingHandler._get_attributes` set `exception.message` to `str(value.args[0])`. When the message is not the first argument, the log attribute is wrong and disagrees with `Span.record_exception`, which uses `str(exception)`. Example: `OSError(2, "No such file or directory")` was exported as `2`.
- **Change:** `str(value.args[0])` becomes `str(value)`. The `value.args` guard stays, so an exception with no args (for example `ValueError()`) still sets no `exception.message`, as before.
- **Behavior change to call out:** the existing `test_log_record_exception_with_object_payload` uses an exception with a custom `__str__` and asserted the first argument (`"CustomException message"`). It now expects `"CustomException stringified"`, which is what spans report.
- **Test added:** `test_log_record_exception_message_uses_str_of_exception`, with subtests for `OSError(2, "No such file or directory")` and `ValueError("bad value", 42)`. It failed 3/3 on unmodified `main` and passes with the change.
- **Scope:** logging only, as the maintainer asked on the issue. The structlog processor has the same expression and will follow in a separate PR.
- **Commands run:** `tox -e py312-test-instrumentation-logging` (85 passed), `tox -e lint-instrumentation-logging`, `tox -e typecheck`, `tox -e precommit` (all passed), and a `towncrier build --draft` preview of the fragment.

## 開 PR 前（只有人能做）

1. 讀過 diff，每一行都要能解釋
2. 自己寫 commit message。OTel 的 EasyCLA 不接受 `Co-authored-by:` 掛 AI；要揭露的話，用 `Assisted-by:`（和 collector-contrib `#53246` 的做法相同）
3. 照模板自己寫描述、自己勾 checklist；CLA 已在 `#53246` 簽過
4. fork、推送、開 PR，然後把 `.changelog/5353.fixed` 改名成 `<PR 編號>.fixed`，再推一次
5. 開了 PR 之後，把網址寫回 `02-opentelemetry/candidates.json`，狀態改 `PR_OPEN`
6. 這個 PR 合併後，再開 structlog 的 PR
