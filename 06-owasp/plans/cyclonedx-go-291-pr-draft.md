DRAFT

這是給人用的交付檔。代理與 workflow 都不得張貼、推送或開 PR。cyclonedx-go 沒有 PR 模板，組織層的 CONTRIBUTING 也沒有 AI 條款。沒有條款不代表允許代理撰寫，所以 PR 描述由人自己寫，下面只列參考事實。

## 位置

- 外部 checkout：`/Users/dennis/Desktop/upstream-src/CycloneDX/cyclonedx-go`
- 本機分支：`fix-extref-downgrade-291`，base 是 `b3eb7b74d7e1f96758f2fc5d2dec5be3a4b70ae7`
- 改動**尚未 commit**：`convert.go`、`convert_test.go`
- 執行過的命令與結果：`evidence/cyclonedx-go-291.md`

## 建議的 PR 標題（人可改）

```
fix: downgrade external reference types the target spec version does not support
```

## Reference facts (not PR text — write the description yourself)

- **Bug:** `convertExternalReferences` rewrites a type to `other` only when `supportsExternalReferenceType` says the target version lacks it. That function has no case for the 1.6 types `digital-signature`, `electronic-signature`, `rfc-9116` and `source-distribution`, so `EncodeVersion` emits them verbatim into 1.1–1.5 documents, which then fail schema validation (#291).
- **Also covered:** checked against the bundled `schema/` files, the same function also misses `release-notes` (added in 1.4) and `poam` and `security-contact` (added in 1.5). They are the same defect in the same switch, so they are fixed together. The human decides whether to keep this broader scope or narrow it to the four types in the issue.
- **Change:** `convert.go`, `supportsExternalReferenceType` only. 6 added lines.
- **Test added:** `Test_convertExternalReferences_typesNewerThanTargetSpec` checks each of the 7 types for spec 1.1–1.6. It failed 3/3 on unmodified `b3eb7b74` (25 failed assertions) and passes with the change.
- **Commands run:** `go test -race -count=1 ./...`, `go vet ./...`, `golangci-lint run ./...` (v2.15.0, 0 issues).
- **Related:** downstream workarounds in `anchore/syft#5246` and `#5493`.

## 開 PR 前（只有人能做）

1. 讀過 diff。用 `git commit -s` 提交（DCO 要求 `Signed-off-by`）。commit message 自己寫。
2. 決定範圍：要處理全部 7 個類型，還是只處理 issue 寫的 4 個。
3. 要不要揭露 AI 協助、用什麼方式揭露，由人決定。上游沒有規定。
4. PR 描述自己寫，裡面寫 `Fixes #291`。
5. fork、推送、開 PR 都由人操作。
6. 開了 PR 之後，把網址寫回 `06-owasp/candidates.json`，狀態改成 `PR_OPEN`。

注意：這個 repo 從 2026-09-07 之後沒有合併過任何東西，外部 PR 都沒有 review（見 `evidence/recheck-2026-11-17.md`）。
