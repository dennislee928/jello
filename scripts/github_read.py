#!/usr/bin/env python3
"""Read-only GitHub snapshot via ``gh api``.

This module only builds ``GET`` requests. It never comments, assigns, forks,
opens pull requests, or pushes. Issue and pull request bodies are untrusted:
a fixed closing-keyword regex may read them in memory, and they are not
written to disk or passed to a shell.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path
from types import SimpleNamespace

# Four attempts total. Delays run before the 2nd, 3rd, and 4th attempt.
MAX_ATTEMPTS = 4
VERIFIED_AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
CLOSING_RE = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)\b"
)
POLICY_START = "<!-- policy-shas:start -->"
POLICY_END = "<!-- policy-shas:end -->"
MAINTAINER_ASSOCIATIONS = {"MEMBER", "OWNER", "COLLABORATOR"}

# Planning estimates. Applied only after a live fetch shows the issue is
# still open. Closed items must not reuse these numbers.
ESTIMATES = {
    ("apache", "superset", 46197): (3, 3, "low"),
    ("apache", "superset", 46196): (2, 3, "low"),
    ("ossf", "scorecard", 2161): (2, 3, "low"),
    ("open-telemetry", "opentelemetry-collector-contrib", 52509): (2, 3, "low"),
    ("aquasecurity", "trivy-action", 551): (2, 4, "low"),
}

# Overlap for these issues is classified only after the diff is read.
DEFER_OVERLAP = {
    ("open-telemetry", "opentelemetry-collector-contrib", 52509),
}

# Download-path comparison. Not a same-repo closing reference.
SOFT_LINKS = (
    (
        ("aquasecurity", "trivy-action", 551),
        ("aquasecurity", "setup-trivy", 40),
    ),
    (
        ("aquasecurity", "trivy-action", 551),
        ("aquasecurity", "setup-trivy", 43),
    ),
)

SKILLS = {
    "superset": ["React", "TypeScript"],
    "opentelemetry-collector-contrib": ["Go"],
    "semantic-conventions": ["Go"],
    "trivy": ["Go"],
    "trivy-action": ["GitHub Actions"],
    "setup-trivy": ["GitHub Actions"],
    "trivy-db": ["Go"],
    "scorecard": ["Go"],
    "workers-sdk": ["TypeScript"],
}


class GhResult:
    """One HTTP result. ``data`` is JSON, never a shell command."""

    def __init__(self, ok, status, headers, data, detail):
        self.ok = ok
        self.status = status
        self.headers = headers or {}
        self.data = data
        self.detail = detail

    @property
    def rate_limit_remaining(self):
        raw = self.headers.get("x-ratelimit-remaining")
        if raw is not None and str(raw).isdigit():
            return int(raw)
        return None


def parse_gh_output(stdout):
    """Split ``gh api --include`` output into status, headers, and body."""
    text = (stdout or "").replace("\r\n", "\n")
    if not text.startswith("HTTP/"):
        return None, {}, text.strip()
    head, _, body = text.partition("\n\n")
    lines = head.split("\n")
    status_parts = lines[0].split()
    status = int(status_parts[1]) if len(status_parts) > 1 and status_parts[1].isdigit() else None
    headers = {}
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
    return status, headers, body


def _auth_failure(status, stdout, stderr):
    if status == 401:
        return True
    if status is not None:
        return False
    blob = f"{stdout or ''}\n{stderr or ''}".lower()
    markers = ("gh auth login", "authentication required", "gh_token", "to get started with github cli")
    return any(marker in blob for marker in markers)


def _backoff_seconds(attempt, headers):
    """``attempt`` is the zero-based index of the failed call."""
    retry_after = headers.get("retry-after", "")
    if retry_after.isdigit():
        return min(int(retry_after), 30)
    return min(2**attempt, 30)


def _get_command(url):
    command = ["gh", "api", "--include", "--method", "GET", url]
    forbidden = {"-f", "-F", "--field", "--raw-field", "--input", "-X", "POST", "PATCH", "DELETE", "PUT"}
    if forbidden.intersection(command):
        raise RuntimeError("refusing a non-GET gh command")
    return command


def default_runner(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        return SimpleNamespace(returncode=127, stdout="", stderr=f"gh not found: {exc}")


def gh_get(url, *, runner, sleeper, max_attempts=MAX_ATTEMPTS):
    """GET ``url`` with backoff on HTTP 429 and 403.

    Auth failures are not retried. Any other HTTP error fails immediately.
    After ``max_attempts`` rate-limit responses the result is not ok.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    last_status = None
    last_headers = {}
    last_detail = "gh request failed"
    for attempt in range(max_attempts):
        proc = runner(_get_command(url))
        status, headers, body = parse_gh_output(proc.stdout or "")
        last_status = status
        last_headers = headers
        if _auth_failure(status, proc.stdout, proc.stderr):
            return GhResult(False, status, headers, None, "gh auth failed")
        if status in (429, 403):
            last_detail = f"HTTP {status}"
            if attempt + 1 < max_attempts:
                sleeper(_backoff_seconds(attempt, headers))
                continue
            return GhResult(False, status, headers, None, last_detail)
        if status is None:
            detail = "gh request failed"
            err = (proc.stderr or "").strip().splitlines()
            if err:
                detail = err[0][:180]
            return GhResult(False, None, headers, None, detail)
        if not 200 <= status < 300:
            return GhResult(False, status, headers, None, f"HTTP {status}")
        if not body.strip():
            return GhResult(True, status, headers, None, "")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return GhResult(False, status, headers, None, "response was not JSON")
        return GhResult(True, status, headers, data, "")
    return GhResult(False, last_status, last_headers, None, last_detail)


