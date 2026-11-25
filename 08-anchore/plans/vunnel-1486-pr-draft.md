DRAFT

這是給人用的交付檔。代理與 workflow 都不得張貼、推送或開 PR。PR 描述由人自己寫，下面只列參考事實。

## 位置

- 外部 checkout：`/Users/dennis/Desktop/upstream-src/anchore/vunnel`
- 本機分支：`fix/secureos-apk-suffix-ordering`，base 是 `cb2347dfa2a80f0c12dfb8ca3e0e5f70098d15b7`
- 改動**尚未 commit**：`src/vunnel/providers/secureos/parser.py`、`tests/unit/providers/secureos/test_secureos.py`
- 執行過的命令與結果：`evidence/vunnel-1486.md`

## 建議的 PR 標題（人可改）

```
fix(secureos): order APK versions with _p/_rc suffixes per apk rules
```

## Reference facts (not PR text — write the description yourself)

- **Bug:** `_parse_apk_version` leaves segments such as `10_p1` or `0_rc1` as strings, and `_compare_apk_versions` then compares them lexicographically. So `1.10_p1-r1` sorts before `1.2_p1-r1`, and `2.0.0-r1` before `2.0.0_rc1-r1`. The newer fix lands first in `FixedIn` without a `VulnerableRange`, and Grype DB then emits `< newer_fix` (#1486).
- **Change:** a new static method, `_apk_version_key`, parses `digits{.digits}[letter]{_suffix[N]}` into (ints, letter, [(rank, N)]), with the suffix rank `_alpha < _beta < _pre < _rc < (none) < _cvs < _svn < _git < _hg < _p`. `_compare_apk_versions` compares those keys, then `-rN`. Versions outside that grammar fall back to the previous segment-by-segment comparison. `_parse_apk_version` and `_get_base_version_with_r0` are unchanged, and so is the `(parts, revision)` shape that `_normalize` uses.
- **Tests added:** `test_compare_apk_versions` (19 parametrized pairs, including plain versions, `1.2_p1 < 1.10_p1`, `3.3.2_p1-r4 < 3.3.10-r1`, `_rc < release`, `_alpha < _beta < _pre < _rc`, `_p` ordering, and letter suffixes) and `test_normalize_orders_apk_suffixed_fix_versions` (the issue's repro, asserting the FixedIn order and VulnerableRange). On the unmodified base, 7 of them fail. The existing snapshot and schema tests pass unchanged.
- **Commands run:** `make unit` (1518 passed), `make static-analysis` (ruff, mypy clean), `ruff format --check` on parser.py.
- **Not covered:** apk `~hash` suffixes and the leading-zero "fractional" rule for later segments. Those inputs take the old fallback path.

## 開 PR 前（只有人能做）

1. 讀過 diff（`git -C /Users/dennis/Desktop/upstream-src/anchore/vunnel diff`）。
2. 在該 checkout 設好真實的 `user.name`（目前是玩笑名字），再用 `git commit -s` 提交（vunnel 要求 DCO），commit message 自己寫。
3. 要不要揭露 AI 協助、用什麼方式揭露，由人決定。
4. 自己 fork、推送、開 PR，PR 描述自己寫，裡面寫 `Fixes #1486`。
5. 開 PR 後，把 `08-anchore/candidates.json` 改成 `PR_OPEN`，附上 PR URL 與時間戳。
