DRAFT

這是給人用的交付檔。代理與 workflow 都不得張貼、推送或開 PR。PR 描述由人自己寫，下面只列參考事實。

## 位置

- 外部 worktree：`/Users/dennis/Desktop/upstream-src/CycloneDX/cyclonedx-go-281`
- 本機分支：`fix-escape-html-281`，base 是 `b3eb7b74d7e1f96758f2fc5d2dec5be3a4b70ae7`
- 改動**尚未 commit**：`cyclonedx_json.go`、`encode_test.go`
- 執行過的命令與結果：`evidence/cyclonedx-go-281.md`

## 建議的 PR 標題（人可改）

```
fix: honor SetEscapeHTML(false) in custom JSON marshalers
```

## Reference facts (not PR text — write the description yourself)

- **Bug:** the custom `MarshalJSON` methods in `cyclonedx_json.go` call `json.Marshal`, which always escapes `<`, `>` and `&`. The outer `json.Encoder` only adds escaping to a `Marshaler`'s output and never removes it, so `SetEscapeHTML(false)` has no effect on tools, licenses, environment variables, ML datasets, certificates, IKEv2, patents, and other fields written by these methods (#281).
- **Change:** a new unexported helper, `marshalJSON`, encodes with `SetEscapeHTML(false)` and trims the trailing newline. All 21 `json.Marshal` calls in `cyclonedx_json.go` use it. The outer encoder still applies the caller's setting, so the default output (`SetEscapeHTML(true)`) does not change, and neither does a direct `json.Marshal(bom)`.
- **Test added:** `TestJsonBOMEncoder_SetEscapeHTML_customMarshalers` encodes a tool component name and a license name, both with and without escaping. The `no escape` case failed 3/3 on unmodified `b3eb7b74`. The `escape` case passed before the change and still passes; it pins the default behaviour.
- **Commands run:** `go test -race -count=1 ./...`, `go test -count=5 -run TestJsonBOMEncoder ./`, `go vet ./...`, `golangci-lint run ./...` (0 issues).
- **Related:** reported downstream in `interlynk-io/sbomasm#337`; workaround in `interlynk-io/sbomasm#340`.

## 開 PR 前（只有人能做）

1. 讀過 diff。用 `git commit -s` 提交，commit message 自己寫。
2. 要不要揭露 AI 協助、用什麼方式揭露，由人決定。
3. PR 描述自己寫，裡面寫 `Fixes #281`。
4. fork、推送、開 PR 都由人操作。
5. 開了 PR 之後，把網址寫回 `06-owasp/candidates.json`，狀態改成 `PR_OPEN`。

和 #291 是兩個獨立的 PR（上游規則是一個 issue 一個 bug），兩者改的檔案不重疊。
