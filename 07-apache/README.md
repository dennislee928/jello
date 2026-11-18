# Apache（Superset 以外）

`01-apache-superset/` 只放 Superset。其他 Apache repo 的候選、證據與計畫放在這裡。上游規則見 `upstream-requirements.md`，外部 checkout 在 `/Users/dennis/Desktop/upstream-src/apache/<repo>`。

| repo | 候選 | 狀態 |
| --- | --- | --- |
| `apache/iceberg-go` | `#2425` dictionary 欄位的 row filter 失敗 | `DUPLICATE_OR_IN_PROGRESS`：main 已因 arrow-go v18.9.0（`#2632`）修好，見 `evidence/iceberg-go-2425.md` |
| `apache/airflow` | `#77244` OdbcHook driver 警告條件寫反 | `READY_FOR_HUMAN_PR`：一行修正加測試，交付檔 `plans/airflow-77244-pr-draft.md` |

篩選過程與排除原因：`evidence/replacement-selection-2026-11-18.md`。
