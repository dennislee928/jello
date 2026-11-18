# Apache（Superset 以外）

`01-apache-superset/` 只放 Superset。其他 Apache repo 的候選、證據與計畫放在這裡。上游規則見 `upstream-requirements.md`，外部 checkout 在 `/Users/dennis/Desktop/upstream-src/apache/<repo>`。

| repo | 候選 | 狀態 |
| --- | --- | --- |
| `apache/iceberg-go` | `#2425` dictionary 欄位的 row filter 失敗 | `DISCOVERED`：要先由人認領並等維護者回應；新貢獻者一次只做一件 |
| `apache/airflow` | `#77244` OdbcHook driver 警告條件寫反 | `DISCOVERED`：bot 表示不用等核准；PR 要揭露 Gen-AI 協助 |

篩選過程與排除原因：`evidence/replacement-selection-2026-11-18.md`。
