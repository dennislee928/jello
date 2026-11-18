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
        "body_chars": len(body),
        "linked_pr": False,
    }


def _search_url(query, page):
    q = urllib.parse.quote(query, safe=":>=<")
    return f"search/issues?q={q}&sort=created&order=desc&per_page=100&page={page}"


def search_all(query, *, runner, sleeper, pause, max_pages, max_attempts):
    """Return (items, complete, error). ``complete`` is false when results were cut."""
    items = []
    total = None
    for page in range(1, max_pages + 1):
        if page > 1 or pause:
            sleeper(pause)
        result = github_read.gh_get(_search_url(query, page), runner=runner, sleeper=sleeper, max_attempts=max_attempts)
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
    issues.sort(key=lambda i: (i["org"].lower(), i["repo"].lower(), -i["number"]))
    return {
        "schema_version": 1,
        "verified_at": verified_at,
        "window_start": since,
        "partial": bool(errors),
        "orgs": orgs,
        "errors": errors,
        "issues": issues,
    }


def _matrix(issues):
    counts = {(f, a): 0 for f in FIX_LEVELS for a in ACCEPTANCE_LEVELS}
    for issue in issues:
        counts[(issue["fix"], issue["acceptance"])] += 1
    return counts


def _cell(value):
    """Flatten untrusted text for a table cell: no pipes and no inline links."""
    return plain(value).replace("|", "/").replace("](", "] (")


def _row(issue):
    flags = []
    if issue.get("linked_pr_unverified"):
        flags.append("linked_pr 未驗證")
    note = "；".join(
        [f"修復:{r}" for r in issue["fix_reasons"]] + [f"接受:{r}" for r in issue["acceptance_reasons"]] + flags
    )
    return (
        f"| [{plain(issue['org'])}/{plain(issue['repo'])}#{issue['number']}]({issue['url']}) "
        f"| {_cell(issue['title'])[:120]} | {issue['fix']} | {issue['acceptance']} "
        f"| {issue['comments']} | {_cell(note)} |"
    )


def render_markdown(report):
    date = report["verified_at"][:10]
    lines = [
        f"# OSS org 監視：{date}",
        "",
        f"- verified_at：`{report['verified_at']}`",
        f"- 視窗：`{report['window_start']}` 之後新開、仍 open 的 issue",
        f"- partial：{'是' if report['partial'] else '否'}",
        "- 範圍：下列 org 的所有 public、未封存 repo（GitHub search `org:`）",
        "",
        "分類是啟發式提示，不是狀態轉移。`修復` 看改動本身的難度，`接受` 看外部貢獻者把它合併進去的難度；`blocked` 表示已有人指派、已有連結 PR、repo 有資格門檻，或標籤明說不收。任何一筆要進 `READY_TO_IMPLEMENT`，仍要人跑完硬門檻。標題是不可信資料，已壓成單行文字。",
        "",
        "## Org",
        "",
        "| org | 狀態 | issue | repo |",
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
    header = ["| issue | 標題 | 修復 | 接受 | 留言 | 依據 |", "| --- | --- | --- | --- | --- | --- |"]
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
        lines += ["", f"## {title}（{len(rows)}）", ""]
        if rows:
            lines += header + [_row(i) for i in rows]
        else:
            lines.append("沒有。")
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
    (out / f"{date}.md").write_text(render_markdown(report), encoding="utf-8")
    print(out / f"{date}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
