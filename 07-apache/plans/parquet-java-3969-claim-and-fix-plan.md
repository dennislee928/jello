DRAFT

# parquet-java #3969：認領要求與備援修復計畫

- verified_at：`2026-11-18`（`gh api` GET）
- 判定：`DUPLICATE_OR_IN_PROGRESS`（回報者已開 PR），**不留言認領**

## 認領要求（issue 與規則）

- 回報者 `zhangxinyao88` 已開 PR `#3866`，標題是 "GH-3969: Fix leading CLI --conf properties being consumed by Hadoop"。仍是 open、不是 draft，`2026-11-18` 有更新；改了 3 個檔案，+235/−4：
  - `parquet-cli/src/main/java/org/apache/parquet/cli/Main.java`
  - `parquet-cli/src/test/java/org/apache/parquet/cli/CliTestBase.java`
  - `parquet-cli/src/test/java/org/apache/parquet/cli/ConfigurationCliTest.java`
- issue 內文本身就提到 PR `#3866` 帶了回歸測試，以及更大範圍的 CLI 測試由 `#3289` 追蹤
- `AGENTS.md`（blob `1c6841a0`）是給 agent 的參考文件；PR 標題慣例用 `GH-<issue>:`

## 留言要點

- **不留言認領**，修復已經在 PR 裡了
- 能做的事：由人去 review `#3866`，例如在本機跑它的 `ConfigurationCliTest`、確認 `--conf` 會覆蓋 `--config-file`。review 留言由人寫
- 如果想貢獻 parquet-java，可以從 `#3289`（擴大 CLI 測試覆蓋）切出一個不重疊的小項目，先在那個 issue 上問

## 備援修復計畫（只在 #3866 被關掉時才用）

- 根因：Hadoop 的 `GenericOptionsParser` 在 Parquet 的參數解析器拿到參數之前，就先吃掉了開頭的 `--conf`，所以使用者明確指定的屬性沒有蓋過 `writer.properties`
- 修法方向：在 `Main.java` 把 `--conf` 交給 Hadoop 之前，先保留下來，並在讀完 `--config-file` 之後才套用，讓明確指定的屬性優先。細節以 `#3866` 的審查結果為準，不另起爐灶
- 測試：照 issue 的步驟寫。Avro 檔有一個 `uuid` 邏輯型別的 string 欄位，`writer.properties` 設 `parquet.avro.write-parquet-uuid=false`，CLI 帶 `--conf parquet.avro.write-parquet-uuid=true`，斷言輸出的 schema 是 `FIXED_LEN_BYTE_ARRAY` 的 UUID
- 命令：`mvn -pl parquet-cli -am test -Dtest=ConfigurationCliTest`

## 接手時的認領留言要點（只在條件成立時用，由人撰寫）

使用條件：`#3866` 被關閉且沒有合併，作者也沒有再開新 PR。條件不成立時不要留，改去 review `#3866`。

1. 開頭說明 `#3866` 已關閉（附連結與關閉原因），想接手這件
2. 根因一句話：Hadoop 的 `GenericOptionsParser` 在 Parquet 的參數解析之前就吃掉了開頭的 `--conf`，所以明確指定的屬性沒有蓋過 `--config-file`
3. 預計做法：沿用 `#3866` 被 review 認可的部分；若它被關是因為做法問題，先問維護者偏好的方向
4. 測試：照 issue 的 UUID 步驟寫 CLI 測試，斷言 schema 是 `FIXED_LEN_BYTE_ARRAY` 的 UUID
5. PR 標題用 `GH-3969:` 開頭
