# 證據：aquasecurity/setup-trivy #43

- status：`CLOSED`
- last_verified_at：`2026-11-13T16:55:05Z`
- github_state：closed unmerged
- 變更：只動 `action.yaml`
- 內容：release archive 與 checksum，用來避開 `get.trivy.dev` 的 curl 失敗
- 抽樣沒有簽章
- 對 `trivy-action#551`：`possible_overlap`，`fixes_reference` false
- `main` 仍走 `contrib/install.sh`，這份 PR 不是已合併的安裝方式
