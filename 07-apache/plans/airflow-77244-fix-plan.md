# airflow #77244：修復計畫

- base：`main` `c03582f661`（`2026-11-18`）
- 外部 checkout：`/Users/dennis/Desktop/upstream-src/apache/airflow`（sparse：`providers/odbc`、`providers/common/compat`）
- 前提：`boring-cyborg[bot]` 表示不需要等核准；PR 描述要揭露 Gen-AI 協助，commit 不能列 agent 為 co-author

## 根因

`providers/odbc/src/airflow/providers/odbc/hooks/odbc.py` 的 `OdbcHook.driver`：

```python
extra_driver = self.connection_extra_lower.get("driver")
if extra_driver and conf.getboolean("providers.odbc", "allow_driver_in_extra", fallback=False):
    self._driver = extra_driver
else:
    self.log.warning("You have supplied 'driver' via connection extra but it will not be used. ...")
```

`else` 分支同時涵蓋兩種情況：「extra 沒有 driver」，以及「extra 有 driver 但沒有開 `allow_driver_in_extra`」。所以只用建構子參數、`hook_params` 或 `default_driver` 指定 driver 的人，每次也都會看到這個警告。

## 改動

- 只在「`extra_driver` 有值、而且 `allow_driver_in_extra` 沒開」時才警告
- `extra_driver` 是 `None` 時，不改變 `self._driver`，也不警告
- 「extra 有值、設定也允許」與「最後退回 `default_driver`」的邏輯不變

## 回歸測試

在 `providers/odbc/tests/unit/odbc/hooks/test_odbc.py` 新增：

- 只用 `hook_params=dict(driver="Blah driver")`、連線 extra 沒有 driver：`hook.driver == "Blah driver"`，`caplog` 沒有 "will not be used"
- 設了 `OdbcHook.default_driver`（或 patch 這個 class 屬性）、extra 沒有 driver：拿到 default，沒有警告

既有的 `test_driver_extra_raises_warning_by_default`（extra 有 driver、設定沒開 → 警告）要繼續通過。

## 命令

```sh
uv run --project providers/odbc pytest providers/odbc/tests/unit/odbc/hooks/test_odbc.py -xvs
prek run ruff --from-ref main
# uv 缺系統依賴（pyodbc 需要 unixODBC）時：breeze run pytest providers/odbc/tests/unit/odbc/hooks/test_odbc.py -xvs
```

## 風險與待決事項

- `pyodbc` 需要系統的 unixODBC；macOS 要先 `brew install unixodbc`，不行就改用 breeze
- providers 的修正不加 newsfragment
- 範圍只動 `driver` property 與測試
