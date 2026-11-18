DRAFT

# airflow #77244：留言要點

依本庫規則，留言由人撰寫，代理不張貼，所以這裡只列要點。這件不需要先等核准：`boring-cyborg[bot]` 已經回覆 "If you are willing to raise PR to address this issue please do so, no need to wait for approval"。留言是為了避免撞車，可以留，也可以不留。

## 留言要涵蓋的事實（如果要留）

- 會開 PR 修這件
- 確認回報者的判斷：`providers/odbc/src/airflow/providers/odbc/hooks/odbc.py` 的 `OdbcHook.driver` 用 `if extra_driver and conf.getboolean("providers.odbc", "allow_driver_in_extra", ...)` 分流，`else` 分支會發出警告。所以連線 extra **沒有** `driver` 時（`extra_driver is None`）也會跳出 "You have supplied 'driver' via connection extra but it will not be used"
- 預計修法：只在「extra 有 `driver`，但 `allow_driver_in_extra` 沒開」時才警告
- 重現與測試：等 Phase 4 跑完再填，只寫實際跑過的結果

## 要確認的事

- 已經有警告相關的既有測試嗎？在 `providers/odbc/tests/` 裡找，修改時要一起更新
- 依 airflow 規則，PR 描述要聲明使用了 Gen-AI 協助；commit 不能列 agent 為 co-author

## 不要做的事

- 不要夾帶 `OdbcHook` 其他地方的清理
- providers 的修正不加 newsfragment