def _next_link(headers):
    link = headers.get("link", "")
    for part in link.split(","):
        if 'rel="next"' not in part:
            continue
        raw = part.split(";", 1)[0].strip()
        if raw.startswith("<") and raw.endswith(">"):
            return raw[1:-1]
    return None


def fetch_json(url, *, runner, sleeper, max_attempts=MAX_ATTEMPTS, paginate=False):
    """Fetch one JSON document, or every page of a JSON array."""
    if not paginate:
        return gh_get(url, runner=runner, sleeper=sleeper, max_attempts=max_attempts)
    items = []
    seen = set()
    page_url = url
    headers = {}
    pages = 0
    while page_url and page_url not in seen and pages < 10:
        seen.add(page_url)
        result = gh_get(page_url, runner=runner, sleeper=sleeper, max_attempts=max_attempts)
        if not result.ok:
            return result
        headers = result.headers
        if not isinstance(result.data, list):
            return result
        items.extend(result.data)
        page_url = _next_link(result.headers)
        pages += 1
    if page_url:
        return GhResult(False, None, headers, None, "pagination stopped")
    return GhResult(True, 200, headers, items, "")


def _check_name(value, label):
    if not isinstance(value, str) or not NAME_RE.fullmatch(value):
        raise ValueError(f"unsafe {label}")
    return value


def _quote_path(path):
    return "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))


def closing_numbers(text):
    """Return issue numbers named by a closing keyword. ``text`` is untrusted."""
    found = []
    for match in CLOSING_RE.finditer(text or ""):
        number = int(match.group(1))
        if number not in found:
            found.append(number)
    return found


def _names(items, key):
    values = []
    for item in items or []:
        if isinstance(item, dict) and isinstance(item.get(key), str):
            values.append(item[key])
    return sorted(set(values))


def _timeline_facts(events, org, repo):
    """Reduce timeline events to signals and same-repo PR cross-references.

    Comment and issue bodies are ignored on purpose.
    """
    signals = []
    pulls = []
    for event in events or []:
        if not isinstance(event, dict):
            continue
        kind = event.get("event")
        if kind == "commented":
            actor = event.get("actor") or event.get("user") or {}
            login = actor.get("login") if isinstance(actor, dict) else None
            association = event.get("author_association") or "NONE"
            if not login:
                continue
            if association in MAINTAINER_ASSOCIATIONS:
                signals.append(f"maintainer comment from {login}")
            else:
                signals.append(f"comment from {login} (author_association {association})")
            continue
        if kind != "cross-referenced":
            continue
        source = event.get("source") or {}
        issue = source.get("issue") if isinstance(source, dict) else None
        if not isinstance(issue, dict):
            continue
        repository = issue.get("repository") or {}
        full_name = repository.get("full_name") if isinstance(repository, dict) else None
        number = issue.get("number")
        url = issue.get("html_url") if isinstance(issue.get("html_url"), str) else ""
        if not isinstance(full_name, str) or not isinstance(number, int):
            continue
        same_repo = full_name == f"{org}/{repo}"
        is_pr = isinstance(issue.get("pull_request"), dict)
        if same_repo and is_pr:
            source_org, source_repo = full_name.split("/", 1)
            pulls.append(
                {
                    "org": source_org,
                    "repo": source_repo,
                    "number": number,
                    "url": url,
                }
            )
        elif same_repo:
            signals.append(f"same-repo issue cross-reference #{number}")
        else:
            signals.append(f"ignored unrelated cross-reference {full_name}#{number}")
    if not pulls and not any(item.startswith("same-repo") for item in signals):
        signals.append("timeline has no same-repo pull cross-reference; that is not proof of no duplicate")
    return sorted(set(signals)), pulls


