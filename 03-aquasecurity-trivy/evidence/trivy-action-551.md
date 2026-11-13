# 證據：aquasecurity/trivy-action #551

- status：`NEEDS_MAINTAINER`
- last_verified_at：`2026-11-13T16:55:05Z`
- 下載不在 `entrypoint.sh`。安裝在 `setup-trivy`
- version：由 action input 傳給 setup-trivy
- sha256：`main` 的安裝腳本路徑沒有；`#40` 與 `#43` 的 diff 才加上 checksums 檔
- 簽章：這次抽樣沒有看到
- cache：二進位 cache key 含 version、OS、arch；`latest` 不快取。DB cache 在 trivy-action，另算
- 架構：`#40` / `#43` 有 Linux ARM64 對照
- 發布流程：未在這次 diff 裡確認
- 歸屬：功能應落在 `setup-trivy`，除非維護者另有決定
- overlap：`#40` 與 `#43` 都是 `possible_overlap`，`fixes_reference` 為 false

沒有實作。
