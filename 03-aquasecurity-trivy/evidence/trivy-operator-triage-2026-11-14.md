# 證據：aquasecurity/trivy-operator starter issue 初篩

- last_verified_at：`2026-11-14T11:15:59Z`
- 範圍：open、沒有 assignee、標 `good first issue` 的 issue，共 2 個
- 結果：2 個都是 `DUPLICATE_OR_IN_PROGRESS`
- 外部 checkout：沒有建立。沒有跑測試，沒有補丁，沒有留言

## #2896

[#2896](https://github.com/aquasecurity/trivy-operator/issues/2896)（Helm 的 `--slow` 與 `--parallel 1`）。兩個 open PR 都有關閉關鍵字指向它：[#2914](https://github.com/aquasecurity/trivy-operator/pull/2914)、[#3024](https://github.com/aquasecurity/trivy-operator/pull/3024)。

## #2736

[#2736](https://github.com/aquasecurity/trivy-operator/issues/2736) 建於 `2025-09-03`，`kind/testing`。回報的是 integration test 通過，但 log 出現 `Reconciler error`：`failed checking current revision: Deployment.apps "alpine-runner-…" not found`。timeline 沒有任何交叉引用。

### main 上的 CI 現況

讀了 Build workflow run `42596607470`（`main`，`689215dd79a7a6115b053ffb262086f3ad401656`，`2026-11-09`）的 `Run integration tests` job log（job `129096647216`）：

- `Ran 13 of 13 Specs`，`SUCCESS! -- 13 Passed`
- `failed checking current revision` 出現 0 次。`alpine-runner` 這個步驟已不存在；現在叫 `Creating Deployment alpine`（`tests/itest/trivy-operator/behavior/behavior.go`，blob `df615a7d98d4ef969f03b222101d9bf52bc374f0`）
- 唯一一行 `"level":"error"` 是 `controller: replicaset` 的 `Reconciler error`：`failed marking old reports for immediate deletion : exposedsecretreports.aquasecurity.github.io "replicaset-alpine-…-alpine" not found`

### 來源

`pkg/operator/workload/helper.go`（`689215d` 版）：`SkipProcessing` 對 inactive ReplicaSet 呼叫 `MarkOldReportForImmediateDeletion`。後者先 List 各種 report，再對每一筆呼叫 `markReportTTL`，最後由它呼叫 `resolver.Client.Update`。List 與 Update 之間 report 被刪掉時，NotFound 會往上傳，被包成 `failed marking old reports for immediate deletion`。2025 年的訊息是同一個函式更早一步（`IsActiveReplicaSet`）的 NotFound。

### 重疊

[#3001](https://github.com/aquasecurity/trivy-operator/pull/3001) `fix: failed marking old reports` 是 open、非 draft 的 PR，作者就是 `#2736` 的作者。它在 `markReportTTL` 加了 `k8sapierror.IsNotFound(err)` 時回傳 nil，正好處理 main 上仍出現的那一行。判定為 `definite_duplicate`：路徑、符號與錯誤訊息都相同。沒有 `Fixes #2736`，`#2736` 的 timeline 也沒有交叉引用。

`#3001` 的 `mergeable_state` 是 `dirty`，沒有 review，`2026-06-17` 之後沒有更新。接手停滯的 PR 要先取得維護者同意，由人決定，代理不做。

相關但不重疊：已合併的 `#3018`（`9e6aa0b1`，處理 report CRD 不存在的情況）；open 的 `#3070`（superseded ReplicaSet 沒有 pod 時標記 report）是 `possible_overlap`，同在 `SkipProcessing`。

## 這次實際下的 GET

`issues?labels=good first issue&assignee=none`、兩個 issue 的 timeline 與內文、`pulls?state=all`、`pulls/2914`、`pulls/3024`、`pulls/3001` 與其 files、reviews、comments、`commits?path=pkg/operator/workload/helper.go`、`actions/workflows`、`actions/workflows/build.yaml/runs`、`actions/runs/42596607470/jobs`、`actions/jobs/129096647216/logs`、`contents/pkg/operator/workload/helper.go?ref=689215d`，以及搜尋 `"marking old reports"`、`IgnoreNotFound`、`markReportTTL`、`"Reconciler error"`、`SkipProcessing`、`2736`。全部 HTTP 成功。
