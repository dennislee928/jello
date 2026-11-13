# 證據：opentelemetry-collector-contrib #52509

- status：`BLOCKED`
- last_verified_at：`2026-11-13T16:55:05Z`
- Go：根目錄與 processor `go.mod` 都是 `go 1.26.0`
- semconv：processor 模組沒有 semantic-conventions require；只有 `pkg/semconvtest v0.165.1`
- HPA 產生符號：`attributes.go` 與 processor `metadata.yaml` 都沒有引用
- `#50908`：`possible_overlap`。檔案清單是 HPA 擷取，不是產生符號遷移
- `#52631`：週報 issue，沒有 PR diff
- Code Owner：名單已讀到，同意未出現

沒有補丁。
