# Trivy 家族上游規則

四個儲存庫各自驗證。`trivy-action` 的需求不要改送到 `setup-trivy`，也不要反向。外部 checkout 根目錄是 `/Users/dennis/Desktop/upstream-src/aquasecurity/`。本協調庫不執行 `mage` 或 Action 測試。

## aquasecurity/trivy

根目錄 `CONTRIBUTING.md` 只指向 [Issues](https://trivy.dev/docs/latest/community/contribute/issue/) 與 [Pull Requests](https://trivy.dev/docs/latest/community/contribute/pr/)。非維護者開的 issue 會被立刻關閉。先開 GitHub Discussion，由維護者建立 issue。PR 要連結該 issue。先查 open PR 再考慮認領；認領留言不在本協調庫的授權內。

驗證命令以文件為準：`mage build`、`mage lint:run`、`mage tidy`、`mage test:unit`，適用時 `mage test:integration`。標題格式 `type(scope): subject`。這些命令只在外部 checkout 對過文件後才跑。

已知碰撞（含 closed-unmerged）維持 `DUPLICATE_OR_IN_PROGRESS`，只當去重 fixture：`#11482`、`#11573`、`#11523`、`#11627`、`#11576`、`#11575`、`#11602`、`#11633`、`#11428`。issue `#11502` 與 `#11568` 是沒有 `Fixes #ID` 時仍要能判成 `definite_duplicate` 的對照。新候選另外排除已有人處理的 `#11383`、`#11411`、`#11389`、`#11447`。

## aquasecurity/trivy-action

根目錄沒有 `CONTRIBUTING.md`。表面檔是 `Makefile`、`entrypoint.sh`、`action.yaml`。`#521` 是已知碰撞。`#551` 維持 `NEEDS_MAINTAINER`，只比較下載路徑與 `setup-trivy` 的 `#40`、`#43`。設計維度是版本釘選、SHA-256、簽章、快取、架構、發布流程，以及功能該落在哪個儲存庫。

## aquasecurity/setup-trivy

根目錄沒有 `CONTRIBUTING.md`，主要檔是 `action.yaml`。`#40` 與 `#43` 是對照，不是把 `#551` 搬過來的理由。關係在讀完兩邊的下載路徑之前標 `possible_overlap` 或保持未確認，不標成同一個修復。

## aquasecurity/trivy-db

根目錄沒有 `CONTRIBUTING.md`。表面檔是 `go.mod` 與 `Makefile`。`#702` 維持 `DUPLICATE_OR_IN_PROGRESS`。資料庫的發布流程不拿去解釋 Action 的安裝路徑。

## 本次驗證

last_verified_at: null

<!-- policy-shas:start -->
尚未以 `gh api` 重抓四個儲存庫的政策檔或表面檔 blob SHA。
<!-- policy-shas:end -->

## 新候選怎麼找

優先看 Discussion，以及維護者建立的 issue。排除上一節全部碰撞編號，再加上 `#11383`、`#11411`、`#11389`、`#11447`。新編號要走完整 G0–G4。這個 phase 不實作新修復。
