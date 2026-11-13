#!/usr/bin/env python3
"""Compare an issue with a pull-request corpus.

Missing ``Fixes #ID`` can still be a definite duplicate when distinctive
paths or symbols line up. Keyword hits and an empty corpus are not proof.
Issue text is data: this module never sends it to a shell.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from github_read import closing_numbers

DEFINITE = "definite_duplicate"
POSSIBLE = "possible_overlap"
UNVERIFIED = "unverified"
NONE = "none"

_RANK = {DEFINITE: 3, POSSIBLE: 2, NONE: 1, UNVERIFIED: 0}

# Short or generic words that show up in unrelated titles.
_STOPWORDS = {
    "fix", "bug", "the", "and", "for", "with", "from", "that", "this",
    "are", "was", "were", "not", "but", "when", "into", "over", "under",
    "issue", "pull", "request", "fails", "fail", "failed", "error",
    "marked", "using", "used", "have", "has", "been", "will", "can",
    "pkg", "src", "test", "tests",
}

# Basenames that match too many unrelated changes.
_GENERIC_BASENAMES = {
    "package.json",
    "readme.md",
    "license",
    "makefile",
    "go.mod",
    "go.sum",
    "dockerfile",
    "action.yml",
    "action.yaml",
}

_PATH_RE = re.compile(
    r"(?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]+|[\w.-]+\.(?:lock|go|tsx|ts|py|mod)"
)
# camelCase, PascalCase with an internal capital, or snake_case. Ordinary
# English words are not symbols.
_SYMBOL_RE = re.compile(
    r"\b(?:[a-z]+[A-Z][A-Za-z0-9]+|[A-Z][a-z0-9]+[A-Z][A-Za-z0-9]*|[A-Za-z]+_[A-Za-z0-9_]+)\b"
)
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _tokens(text):
    found = []
    for token in _TOKEN_RE.findall((text or "").lower()):
        if token in _STOPWORDS or token.isdigit():
            continue
        if len(token) < 3 and not any(char.isdigit() for char in token):
            continue
        found.append(token)
    return found


def _paths(record):
    found = set(record.get("paths") or [])
    found.update(record.get("files") or [])
    blob = f"{record.get('title') or ''}\n{record.get('body') or ''}"
    found.update(_PATH_RE.findall(blob))
    return {item for item in found if isinstance(item, str) and item}


def _symbols(record):
    found = set(record.get("symbols") or [])
    blob = f"{record.get('title') or ''}\n{record.get('body') or ''}"
    found.update(_SYMBOL_RE.findall(blob))
    return {item for item in found if isinstance(item, str) and len(item) >= 6}


def _same_path(left, right):
    if left == right:
        return True
    left_name = PurePosixPath(left.lower()).name
    right_name = PurePosixPath(right.lower()).name
    if left_name != right_name or left_name in _GENERIC_BASENAMES:
        return False
    return True


def _shared_paths(issue, pr):
    """Paths on the pull request come from its file list, not the title.

    A basename such as ``package.json`` is too common to count. ``bun.lock``
    and ``yarn.lock`` are specific enough.
    """
    pr_paths = [item for item in list(pr.get("files") or []) + list(pr.get("paths") or []) if isinstance(item, str)]
    if not pr_paths:
        return []
    shared = []
    for left in sorted(_paths(issue)):
        for right in pr_paths:
            if _same_path(left, right) and right not in shared:
                shared.append(right)
    return shared


def _rationale(overlap, fixes_reference):
    if fixes_reference:
        return "PR 內文有關閉關鍵字指向這個 issue。"
    if overlap == DEFINITE:
        return "沒有 Fixes #ID。路徑、符號或足夠的罕見詞同時重疊，所以是 definite_duplicate。"
    if overlap == POSSIBLE:
        return "只有部分標題重疊，或缺少路徑與符號，不足以判成 definite_duplicate。"
    if overlap == UNVERIFIED:
        return "沒有可用的 PR corpus。空結果不是「沒有重複」的證據。"
    return "沒有足夠的路徑、符號或罕見詞。編號或單一關鍵字命中是搜尋雜訊，不是重複。"


def classify_pair(issue, pr):
    """Classify one issue against one pull request.

    ``pr`` is untrusted text plus optional file and symbol lists. An empty
    file list does not prove the pull request is unrelated.
    """
    number = issue.get("number")
    fixes = number in closing_numbers(pr.get("body") or "") or number in closing_numbers(pr.get("title") or "")
    shared_paths = _shared_paths(issue, pr)
    shared_symbols = sorted(_symbols(issue) & _symbols(pr))
    issue_tokens = set(_tokens(f"{issue.get('title') or ''} {issue.get('body') or ''}"))
    pr_tokens = set(_tokens(f"{pr.get('title') or ''} {pr.get('body') or ''}"))
    shared_tokens = sorted(issue_tokens & pr_tokens)
    has_corpus_detail = bool(pr.get("files") or pr.get("symbols") or pr.get("paths"))

    if fixes:
        overlap = DEFINITE
    elif shared_paths and (shared_symbols or len(shared_tokens) >= 3):
        overlap = DEFINITE
    elif shared_symbols and len(shared_tokens) >= 3:
        overlap = DEFINITE
    elif len(shared_tokens) >= 5:
        overlap = DEFINITE
    elif shared_paths or shared_symbols or len(shared_tokens) >= 2:
        # A title echo without files is only a possible overlap.
        overlap = POSSIBLE if has_corpus_detail or len(shared_tokens) >= 2 else UNVERIFIED
    elif not (pr.get("title") or pr.get("body") or has_corpus_detail):
        overlap = UNVERIFIED
    else:
        overlap = NONE

    return {
        "number": pr.get("number"),
        "org": pr.get("org") or issue.get("org"),
        "repo": pr.get("repo") or issue.get("repo"),
        "overlap": overlap,
        "fixes_reference": bool(fixes),
        "shared_paths": shared_paths,
        "shared_symbols": shared_symbols,
        "rationale": _rationale(overlap, bool(fixes)),
    }


def classify_against_corpus(issue, corpus):
    """Return the strongest overlap in ``corpus``.

    ``None`` and ``[]`` both mean the corpus is missing. That stays
    ``unverified`` so an empty fetch cannot be reported as unique work.
    """
    if not corpus:
        return {
            "overlap": UNVERIFIED,
            "fixes_reference": False,
            "matches": [],
            "rationale": _rationale(UNVERIFIED, False),
        }
    matches = [classify_pair(issue, pr) for pr in corpus]
    best = max(_RANK[item["overlap"]] for item in matches)
    kept = [item for item in matches if _RANK[item["overlap"]] == best and item["overlap"] != NONE]
    if not kept:
        overlap = NONE
        fixes = False
    else:
        overlap = kept[0]["overlap"]
        fixes = any(item["fixes_reference"] for item in kept)
    kept = sorted(kept, key=lambda item: (item.get("repo") or "", item.get("number") or 0))
    return {
        "overlap": overlap,
        "fixes_reference": fixes,
        "matches": kept,
        "rationale": _rationale(overlap, fixes),
    }