def judge_status(*, role, fetch_ok, github_state, vouch_present=None):
    """Map a live fetch to the status machine. Do not invent a ready state."""
    if not fetch_ok:
        return "UNVERIFIED"
    if role == "known_collision":
        return "DUPLICATE_OR_IN_PROGRESS"
    if role == "blocked_vouch":
        if vouch_present is None:
            return "UNVERIFIED"
        return "DISCOVERED" if vouch_present else "BLOCKED"
    if github_state == "closed":
        return "CLOSED"
    if role == "needs_maintainer":
        return "NEEDS_MAINTAINER"
    if role == "blocked_symbols":
        return "BLOCKED"
    if role == "revalidate":
        # A missing cross-reference is not evidence that nobody is working on it.
        return "UNVERIFIED"
    if role == "comparison":
        return "DISCOVERED"
    return "UNVERIFIED"


def _scores(status, org, repo, number, hard_gates):
    if repo == "workers-sdk" and status == "BLOCKED":
        acceptance, impact, confidence = 1, None, "unknown"
        rationale = "Vouch 未通過。acceptance 只反映資格缺口。impact 不評，使用量維持 unknown。"
    elif (org, repo, number) in ESTIMATES and status in {"UNVERIFIED", "NEEDS_MAINTAINER", "BLOCKED"}:
        acceptance, impact, confidence = ESTIMATES[(org, repo, number)]
        rationale = (
            f"計畫估算 acceptance {acceptance}、impact {impact}，信心 {confidence}。"
            "這次 live issue 仍開放，所以保留低信心估計；這不是使用量。"
            "硬門檻覆寫分數，不能進入 READY_TO_IMPLEMENT。"
        )
    elif status == "DUPLICATE_OR_IN_PROGRESS":
        acceptance, impact, confidence = None, None, "low"
        rationale = "已知碰撞或已有人在處理。不計實作分數。"
    elif status in {"CLOSED", "DISCOVERED"}:
        acceptance, impact, confidence = None, None, "unknown"
        rationale = "不是實作候選。已依 live 狀態重抓，不沿用計畫分數。"
    else:
        acceptance, impact, confidence = None, None, "unknown"
        rationale = "資料不足，不估分。"
    return {
        "acceptance_score": acceptance,
        "impact_score": impact,
        "confidence": confidence,
        "score_rationale": rationale,
        "hard_gate_failed": status in hard_gates,
    }


def _next_action(status, repo, number):
    special = {
        ("superset", 46197): "讀 TableChart.tsx、其測試與 dashboard Chart.tsx。需要執行中的 UI 才能斷言時維持 REPRO_PENDING。",
        ("superset", 46196): "核對 description 與 description_markdown。不可信描述不得進 dangerouslySetInnerHTML。",
        ("scorecard", 2161): "只寫設計筆記，把刪除的 release branch、改名的 default branch、API 權限不足與真正未保護分開。不改分數語意。",
        ("opentelemetry-collector-contrib", 52509): "確認產生的 HPA 符號與 Code Owner 之前維持 BLOCKED。#50908 的 overlap 等 diff。",
        ("trivy-action", 551): "對照 setup-trivy #40 與 #43 的下載路徑，只寫版本釘選、SHA-256、簽章、快取、架構與發布流程。",
        ("semantic-conventions", 4100): "只核對 collector 依賴的 semconv 版本。這不是本協調庫要開的 PR。",
    }
    if status == "CLOSED":
        return "重抓時已關閉或合併。不沿用計畫分數，也不選為實作。"
    if status == "DUPLICATE_OR_IN_PROGRESS":
        return "已知重疊或已有人處理。停止實作，只留去重紀錄。"
    if (repo, number) in special and status != "UNVERIFIED":
        return special[(repo, number)]
    if (repo, number) in special:
        return special[(repo, number)]
    if status == "BLOCKED":
        return "資格或依賴未確認。不選實作 issue。"
    if status == "NEEDS_MAINTAINER":
        return "維持 NEEDS_MAINTAINER。草稿不張貼。"
    if status == "DISCOVERED":
        return "只當上下文。不選為實作候選。"
    return "補齊 API 證據。缺少交叉引用不算沒有人在做；搜尋雜訊不算重複。"


