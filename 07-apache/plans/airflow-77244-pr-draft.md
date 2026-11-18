DRAFT

這是給人用的交付檔。代理與 workflow 都不得張貼、推送或開 PR。依本庫規則，PR 描述由人撰寫，所以下面只列事實。

## 位置

- 外部 checkout：`/Users/dennis/Desktop/upstream-src/apache/airflow`
- 本機分支：`fix-odbc-driver-warning-77244`，base 是 `c03582f661`
- 改動**尚未 commit**：
  - `providers/odbc/src/airflow/providers/odbc/hooks/odbc.py`（1 行）
  - `providers/odbc/tests/unit/odbc/hooks/test_odbc.py`（新增 1 個參數化測試）
- 執行過的命令與結果：`evidence/airflow-77244.md`

## 建議的 PR 標題（人可改）

```
Only warn about the ODBC driver in connection extra when one is set
```

## airflow 的規定

- PR 模板有 "Was generative AI tooling used to co-author this PR?"：用了就把方框改成 `[X]`，並取消 `Generated-by: [Tool Name] following [the guidelines](...)` 的註解，填入工具名稱
- `AGENTS.md`：**不得把 agent 列為 commit co-author**，commit 結尾不要加 `Co-authored-by: Claude ...`
- 內文用 `closes: #77244`
- providers 的修正不加 newsfragment
- `05_pull_requests.rst`：作者要讀懂每一行，維護者問起時要能解釋

## Reference facts (not PR text — write the description yourself)

- **Bug:** `OdbcHook.driver` used `if extra_driver and allow_driver_in_extra: ... else: warn`. The `else` branch also ran when the connection extra had no `driver` at all, so users who set the driver through the hook constructor, `hook_params`, or `OdbcHook.default_driver` (as in #77244) always got "You have supplied 'driver' via connection extra but it will not be used".
- **Change:** `else:` becomes `elif extra_driver:`. The warning now fires only when the extra names a driver and `[providers.odbc] allow_driver_in_extra` is off. Nothing else in `driver` changes.
- **Test added:** `test_driver_without_extra_does_not_warn`, parametrized over a driver from `hook_params`, a driver from `default_driver`, and no driver at all. All three failed on unmodified `c03582f661` (the warning text was captured) and pass with the change. The existing `test_driver_extra_raises_warning_by_default` and `test_driver_extra_raises_warning_and_returns_default_driver_by_default` still pass.
- **Commands run:** `uv run --project providers/odbc pytest providers/odbc/tests/unit/odbc/hooks/test_odbc.py` (38 passed), `prek run ruff` and `prek run ruff-format` on the two files (passed). `mypy-providers` was not run (it needs breeze).

## 開 PR 前（只有人能做）

1. 讀過 diff，確定每一行都能解釋
2. 自己寫 commit message，不要加 agent co-author。Apache 不需要 DCO
3. 要不要先在 issue 留言避免撞車，見 `plans/airflow-77244-claim-outline.md`
4. fork、推送、開 PR；模板的 Gen-AI 方框和 `Generated-by` 由人填
5. 開了 PR 之後，把網址寫回 `07-apache/candidates.json`，狀態改成 `PR_OPEN`
