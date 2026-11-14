#!/usr/bin/env python3
"""Daily scan against a human-reviewed baseline.

Only the repos listed in ``config/targets.json`` are read. Historical issues
are not replayed when the baseline has no watermark, and a matching keyword
is required before a new issue is reported. Issue bodies are dropped and
never passed to a shell.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
from pathlib import Path

import github_read


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def target_names(config):
    names = []
    for target in config["targets"]:
        name = f"{target['org']}/{target['repo']}"
        if name not in names:
            names.append(name)
    return names


def excluded_keys(config):
    keys = set()
    for target in config["targets"]:
        for number in target.get("excluded_numbers") or []:
            keys.add((target["org"], target["repo"], number))
        for seed in target.get("seeds") or []:
            if seed.get("role") == "known_collision" and isinstance(seed.get("number"), int):
                org = seed.get("org") or target["org"]
                repo = seed.get("repo") or target["repo"]
                keys.add((org, repo, seed["number"]))
    return keys


def keyword_hit(title, labels, keywords):
    """Return the first matching keyword.

    Short keywords such as ``Go`` must match a whole token so ``good`` and
    ``algorithm`` are not hits.
    """
    blob = f"{title or ''} {' '.join(labels or [])}".lower()
    for word in keywords:
        needle = word.lower()
        if len(needle) <= 3:
            if re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", blob):
                return word
        elif needle in blob:
            return word
    return None


def _bonus(labels, bonus_labels):
    wanted = {item.lower() for item in bonus_labels}
    return sorted(label for label in labels or [] if label.lower() in wanted)


def _plain_list(values):
    return ",".join(sorted(values or []))


def _item_url(org, repo, number, kind):
    leaf = "pull" if kind == "pull_request" else "issues"
    return f"https://github.com/{org}/{repo}/{leaf}/{number}"


def _normalize(raw):
    """Copy the fields the report is allowed to see. Bodies are discarded."""
    labels = sorted(set(raw.get("labels") or []))
    assignees = sorted(set(raw.get("assignees") or []))
    return {
        "org": raw["org"],
        "repo": raw["repo"],
        "number": raw["number"],
        "kind": raw["kind"],
        "title": raw.get("title") or "",
        "labels": labels,
        "assignees": assignees,
        "github_state": raw.get("github_state") or "unknown",
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "comment_count": raw.get("comment_count"),
    }


def select_changes(observations, baseline, *, keywords, bonus_labels, excluded):
    """Split observations into new items, material changes, and skipped stale rows.

    An observation created before the watermark and absent from the baseline
    is stale. It is counted and not alerted. Bonus labels do not qualify an
    item by themselves.
    """
    watermark = baseline.get("verified_at")
    known = {}
    for item in baseline.get("items") or []:
        known[(item["org"], item["repo"], item["number"])] = item
    new_items = []
    changes = []
    skipped = 0
    for raw in observations:
        current = _normalize(raw)
        key = (current["org"], current["repo"], current["number"])
        if key in excluded:
            skipped += 1
            continue
        previous = known.get(key)
        if previous is not None:
            if previous.get("github_state") != current["github_state"]:
                changes.append(_change(current, "github_state", previous.get("github_state"), current["github_state"]))
            if _plain_list(previous.get("assignees")) != _plain_list(current["assignees"]):
                changes.append(
                    _change(current, "assignees", _plain_list(previous.get("assignees")), _plain_list(current["assignees"]))
                )
            if "comment_count" in previous and previous.get("comment_count") != current["comment_count"]:
                changes.append(
                    _change(current, "comment_count", str(previous.get("comment_count")), str(current["comment_count"]))
                )
            continue
        created = current.get("created_at") or ""
        if not watermark or not created or created < watermark:
            skipped += 1
            continue
        matched = keyword_hit(current["title"], current["labels"], keywords)
        if not matched:
            skipped += 1
            continue
        bonuses = _bonus(current["labels"], bonus_labels)
        signals = [f"keyword:{matched}"]
        signals.extend(f"bonus:{label}" for label in bonuses)
        new_items.append(
            {
                "org": current["org"],
                "repo": current["repo"],
                "number": current["number"],
                "kind": current["kind"],
                "url": _item_url(current["org"], current["repo"], current["number"], current["kind"]),
                "title": current["title"],
                "reason": f"在 {watermark} 之後新開，標題符合關鍵字 {matched}",
                "signals": signals,
            }
        )
    new_items.sort(key=lambda item: (item["org"], item["repo"], item["number"]))
    changes.sort(key=lambda item: (item["org"], item["repo"], item["number"], item["change"]))
    return new_items, changes, skipped


def _change(current, field, before, after):
    return {
        "org": current["org"],
        "repo": current["repo"],
        "number": current["number"],
        "url": _item_url(current["org"], current["repo"], current["number"], current["kind"]),
        "change": field,
        "before": "" if before is None else str(before),
        "after": "" if after is None else str(after),
    }


def build_report(
    *,
    observations,
    errors,
    baseline,
    baseline_path,
    config,
    verified_at,
    failed_repos=None,
):
    failed = set(failed_repos or [])
    allowed = {(target["org"], target["repo"]) for target in config["targets"]}
    visible = [
        item
        for item in observations
        if (item["org"], item["repo"]) in allowed and (item["org"], item["repo"]) not in failed
    ]
    new_items, changes, skipped = select_changes(
        visible,
        baseline,
        keywords=config["keywords"],
        bonus_labels=config["bonus_labels"],
        excluded=excluded_keys(config),
    )
    uncertainties = []
    if not baseline.get("verified_at"):
        uncertainties.append(
            {
                "org": "",
                "repo": "",
                "number": None,
                "detail": "基線沒有水位，沒有列出歷史 issue",
            }
        )
    for org, repo in sorted(failed):
        uncertainties.append(
            {
                "org": org,
                "repo": repo,
                "number": None,
                "detail": "這個儲存庫讀取失敗，受影響項目維持 UNVERIFIED",
            }
        )
    report_errors = []
    for error in errors:
        report_errors.append(
            {
                "org": error["org"],
                "repo": error["repo"],
                "http_status": error.get("http_status"),
                "detail": error["detail"],
            }
        )
    report_errors.sort(key=lambda item: (item["org"], item["repo"], item["detail"]))
    uncertainties.sort(key=lambda item: (item["org"], item["repo"], item["number"] is None, item["number"] or -1, item["detail"]))
    return {
        "schema_version": 1,
        "generated_at": verified_at,
        "verified_at": verified_at,
        "partial": bool(report_errors),
        "baseline_path": baseline_path,
        "baseline_verified_at": baseline.get("verified_at"),
        "targets": target_names(config),
        "new_qualifying": new_items,
        "material_changes": changes,
        "uncertainties": uncertainties,
        "errors": report_errors,
        "stale_skipped": skipped,
        "rate_limit_remaining": None,
    }


def _observation_from_api(org, repo, data):
    kind = "pull_request" if isinstance(data.get("pull_request"), dict) else "issue"
    return _normalize(
        {
            "org": org,
            "repo": repo,
            "number": data.get("number"),
            "kind": kind,
            "title": data.get("title") or "",
            "labels": github_read._names(data.get("labels"), "name"),
            "assignees": github_read._names(data.get("assignees"), "login"),
            "github_state": data.get("state") or "unknown",
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "comment_count": data.get("comments") if isinstance(data.get("comments"), int) else None,
        }
    )


def fetch_observations(config, since, *, runner, sleeper, max_attempts=github_read.MAX_ATTEMPTS):
    """GET issues updated since ``since``. No watermark means no request."""
    if not since:
        return [], [], set()
    observations = []
    errors = []
    failed = set()
    for target in config["targets"]:
        org = target["org"]
        repo = target["repo"]
        quoted = urllib.parse.quote(since, safe="")
        url = (
            f"repos/{org}/{repo}/issues?state=all&sort=updated&direction=desc"
            f"&per_page=100&since={quoted}"
        )
        result = github_read.fetch_json(
            url,
            runner=runner,
            sleeper=sleeper,
            max_attempts=max_attempts,
            paginate=True,
        )
        if not result.ok or not isinstance(result.data, list):
            errors.append(
                {
                    "org": org,
                    "repo": repo,
                    "number": None,
                    "http_status": result.status,
                    "detail": result.detail or "fetch failed",
                }
            )
            failed.add((org, repo))
            continue
        for data in result.data:
            if isinstance(data, dict) and isinstance(data.get("number"), int):
                observations.append(_observation_from_api(org, repo, data))
    observations.sort(key=lambda item: (item["org"], item["repo"], item["number"]))
    return observations, errors, failed


def report_from_fixture(path, config):
    fixture = _load(path)
    verified_at = fixture["verified_at"]
    if not github_read.VERIFIED_AT_RE.fullmatch(verified_at):
        raise ValueError("fixture verified_at must look like 2026-11-14T01:00:00Z")
    failed = {(error["org"], error["repo"]) for error in fixture.get("errors") or []}
    return build_report(
        observations=fixture.get("observations") or [],
        errors=fixture.get("errors") or [],
        baseline=fixture["baseline"],
        baseline_path=str(path),
        config=config,
        verified_at=verified_at,
        failed_repos=failed,
    )


def dump_report(report, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only daily scan. GET only.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--baseline", default="reports/state/baseline.json")
    parser.add_argument("--fixture")
    parser.add_argument("--verified-at")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-attempts", type=int, default=github_read.MAX_ATTEMPTS)
    args = parser.parse_args(argv)
    root = Path(args.root)
    config = _load(root / "config" / "targets.json")
    if args.fixture:
        report = report_from_fixture(args.fixture, config)
    else:
        if not args.verified_at or not github_read.VERIFIED_AT_RE.fullmatch(args.verified_at):
            raise SystemExit("live scan requires --verified-at like 2026-11-14T01:00:00Z")
        baseline = _load(root / args.baseline)
        observations, errors, failed = fetch_observations(
            config,
            baseline.get("verified_at"),
            runner=github_read.default_runner,
            sleeper=time.sleep,
            max_attempts=args.max_attempts,
        )
        report = build_report(
            observations=observations,
            errors=errors,
            baseline=baseline,
            baseline_path=args.baseline,
            config=config,
            verified_at=args.verified_at,
            failed_repos=failed,
        )
    dump_report(report, args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