def _blocking(status, org, repo, number, vouch_present):
    items = []
    if (org, repo, number) == ("open-telemetry", "opentelemetry-collector-contrib", 52509):
        items.append("generated HPA symbols unconfirmed")
        items.append("code owner approval unconfirmed")
    if (org, repo, number) == ("aquasecurity", "trivy-action", 551):
        items.append("maintainer agreement on which repo owns the download feature")
    if (org, repo, number) == ("ossf", "scorecard", 2161):
        items.append("maintainer agreement before any score-semantics change")
    if repo == "workers-sdk" and vouch_present is False:
        items.append("dennislee928 is not in .github/VOUCHED.td")
    if status == "DUPLICATE_OR_IN_PROGRESS":
        items.append("overlapping pull request is already tracked")
    if status == "UNVERIFIED":
        items.append("duplicate check is incomplete")
    return sorted(set(items))


def _empty_candidate(org, repo, kind, number, verified_at, local_dir, detail, hard_gates):
    if kind == "pull_request" and number is not None:
        url = f"https://github.com/{org}/{repo}/pull/{number}"
    elif number is not None:
        url = f"https://github.com/{org}/{repo}/issues/{number}"
    else:
        url = f"https://github.com/{org}/{repo}"
    status = "UNVERIFIED"
    scored = _scores(status, org, repo, number, hard_gates)
    evidence = f"{local_dir}/evidence/vouch.md" if kind == "qualification" else f"{local_dir}/evidence/{repo}-{number}.md"
    return {
        "org": org,
        "repo": repo,
        "kind": kind,
        "issue_number": number,
        "url": url,
        "title": "",
        "labels": [],
        "assignees": [],
        "github_state": "unknown",
        "issue_updated_at": None,
        "last_verified_at": verified_at,
        "status": status,
        "duplicate_prs": [],
        "maintainer_signals": [detail],
        "blocking_dependencies": ["duplicate check is incomplete"],
        "skills_match": SKILLS.get(repo, []),
        "sources": [url],
        "next_action": _next_action(status, repo, number),
        "evidence_path": evidence,
        **scored,
    }


def build_candidate(seed, target, payload, *, verified_at, local_dir, hard_gates, vouch_present=None):
    """Build one candidate from a normalized payload. ``payload['body']`` is not copied."""
    org = seed.get("org") or target["org"]
    repo = seed.get("repo") or target["repo"]
    kind = seed["kind"]
    number = seed.get("number")
    if payload is None or not payload.get("ok"):
        detail = (payload or {}).get("detail") or "fetch failed"
        return _empty_candidate(org, repo, kind, number, verified_at, local_dir, detail, hard_gates)

    github_state = payload.get("state") if payload.get("state") in {"open", "closed"} else "unknown"
    status = judge_status(
        role=seed.get("role") or "",
        fetch_ok=True,
        github_state=github_state,
        vouch_present=vouch_present,
    )
    # A missing timeline means the duplicate check is incomplete. Keep the
    # explicit gates (collision, vouch, maintainer, symbols); do not invent
    # "nobody is working on this" from a failed secondary request.
    if payload.get("timeline_unavailable") and status == "DISCOVERED":
        status = "UNVERIFIED"
    signals = list(payload.get("signals") or [])
    if payload.get("timeline_unavailable"):
        signals.append("timeline unavailable; missing cross-reference is not proof of no duplicate")
    if payload.get("merged") is True:
        signals.append("upstream merged")
    elif kind == "pull_request" and github_state == "closed" and payload.get("merged") is False:
        signals.append("closed unmerged")
    if payload.get("state_reason"):
        signals.append(f"state_reason {payload['state_reason']}")
    scored = _scores(status, org, repo, number, hard_gates)
    if kind == "qualification":
        evidence = f"{local_dir}/evidence/vouch.md"
        url = payload.get("html_url") or f"https://github.com/{org}/{repo}"
        title = payload.get("title") or "Vouch gate"
    else:
        evidence = f"{local_dir}/evidence/{repo}-{number}.md"
        url = payload.get("html_url") or ""
        title = payload.get("title") or ""
    sources = [url]
    sources.extend(payload.get("source_urls") or [])
    return {
        "org": org,
        "repo": repo,
        "kind": kind if kind == "qualification" else payload.get("kind", kind),
        "issue_number": number,
        "url": url,
        "title": title.strip(),
        "labels": list(payload.get("labels") or []),
        "assignees": list(payload.get("assignees") or []),
        "github_state": github_state,
        "issue_updated_at": payload.get("updated_at"),
        "last_verified_at": verified_at,
        "status": status,
        "duplicate_prs": [],
        "maintainer_signals": sorted(set(signals)),
        "blocking_dependencies": _blocking(status, org, repo, number, vouch_present),
        "skills_match": SKILLS.get(repo, []),
        "sources": sorted(set(item for item in sources if item)),
        "next_action": _next_action(status, repo, number),
        "evidence_path": evidence,
        **scored,
    }


