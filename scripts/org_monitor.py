#!/usr/bin/env python3
"""Daily read-only monitor of every public repo in the configured orgs.

One GitHub search per org (``org:<name> is:issue is:open archived:false``)
covers all of that org's public repos without listing them one by one. A
second search with ``linked:pr`` marks issues that already have a pull
request. Only ``GET`` requests are sent, through ``github_read.gh_get``.

Each issue gets two heuristic labels:

- ``fix``: how hard the change itself looks (low, medium, high).
- ``acceptance``: how hard it would be for an outside contributor to get it
  merged (low, medium, high, blocked).

These are triage hints, not state machine transitions. Nothing here moves a
candidate to ``READY_TO_IMPLEMENT``; a human still runs the hard gates.

Issue bodies are untrusted. They are read in memory only for their length,
never written to disk, never echoed, and never passed to a shell. Titles go
through ``render_report.plain`` before they reach Markdown.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import time
import urllib.parse
from pathlib import Path

import github_read
from render_report import plain

FIX_LEVELS = ("low", "medium", "high")
ACCEPTANCE_LEVELS = ("low", "medium", "high", "blocked")
ORG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")
LABEL_RE = re.compile(r"^[A-Za-z0-9 _./:-]{1,50}$")

# Phrases people use to claim an issue. Matched in memory against comment
# bodies, which are untrusted and never stored.
CLAIM_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"\b(?:i'?d|i would) (?:like|love) to (?:work on|take|pick|tackle|handle|fix|contribute|give)",
        r"\b(?:can|could|may) i (?:work on|take|pick|tackle|handle|fix|be assigned|get assigned|contribute)",
        r"\b(?:please )?assign (?:this|it)(?: issue)? to me\b",
        r"\bassign me\b",
        r"(?:^|\n)\s*/assign\b",
        r"\bi'?m (?:working on|on) (?:this|it)\b",
        r"\bi'?ll (?:take|work on|pick up|tackle) (?:this|it)\b",
        r"\bi want to (?:work on|take|fix|tackle)\b",
        r"\bhave a fix ready\b",
        r"\bworking on (?:a |the )?fix\b",
        r"\bwill try to pick (?:this |it )?up\b",
        r"\b(?:would|'d) like (?:to )?pick (?:this |it )?up\b",
        r"\bbefore i open (?:a|the) pr\b",
        r"\bi can open a pr\b",
        r"\[x\] yes i am willing to submit a pr",
        r"\balready (?:fixed|reproduced)\b[^.\n]{0,80}\b(?:working on|fix)\b",
    )
)
TAKEN_ORDER = ("merged_pr", "open_pr", "assigned", "claimed")


def _lower_set(values):
    return {value.lower() for value in values or []}


def _title_has(title, words):
    blob = (title or "").lower()
    for word in words or []:
        needle = word.lower()
        if len(needle) <= 4 and needle.isalpha():
            if re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", blob):
                return word
        elif needle in blob:
            return word
    return None


def classify_fix(issue, rules):
    """Return (level, reasons). Labels outrank title words; body length only raises."""
    labels = _lower_set(issue["labels"])
    reasons = []
    level = None
    hit = sorted(labels & _lower_set(rules.get("high_labels")))
    if hit:
        level = "high"
        reasons.append(f"label:{hit[0]}")
    if level is None:
        hit = sorted(labels & _lower_set(rules.get("low_labels")))
        if hit:
            level = "low"
            reasons.append(f"label:{hit[0]}")
    if level is None:
        word = _title_has(issue["title"], rules.get("high_title_words"))
        if word:
            level = "high"
            reasons.append(f"title:{word}")
    if level is None:
        word = _title_has(issue["title"], rules.get("low_title_words"))
        if word:
            level = "low"
            reasons.append(f"title:{word}")
    if level is None:
        hit = sorted(labels & _lower_set(rules.get("medium_labels")))
        word = None if hit else _title_has(issue["title"], rules.get("medium_title_words"))
        if hit or word:
            level = "medium"
            reasons.append(f"label:{hit[0]}" if hit else f"title:{word}")
    if level is None:
        level = "medium"
        reasons.append("default")
    limit = rules.get("long_body_chars") or 0
    if limit and issue.get("body_chars", 0) > limit and level != "high":
        level = "high" if level == "medium" else "medium"
        reasons.append(f"body>{limit}")
    return level, reasons


def classify_acceptance(issue, rules, overrides):
    """Return (level, reasons). Hard blockers win over every positive signal."""
    labels = _lower_set(issue["labels"])
    name = f"{issue['org']}/{issue['repo']}"
    reasons = []
    override = (overrides or {}).get(name)
    if override and override.get("acceptance") == "blocked":
        return "blocked", [f"repo:{override.get('reason', 'override')}"]
    hit = sorted(labels & _lower_set(rules.get("blocked_labels")))
    if hit:
        return "blocked", [f"label:{hit[0]}"]
    if issue["assignees"]:
        return "blocked", ["assigned"]
    if issue["linked_pr"]:
        return "blocked", ["linked_pr"]
    level = "medium"
    low = sorted(labels & _lower_set(rules.get("low_labels")))
    high = sorted(labels & _lower_set(rules.get("high_labels")))
    if high:
        level = "high"
        reasons.append(f"label:{high[0]}")
    elif low:
        level = "low"
        reasons.append(f"label:{low[0]}")
    else:
        reasons.append("default")
    if issue.get("author_association") in set(rules.get("maintainer_associations") or []):
        reasons.append("maintainer-filed")
        if level == "low":
            level = "medium"
    if override and override.get("acceptance") in ("high", "medium") and level != "high":
        level = override["acceptance"]
        reasons.append(f"repo:{override.get('reason', 'override')}")
    return level, reasons


def _repo_from_url(url):
    # https://api.github.com/repos/<org>/<repo>
    parts = (url or "").rstrip("/").split("/")
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return None, None


def normalize(raw):
    org, repo = _repo_from_url(raw.get("repository_url"))
    body = raw.get("body") or ""
    return {
        "org": org,
        "repo": repo,
        "number": raw.get("number"),
        "url": raw.get("html_url") or "",
        "title": raw.get("title") or "",
        "labels": sorted({(label.get("name") or "") for label in raw.get("labels") or [] if isinstance(label, dict)}),
        "assignees": sorted({(user.get("login") or "") for user in raw.get("assignees") or [] if isinstance(user, dict)}),
        "author_association": raw.get("author_association") or "",
        "comments": raw.get("comments") or 0,
        "created_at": raw.get("created_at"),
        "author": (raw.get("user") or {}).get("login") or "",
        "body_chars": len(body),
        "self_claim": is_claim(body),
        "linked_pr": False,
    }


def _search_url(query, page, sort="created"):
    q = urllib.parse.quote(query, safe=":>=<")
    return f"search/issues?q={q}&sort={sort}&order=desc&per_page=100&page={page}"


def search_all(query, *, runner, sleeper, pause, max_pages, max_attempts, sort="created"):
    """Return (items, complete, error). ``complete`` is false when results were cut."""
    items = []
    total = None
    for page in range(1, max_pages + 1):
        if page > 1 or pause:
            sleeper(pause)
        result = github_read.gh_get(_search_url(query, page, sort), runner=runner, sleeper=sleeper, max_attempts=max_attempts)
        if not result.ok:
            return items, False, result.detail or "search failed"
        data = result.data or {}
        total = data.get("total_count", 0)
        batch = data.get("items") or []
        items.extend(batch)
        if data.get("incomplete_results"):
            return items, False, "GitHub marked the search incomplete"
        if len(batch) < 100 or len(items) >= total:
            return items, True, ""
    return items, len(items) >= (total or 0), "" if len(items) >= (total or 0) else f"stopped at {max_pages} pages of {total}"


def is_claim(body):
    text = (body or "").lower().replace("’", "'")
    return any(pattern.search(text) for pattern in CLAIM_PATTERNS)


def taken_from_timeline(issue, events, *, maintainer_associations, claim_since):
    """Decide whether someone already took the issue.

    Returns (status, evidence). ``status`` is one of ``merged_pr``,
    ``open_pr``, ``assigned``, ``claimed`` or ``free``. Only pull requests in
    the same repo count, so a merged PR in someone's fork does not.
    """
    found = {}
    own_repo = f"https://github.com/{issue['org']}/{issue['repo']}/pull/".lower()
    for event in events or []:
        if not isinstance(event, dict):
            continue
        kind = event.get("event")
        if kind == "cross-referenced":
            source = (event.get("source") or {}).get("issue") or {}
            url = source.get("html_url") or ""
            if not source.get("pull_request") or not url.lower().startswith(own_repo):
                continue
            number = url.rstrip("/").rsplit("/", 1)[-1]
            if (source.get("pull_request") or {}).get("merged_at"):
                found.setdefault("merged_pr", f"#{number}")
            elif source.get("state") == "open":
                found.setdefault("open_pr", f"#{number}")
        elif kind == "connected":
            found.setdefault("open_pr", "connected")
        elif kind == "commented":
            user = event.get("user") or event.get("actor") or {}
            login = user.get("login") or ""
            if user.get("type") == "Bot" or login.endswith("[bot]"):
                continue
            if event.get("author_association") in maintainer_associations:
                continue
            if (event.get("created_at") or "") < claim_since:
                continue
            if is_claim(event.get("body")):
                found["claimed"] = login
    if issue["assignees"]:
        found.setdefault("assigned", ",".join(issue["assignees"]))
    for status in TAKEN_ORDER:
        if status in found:
            return status, found[status]
    return "free", ""


def mentioning_pr(issue, items):
    """Return the first open PR whose title or body names this issue (``#n`` or ``GH-n``)."""
    pattern = re.compile(rf"(?:#|GH-){issue['number']}(?![0-9A-Za-z_])", re.IGNORECASE)
    for item in items or []:
        if not isinstance(item, dict) or "pull_request" not in item:
            continue
        if pattern.search(f"{item.get('title') or ''}\n{item.get('body') or ''}"):
            return f"#{item.get('number')}"
    return None


def check_taken(issue, *, runner, sleeper, max_attempts, maintainer_associations, claim_since, pr_pause=0.0):
    """Timeline first, then the issue body, then open PRs that mention the issue number."""
    url = f"repos/{issue['org']}/{issue['repo']}/issues/{issue['number']}/timeline?per_page=100"
    result = github_read.fetch_json(url, runner=runner, sleeper=sleeper, max_attempts=max_attempts, paginate=True)
    if not result.ok:
        return "UNVERIFIED", result.detail or "timeline failed"
    status, evidence = taken_from_timeline(
        issue, result.data, maintainer_associations=maintainer_associations, claim_since=claim_since
    )
    if status != "free":
        return status, evidence
    if issue.get("self_claim"):
        return "claimed", f"{issue.get('author') or 'author'}(body)"
    if pr_pause:
        sleeper(pr_pause)
    query = urllib.parse.quote(f"repo:{issue['org']}/{issue['repo']} is:pr is:open {issue['number']}", safe=":")
    found = github_read.gh_get(
        f"search/issues?q={query}&per_page=20", runner=runner, sleeper=sleeper, max_attempts=max_attempts
    )
    if not found.ok:
        return "UNVERIFIED", f"pr search: {found.detail or 'failed'}"
    pr = mentioning_pr(issue, (found.data or {}).get("items"))
    if pr:
        return "open_pr", pr
    return "free", ""


def _apply_taken(issue, status, evidence):
    issue["taken"] = status
    issue["taken_evidence"] = evidence
    if status in TAKEN_ORDER:
        issue["acceptance"] = "blocked"
        issue["acceptance_reasons"] = [f"{status}:{evidence}"] + [
            r for r in issue["acceptance_reasons"] if not r.startswith(("assigned", "linked_pr"))
        ]


def _check_priority(issue):
    fix_rank = FIX_LEVELS.index(issue["fix"])
    acc_rank = ACCEPTANCE_LEVELS.index(issue["acceptance"])
    return (acc_rank, fix_rank, -(issue["number"]))


def _starter_query(org, labels):
    quoted = ",".join(f'"{label}"' for label in labels)
    return f"org:{org} is:issue is:open archived:false label:{quoted} no:assignee -linked:pr"


def monitor(config, verified_at, *, runner=None, sleeper=None, max_attempts=github_read.MAX_ATTEMPTS):
    runner = runner or github_read.default_runner
    sleeper = sleeper or time.sleep
    now = dt.datetime.strptime(verified_at, "%Y-%m-%dT%H:%M:%SZ")
    since = (now - dt.timedelta(days=int(config.get("window_days", 1)))).strftime("%Y-%m-%dT%H:%M:%SZ")
    pause = float(config.get("search_pause_seconds", 0))
    max_pages = int(config.get("max_pages_per_org", 5))
    issues = []
    orgs = []
    errors = []
    for org in config["orgs"]:
        if not ORG_RE.match(org):
            errors.append({"org": org, "detail": "invalid org name"})
            continue
        base = f"org:{org} is:issue is:open archived:false created:>={since}"
        raw, complete, detail = search_all(
            base, runner=runner, sleeper=sleeper, pause=pause, max_pages=max_pages, max_attempts=max_attempts
        )
        linked, linked_complete, linked_detail = search_all(
            f"{base} linked:pr", runner=runner, sleeper=sleeper, pause=pause, max_pages=max_pages, max_attempts=max_attempts
        )
        linked_urls = {item.get("html_url") for item in linked}
        status = "ok"
        if not complete or not linked_complete:
            status = "UNVERIFIED"
            errors.append({"org": org, "detail": detail or linked_detail or "incomplete"})
        repos = set()
        for item in raw:
            if item.get("pull_request"):
                continue
            issue = normalize(item)
            if not issue["org"] or not isinstance(issue["number"], int):
                continue
            issue["linked_pr"] = issue["url"] in linked_urls
            if not linked_complete:
                issue["linked_pr_unverified"] = True
            issue["fix"], issue["fix_reasons"] = classify_fix(issue, config.get("fix") or {})
            issue["acceptance"], issue["acceptance_reasons"] = classify_acceptance(
                issue, config.get("acceptance") or {}, config.get("repo_overrides")
            )
            issue.pop("body_chars", None)
            repos.add(issue["repo"])
            issues.append(issue)
        orgs.append({"org": org, "status": status, "issues": sum(1 for i in issues if i["org"] == org), "repos": len(repos)})
    taken_cfg = config.get("taken_check") or {}
    maintainers = set((config.get("acceptance") or {}).get("maintainer_associations") or [])
    claim_since = (now - dt.timedelta(days=int(taken_cfg.get("claim_days", 60)))).strftime("%Y-%m-%dT%H:%M:%SZ")

    def verify(batch, limit):
        checked = 0
        for issue in sorted(batch, key=_check_priority):
            if issue["assignees"]:
                issue["taken"], issue["taken_evidence"] = "assigned", ",".join(issue["assignees"])
                continue
            if issue.get("linked_pr"):
                issue["taken"], issue["taken_evidence"] = "open_pr", "linked:pr"
                continue
            if issue["acceptance"] == "blocked" or issue["fix"] == "high":
                issue["taken"], issue["taken_evidence"] = "skipped", ""
                continue
            if checked >= limit:
                issue["taken"] = "not_checked"
                continue
            checked += 1
            status, evidence = check_taken(
                issue,
                runner=runner,
                sleeper=sleeper,
                max_attempts=max_attempts,
                maintainer_associations=maintainers,
                claim_since=claim_since,
                pr_pause=pause,
            )
            _apply_taken(issue, status, evidence)
        return checked

    window_checked = verify(issues, int(taken_cfg.get("window_max_checks", 100)))

    starter = []
    notes = []
    starter_labels = [label for label in config.get("starter_labels") or [] if LABEL_RE.match(label)]
    seen = {issue["url"] for issue in issues}
    if starter_labels:
        for org in config["orgs"]:
            if not ORG_RE.match(org):
                continue
            raw, complete, detail = search_all(
                _starter_query(org, starter_labels),
                runner=runner,
                sleeper=sleeper,
                pause=pause,
                max_pages=int(taken_cfg.get("starter_pages_per_org", 1)),
                max_attempts=max_attempts,
                sort="updated",
            )
            if not complete:
                if detail.startswith("stopped at"):
                    notes.append({"org": org, "detail": f"starter 池只取最近更新的 {len(raw)} 筆（{detail}）"})
                else:
                    errors.append({"org": org, "detail": f"starter search: {detail or 'incomplete'}"})
            for item in raw:
                if item.get("pull_request"):
                    continue
                issue = normalize(item)
                if not issue["org"] or not isinstance(issue["number"], int) or issue["url"] in seen:
                    continue
                seen.add(issue["url"])
                issue["fix"], issue["fix_reasons"] = classify_fix(issue, config.get("fix") or {})
                issue["acceptance"], issue["acceptance_reasons"] = classify_acceptance(
                    issue, config.get("acceptance") or {}, config.get("repo_overrides")
                )
                issue.pop("body_chars", None)
                starter.append(issue)
    starter_checked = verify(starter, int(taken_cfg.get("starter_max_checks", 150)))
    for issue in issues + starter:
        if issue.get("taken") == "UNVERIFIED":
            issue["acceptance_reasons"].append("taken:UNVERIFIED")

    issues.sort(key=lambda i: (i["org"].lower(), i["repo"].lower(), -i["number"]))
    starter.sort(key=lambda i: (i["org"].lower(), i["repo"].lower(), -i["number"]))
    return {
        "schema_version": 2,
        "verified_at": verified_at,
        "window_start": since,
        "claim_since": claim_since,
        "partial": bool(errors),
        "orgs": orgs,
        "errors": errors,
        "notes": notes,
        "issues": issues,
        "starter": starter,
        "taken_checks": {"window": window_checked, "starter": starter_checked},
    }


def _matrix(issues):
    counts = {(f, a): 0 for f in FIX_LEVELS for a in ACCEPTANCE_LEVELS}
    for issue in issues:
        counts[(issue["fix"], issue["acceptance"])] += 1
    return counts


def _cell(value):
    """Flatten untrusted text for a table cell: no pipes and no inline links."""
    return plain(value).replace("|", "/").replace("](", "] (")


TAKEN_TEXT = {
    "free": "無人接手",
    "claimed": "已有人認領",
    "assigned": "已指派",
    "open_pr": "已有 open PR",
    "merged_pr": "已有合併 PR",
    "skipped": "未查",
    "not_checked": "未查（超過上限）",
    "UNVERIFIED": "UNVERIFIED",
}


def _taken_cell(issue):
    status = issue.get("taken", "skipped")
    text = TAKEN_TEXT.get(status, status)
    evidence = issue.get("taken_evidence")
    return _cell(f"{text} {evidence}" if evidence else text)


def _labels_cell(issue, starter_labels):
    wanted = _lower_set(starter_labels)
    labels = sorted(issue["labels"], key=lambda name: (name.lower() not in wanted, name.lower()))
    shown = labels[:4]
    more = f" +{len(labels) - 4}" if len(labels) > 4 else ""
    return _cell(", ".join(shown) + more) if shown else ""


def _row(issue, starter_labels):
    flags = []
    if issue.get("linked_pr_unverified"):
        flags.append("linked_pr 未驗證")
    note = "；".join(
        [f"修復:{r}" for r in issue["fix_reasons"]] + [f"接受:{r}" for r in issue["acceptance_reasons"]] + flags
    )
    return (
        f"| [{plain(issue['org'])}/{plain(issue['repo'])}#{issue['number']}]({issue['url']}) "
        f"| {_cell(issue['title'])[:120]} | {_labels_cell(issue, starter_labels)} | {issue['fix']} | {issue['acceptance']} "
        f"| {_taken_cell(issue)} | {issue['comments']} | {_cell(note)} |"
    )


HEADER = [
    "| issue | 標題 | 標籤 | 修復 | 接受 | 接手 | 留言 | 依據 |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
]


def _groups(issues, lines, starter_labels, prefix=""):
    groups = [
        ("優先看：修復 low／medium，接受 low", lambda i: i["fix"] in ("low", "medium") and i["acceptance"] == "low"),
        ("可以看：接受 medium", lambda i: i["acceptance"] == "medium" and i["fix"] != "high"),
        ("難：修復 high 或接受 high", lambda i: i["acceptance"] == "high" or (i["fix"] == "high" and i["acceptance"] in ("low", "medium"))),
        ("不收：blocked", lambda i: i["acceptance"] == "blocked"),
    ]
    placed = set()
    for title, test in groups:
        rows = [i for i in issues if id(i) not in placed and test(i)]
        placed.update(id(i) for i in rows)
        lines += ["", f"## {prefix}{title}（{len(rows)}）", ""]
        if rows:
            lines += HEADER + [_row(i, starter_labels) for i in rows]
        else:
            lines.append("沒有。")


def render_markdown(report, starter_labels=()):
    date = report["verified_at"][:10]
    lines = [
        f"# OSS org 監視：{date}",
        "",
        f"- verified_at：`{report['verified_at']}`",
        f"- 視窗：`{report['window_start']}` 之後新開、仍 open 的 issue",
        f"- 接手檢查：讀 timeline，同 repo 的 open／合併 PR 交叉引用、指派，或 `{report.get('claim_since', '')}` 之後非維護者的認領留言；再看 issue 內文有沒有回報者自己認領；最後搜尋標題或內文提到這個編號（`#n`、`GH-n`）的 open PR。任何一項成立都算已接手",
        f"- partial：{'是' if report['partial'] else '否'}",
        "- 範圍：下列 org 的所有 public、未封存 repo（GitHub search `org:`）",
        "",
        "分類是啟發式提示，不是狀態轉移。`修復` 看改動本身的難度，`接受` 看外部貢獻者把它合併進去的難度；`blocked` 表示已有人指派、已有 PR、已有人認領、repo 有資格門檻，或標籤明說不收。`接手` 欄寫 `無人接手` 只代表 timeline 上看不到，仍要人在 issue 上確認。任何一筆要進 `READY_TO_IMPLEMENT`，仍要人跑完硬門檻。標題與標籤是不可信資料，已壓成單行文字。",
        "",
        "## Org",
        "",
        "| org | 狀態 | 新 issue | repo |",
        "| --- | --- | --- | --- |",
    ]
    for org in report["orgs"]:
        lines.append(f"| `{org['org']}` | {org['status']} | {org['issues']} | {org['repos']} |")
    issues = report["issues"]
    counts = _matrix(issues)
    lines += ["", "## 分類矩陣（列：修復，欄：接受）", "", "| 修復 \\ 接受 | " + " | ".join(ACCEPTANCE_LEVELS) + " |",
              "| --- | " + " | ".join("---" for _ in ACCEPTANCE_LEVELS) + " |"]
    for f in FIX_LEVELS:
        lines.append(f"| {f} | " + " | ".join(str(counts[(f, a)]) for a in ACCEPTANCE_LEVELS) + " |")
    _groups(issues, lines, starter_labels)

    starter = report.get("starter") or []
    free = [i for i in starter if i.get("taken") == "free"]
    taken = [i for i in starter if i.get("taken") in TAKEN_ORDER]
    other = [i for i in starter if i not in free and i not in taken]
    lines += [
        "",
        f"## Starter 池：{', '.join(starter_labels) if starter_labels else '未設定'}（不限開立時間，{len(starter)} 筆）",
        "",
        f"搜尋條件已排除有 assignee 與 linked PR 的 issue；再讀 timeline 後，{len(free)} 筆無人接手、{len(taken)} 筆已被接手、{len(other)} 筆未查或修復 high。",
    ]
    for title, rows in (("無人接手", free), ("已被接手", taken), ("未查或修復 high", other)):
        lines += ["", f"### {title}（{len(rows)}）", ""]
        if rows:
            lines += HEADER + [_row(i, starter_labels) for i in sorted(rows, key=_check_priority)]
        else:
            lines.append("沒有。")

    if report.get("notes"):
        lines += ["", "## 註記", ""] + [f"- `{plain(n['org'])}`：{plain(n['detail'])}" for n in report["notes"]]
    checks = report.get("taken_checks") or {}
    lines += ["", f"接手檢查共讀了 {checks.get('window', 0)} + {checks.get('starter', 0)} 個 timeline。"]
    lines += ["", "## 錯誤", ""]
    if report["errors"]:
        lines += [f"- `{plain(e['org'])}`：{plain(e['detail'])}" for e in report["errors"]]
    else:
        lines.append("沒有。")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only org-wide issue monitor. GET only.")
    parser.add_argument("--config", default="config/org-monitor.json")
    parser.add_argument("--verified-at", required=True)
    parser.add_argument("--out-dir", required=True, help="writes <date>.md and <date>.json here")
    parser.add_argument("--max-attempts", type=int, default=github_read.MAX_ATTEMPTS)
    args = parser.parse_args(argv)
    if not github_read.VERIFIED_AT_RE.match(args.verified_at):
        parser.error("--verified-at must look like 2026-11-18T01:00:00Z")
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    report = monitor(config, args.verified_at, max_attempts=args.max_attempts)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    date = args.verified_at[:10]
    (out / f"{date}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / f"{date}.md").write_text(render_markdown(report, config.get("starter_labels") or ()), encoding="utf-8")
    print(out / f"{date}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