def _duplicate(org, repo, number, url, overlap, fixes_reference, rationale):
    return {
        "org": org,
        "repo": repo,
        "number": number,
        "url": url or f"https://github.com/{org}/{repo}/pull/{number}",
        "overlap": overlap,
        "fixes_reference": fixes_reference,
        "rationale": rationale,
    }


def link_candidates(candidates, payloads, hard_gates=None):
    """Attach duplicate records. Does not treat keyword noise as a duplicate.

    ``payloads`` maps ``(org, repo, number)`` to a normalized payload that may
    still hold ``body`` and ``cross_pulls``. Bodies are dropped before return.
    """
    by_key = {(item["org"], item["repo"], item["issue_number"]): item for item in candidates}
    for key, payload in payloads.items():
        if not payload or not payload.get("ok"):
            continue
        if payload.get("kind") != "pull_request":
            continue
        org, repo, number = key
        url = payload.get("html_url") or ""
        for target_number in closing_numbers(payload.get("body") or ""):
            target_key = (org, repo, target_number)
            target = by_key.get(target_key)
            if target is None or target_key in DEFER_OVERLAP:
                if target_key in DEFER_OVERLAP and target is not None:
                    target["maintainer_signals"] = sorted(
                        set(target["maintainer_signals"])
                        | {f"#{number} has a closing keyword; overlap waits on the diff"}
                    )
                continue
            target["duplicate_prs"].append(
                _duplicate(
                    org,
                    repo,
                    number,
                    url,
                    "definite_duplicate",
                    True,
                    "PR 內文有關閉關鍵字指向這個編號。這是交叉引用，不是搜尋雜訊。",
                )
            )
            if target["status"] in {"DISCOVERED", "UNVERIFIED", "NEEDS_MAINTAINER"}:
                target["status"] = "DUPLICATE_OR_IN_PROGRESS"
                target["next_action"] = _next_action(target["status"], target["repo"], target["issue_number"])
                gates = hard_gates if hard_gates is not None else {"DUPLICATE_OR_IN_PROGRESS"}
                target.update(_scores(target["status"], org, repo, target_number, gates))
                target["blocking_dependencies"] = sorted(
                    set(target["blocking_dependencies"])
                    | {"overlapping pull request is already tracked"}
                )

    for key, payload in payloads.items():
        candidate = by_key.get(key)
        if candidate is None or key in DEFER_OVERLAP:
            continue
        for pull in payload.get("cross_pulls") or []:
            already = any(item["number"] == pull["number"] and item["repo"] == pull["repo"] for item in candidate["duplicate_prs"])
            if already:
                continue
            candidate["duplicate_prs"].append(
                _duplicate(
                    pull["org"],
                    pull["repo"],
                    pull["number"],
                    pull["url"],
                    "unverified",
                    False,
                    "timeline 有同儲存庫 PR 交叉引用，但沒有關閉關鍵字。這不能證明重複，也不能證明沒有重複。",
                )
            )
            if pull["url"] and pull["url"] not in candidate["sources"]:
                candidate["sources"].append(pull["url"])
                candidate["sources"] = sorted(set(candidate["sources"]))

    for left, right in SOFT_LINKS:
        source = by_key.get(left)
        other = payloads.get(right)
        if source is None or not other or not other.get("ok"):
            continue
        if any(item["number"] == right[2] and item["repo"] == right[1] for item in source["duplicate_prs"]):
            continue
        source["duplicate_prs"].append(
            _duplicate(
                right[0],
                right[1],
                right[2],
                other.get("html_url") or "",
                "possible_overlap",
                False,
                "沒有同儲存庫的關閉關鍵字。下載路徑尚未逐行對過，所以只標 possible_overlap，不是 definite_duplicate。",
            )
        )

    for key, candidate in by_key.items():
        if key not in DEFER_OVERLAP:
            continue
        for other_number, label in ((50908, "#50908"), (52631, "#52631")):
            other = payloads.get((key[0], key[1], other_number))
            if other and other.get("ok"):
                candidate["maintainer_signals"] = sorted(
                    set(candidate["maintainer_signals"])
                    | {f"{label} metadata was fetched; overlap waits on the diff"}
                )
        candidate["duplicate_prs"] = []

    for candidate in candidates:
        candidate["duplicate_prs"] = sorted(
            candidate["duplicate_prs"],
            key=lambda item: (item["repo"], item["number"], item["overlap"]),
        )
        candidate["maintainer_signals"] = sorted(set(candidate["maintainer_signals"]))
    for payload in payloads.values():
        if isinstance(payload, dict):
            payload.pop("body", None)
    return candidates


def _normalize_issue(data, kind):
    return {
        "ok": True,
        "kind": "pull_request" if kind == "pull_request" or isinstance(data.get("pull_request"), dict) else "issue",
        "state": data.get("state"),
        "merged": data.get("merged") if kind == "pull_request" else None,
        "state_reason": data.get("state_reason") if isinstance(data.get("state_reason"), str) else None,
        "title": data.get("title") if isinstance(data.get("title"), str) else "",
        "labels": _names(data.get("labels"), "name"),
        "assignees": _names(data.get("assignees"), "login"),
        "updated_at": data.get("updated_at") if isinstance(data.get("updated_at"), str) else None,
        "html_url": data.get("html_url") if isinstance(data.get("html_url"), str) else "",
        "body": data.get("body") if isinstance(data.get("body"), str) else "",
        "signals": [],
        "cross_pulls": [],
        "source_urls": [],
        "timeline_unavailable": False,
        "detail": "",
    }


def _decode_content(payload):
    if not isinstance(payload, dict):
        return None
    if payload.get("encoding") == "base64" and isinstance(payload.get("content"), str):
        try:
            return base64.b64decode(payload["content"]).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return None
    return None


def login_in_text(text, login):
    """Match the GitHub login as a whole token."""
    if text is None:
        return None
    pattern = rf"(?<![A-Za-z0-9-]){re.escape(login)}(?![A-Za-z0-9-])"
    return re.search(pattern, text) is not None


def _fetch_seed(seed, target, *, runner, sleeper, max_attempts):
    org = _check_name(seed.get("org") or target["org"], "org")
    repo = _check_name(seed.get("repo") or target["repo"], "repo")
    kind = seed["kind"]
    number = seed.get("number")
    errors = []
    if kind == "qualification":
        return None, errors
    if not isinstance(number, int):
        return {"ok": False, "detail": "seed number missing"}, errors
    if kind == "pull_request":
        url = f"repos/{org}/{repo}/pulls/{number}"
    else:
        url = f"repos/{org}/{repo}/issues/{number}"
    result = fetch_json(url, runner=runner, sleeper=sleeper, max_attempts=max_attempts)
    if not result.ok or not isinstance(result.data, dict):
        errors.append(_error(org, repo, number, result))
        return {"ok": False, "detail": result.detail or "fetch failed"}, errors
    payload = _normalize_issue(result.data, kind)
    if kind == "issue":
        timeline = fetch_json(
            f"repos/{org}/{repo}/issues/{number}/timeline?per_page=100",
            runner=runner,
            sleeper=sleeper,
            max_attempts=max_attempts,
            paginate=True,
        )
        if not timeline.ok or not isinstance(timeline.data, list):
            payload["timeline_unavailable"] = True
            errors.append(_error(org, repo, number, timeline, prefix="timeline "))
        else:
            signals, pulls = _timeline_facts(timeline.data, org, repo)
            payload["signals"] = signals
            payload["cross_pulls"] = pulls
            payload["source_urls"] = [item["url"] for item in pulls if item.get("url")]
    return payload, errors


def _error(org, repo, number, result, prefix=""):
    return {
        "org": org,
        "repo": repo,
        "number": number,
        "http_status": result.status,
        "detail": f"{prefix}{result.detail or 'fetch failed'}",
    }


def _fetch_policies(target, *, runner, sleeper, max_attempts):
    org = _check_name(target["org"], "org")
    repo = _check_name(target["repo"], "repo")
    ref = _check_name(target["default_branch"], "branch")
    rows = []
    errors = []
    for path in target.get("policy_files") or []:
        url = f"repos/{org}/{repo}/contents/{_quote_path(path)}?ref={urllib.parse.quote(ref, safe='')}"
        result = fetch_json(url, runner=runner, sleeper=sleeper, max_attempts=max_attempts)
        row = {"org": org, "repo": repo, "ref": ref, "path": path, "sha": "", "text": None}
        if result.ok and isinstance(result.data, dict) and isinstance(result.data.get("sha"), str):
            row["sha"] = result.data["sha"]
            row["text"] = _decode_content(result.data)
            row["html_url"] = result.data.get("html_url") if isinstance(result.data.get("html_url"), str) else ""
        else:
            errors.append(_error(org, repo, None, result, prefix=f"{path} "))
        rows.append(row)
    return rows, errors


def render_policy_block(rows, notes):
    lines = [
        "| 儲存庫 | 分支 | 路徑 | blob SHA |",
        "| --- | --- | --- | --- |",
    ]
    for row in sorted(rows, key=lambda item: (item["org"], item["repo"], item["path"])):
        sha = row["sha"] or "缺失"
        lines.append(
            f"| `{row['org']}/{row['repo']}` | `{row['ref']}` | `{row['path']}` | `{sha}` |"
        )
    if notes:
        lines.append("")
        for note in notes:
            lines.append(note)
    return "\n".join(lines)


def patch_requirements(text, verified_at, block):
    """Replace the verification stamp and the policy-SHA block. Leave prose intact."""
    lines = []
    replaced = False
    for line in text.splitlines():
        if not replaced and line.startswith("last_verified_at:"):
            lines.append(f"last_verified_at: {verified_at}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        raise ValueError("missing last_verified_at line")
    stamped = "\n".join(lines) + "\n"
    if POLICY_START not in stamped or POLICY_END not in stamped:
        raise ValueError("missing policy SHA markers")
    pre, _, rest = stamped.partition(POLICY_START)
    _, _, post = rest.partition(POLICY_END)
    return f"{pre}{POLICY_START}\n{block.strip()}\n{POLICY_END}{post}"


def _candidate_sort_key(candidate):
    number = candidate["issue_number"]
    return (
        candidate["org"],
        candidate["repo"],
        number is None,
        -1 if number is None else number,
        candidate["kind"],
    )


def _dump(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _render_vouch(candidate, sha, verified_at):
    present = "是" if candidate["status"] == "DISCOVERED" else "否"
    if candidate["status"] == "UNVERIFIED":
        present = "未能讀取"
    return (
        "# Vouch 資格\n\n"
        "- org / repo：`cloudflare/workers-sdk`\n"
        "- 檔案：`.github/VOUCHED.td`\n"
        f"- blob SHA：`{sha or '缺失'}`\n"
        "- 帳號：`dennislee928`\n"
        f"- 是否在名單：{present}\n"
        f"- last_verified_at：`{verified_at}`\n"
        f"- status：`{candidate['status']}`\n\n"
        "比對使用完整登入字串。名單全文不複製進本儲存庫。\n"
    )


def snapshot(root, verified_at, *, runner=None, sleeper=None, max_attempts=MAX_ATTEMPTS):
    """Fetch seeds and write ``candidates.json`` plus policy SHA blocks.

    ``verified_at`` is an input. Two calls with the same input and the same
    ``gh`` responses write the same bytes. Rate-limit counters stay off disk
    because they change between otherwise identical reads.
    """
    if not VERIFIED_AT_RE.fullmatch(verified_at):
        raise ValueError("verified_at must look like 2026-11-14T00:00:00Z")
    root = Path(root)
    runner = runner or default_runner
    sleeper = sleeper or time.sleep
    config = json.loads((root / "config" / "targets.json").read_text(encoding="utf-8"))
    scoring = json.loads((root / "config" / "scoring.json").read_text(encoding="utf-8"))
    hard_gates = set(scoring["hard_gate_statuses"])
    if scoring.get("hard_gates_override") is not True:
        raise ValueError("hard_gates_override must stay true")

    probe = gh_get("rate_limit", runner=runner, sleeper=sleeper, max_attempts=max_attempts)
    grouped = {}
    for target in config["targets"]:
        grouped.setdefault(target["local_dir"], []).append(target)

    written = []
    for local_dir in sorted(grouped):
        targets = grouped[local_dir]
        candidates = []
        payloads = {}
        errors = []
        rows = []
        notes = []
        vouch_sha = ""
        vouch_present = None
        if not probe.ok and _auth_failure(probe.status, "", probe.detail):
            auth_failed = True
        else:
            auth_failed = probe.detail == "gh auth failed"
        for target in targets:
            if auth_failed:
                for seed in target.get("seeds") or []:
                    org = seed.get("org") or target["org"]
                    repo = seed.get("repo") or target["repo"]
                    candidates.append(
                        _empty_candidate(
                            org,
                            repo,
                            seed["kind"],
                            seed.get("number"),
                            verified_at,
                            local_dir,
                            "gh auth failed",
                            hard_gates,
                        )
                    )
                    errors.append(
                        {
                            "org": org,
                            "repo": repo,
                            "number": seed.get("number"),
                            "http_status": probe.status,
                            "detail": "gh auth failed",
                        }
                    )
                continue
            policy_rows, policy_errors = _fetch_policies(
                target, runner=runner, sleeper=sleeper, max_attempts=max_attempts
            )
            rows.extend(policy_rows)
            errors.extend(policy_errors)
            if target["repo"] == "workers-sdk":
                vouch_row = next((row for row in policy_rows if row["path"] == ".github/VOUCHED.td"), None)
                login = target.get("vouch_login") or "dennislee928"
                if vouch_row is None or not vouch_row.get("sha"):
                    vouch_present = None
                    notes.append("`dennislee928` 是否在 `.github/VOUCHED.td`：未能讀取，資格為 UNVERIFIED。")
                else:
                    vouch_sha = vouch_row["sha"]
                    vouch_present = login_in_text(vouch_row.get("text"), login)
                    if vouch_present is None:
                        notes.append("`dennislee928` 是否在 `.github/VOUCHED.td`：檔案 SHA 已讀到，內文不足以比對，資格為 UNVERIFIED。")
                    else:
                        answer = "是" if vouch_present else "否"
                        notes.append(f"`dennislee928` 是否在 `.github/VOUCHED.td`：{answer}。")
            for seed in target.get("seeds") or []:
                org = seed.get("org") or target["org"]
                repo = seed.get("repo") or target["repo"]
                number = seed.get("number")
                if seed["kind"] == "qualification":
                    payload = {
                        "ok": vouch_present is not None,
                        "kind": "qualification",
                        "state": "open",
                        "title": "Vouch gate for dennislee928",
                        "html_url": "https://github.com/cloudflare/workers-sdk/blob/main/.github/VOUCHED.td",
                        "labels": [],
                        "assignees": [],
                        "updated_at": None,
                        "signals": [notes[-1]] if notes else ["vouch file was not read"],
                        "detail": "vouch file was not read",
                    }
                    seed_errors = []
                else:
                    payload, seed_errors = _fetch_seed(
                        seed, target, runner=runner, sleeper=sleeper, max_attempts=max_attempts
                    )
                errors.extend(seed_errors)
                candidate = build_candidate(
                    seed,
                    target,
                    payload,
                    verified_at=verified_at,
                    local_dir=local_dir,
                    hard_gates=hard_gates,
                    vouch_present=vouch_present if repo == "workers-sdk" else None,
                )
                candidates.append(candidate)
                if number is not None and payload is not None:
                    payloads[(org, repo, number)] = payload
        link_candidates(candidates, payloads, hard_gates)
        for row in rows:
            row.pop("text", None)
        document = {
            "schema_version": 1,
            "directory": local_dir,
            "last_verified_at": verified_at,
            "partial": bool(errors),
            "errors": sorted(errors, key=lambda item: (item["org"], item["repo"], item["number"] is None, item["number"] or -1, item["detail"])),
            "candidates": sorted(candidates, key=_candidate_sort_key),
        }
        directory = root / local_dir
        _dump(directory / "candidates.json", document)
        requirements = directory / "upstream-requirements.md"
        block = render_policy_block(rows, sorted(set(notes)))
        requirements.write_text(
            patch_requirements(requirements.read_text(encoding="utf-8"), verified_at, block),
            encoding="utf-8",
        )
        written.append(str(directory / "candidates.json"))
        written.append(str(requirements))
        if local_dir == "05-cloudflare-workers-sdk":
            qualification = next(item for item in document["candidates"] if item["kind"] == "qualification")
            vouch_path = directory / "evidence" / "vouch.md"
            vouch_path.write_text(_render_vouch(qualification, vouch_sha, verified_at), encoding="utf-8")
            written.append(str(vouch_path))
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only GitHub snapshot. GET only.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--verified-at", required=True)
    parser.add_argument("--max-attempts", type=int, default=MAX_ATTEMPTS)
    args = parser.parse_args(argv)
    written = snapshot(args.root, args.verified_at, max_attempts=args.max_attempts)
    print(f"verified_at={args.verified_at}")
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
