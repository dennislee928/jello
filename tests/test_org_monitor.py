"""Org-wide monitor: classification, blockers, pagination, GET-only, no bodies."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import org_monitor  # noqa: E402

CONFIG = json.loads((ROOT / "config" / "org-monitor.json").read_text(encoding="utf-8"))
BODY_MARKER = "SECRET-BODY-MARKER $(rm -rf /)"


def _issue(**overrides):
    base = {
        "org": "acme",
        "repo": "widget",
        "number": 1,
        "url": "https://github.com/acme/widget/issues/1",
        "title": "Something happens",
        "labels": [],
        "assignees": [],
        "author_association": "NONE",
        "comments": 0,
        "body_chars": 100,
        "linked_pr": False,
    }
    base.update(overrides)
    return base


def _raw(number, title, *, repo="widget", labels=(), assignees=(), assoc="NONE", body=BODY_MARKER, pr=False):
    item = {
        "number": number,
        "title": title,
        "html_url": f"https://github.com/acme/{repo}/issues/{number}",
        "repository_url": f"https://api.github.com/repos/acme/{repo}",
        "labels": [{"name": name} for name in labels],
        "assignees": [{"login": login} for login in assignees],
        "author_association": assoc,
        "comments": 2,
        "created_at": "2026-11-17T12:00:00Z",
        "body": body,
    }
    if pr:
        item["pull_request"] = {"url": "x"}
    return item


def _proc(payload, status=200):
    return SimpleNamespace(returncode=0, stdout=f"HTTP/2.0 {status} OK\n\n{json.dumps(payload)}\n", stderr="")


class ClassifyTests(unittest.TestCase):
    def test_fix_levels(self):
        fix = CONFIG["fix"]
        self.assertEqual(org_monitor.classify_fix(_issue(title="Fix typo in README"), fix)[0], "low")
        self.assertEqual(org_monitor.classify_fix(_issue(labels=["good first issue"]), fix)[0], "low")
        self.assertEqual(org_monitor.classify_fix(_issue(title="Panic when config is empty"), fix)[0], "medium")
        self.assertEqual(org_monitor.classify_fix(_issue(title="[Feature] add support for X"), fix)[0], "high")
        self.assertEqual(org_monitor.classify_fix(_issue(labels=["enhancement", "good first issue"]), fix)[0], "high")

    def test_short_title_words_match_whole_tokens(self):
        fix = CONFIG["fix"]
        level, reasons = org_monitor.classify_fix(_issue(title="Update dockerfile"), fix)
        self.assertEqual(level, "medium")
        self.assertEqual(reasons, ["default"])

    def test_long_body_raises_fix_level(self):
        level, reasons = org_monitor.classify_fix(_issue(title="crash", body_chars=9000), CONFIG["fix"])
        self.assertEqual(level, "high")
        self.assertIn("body>6000", reasons)

    def test_acceptance_blockers_win(self):
        acc = CONFIG["acceptance"]
        overrides = CONFIG["repo_overrides"]
        self.assertEqual(
            org_monitor.classify_acceptance(_issue(labels=["good first issue"], assignees=["someone"]), acc, overrides)[0],
            "blocked",
        )
        self.assertEqual(
            org_monitor.classify_acceptance(_issue(labels=["help wanted"], linked_pr=True), acc, overrides)[0], "blocked"
        )
        self.assertEqual(org_monitor.classify_acceptance(_issue(labels=["in-house"]), acc, overrides)[0], "blocked")
        vouch = _issue(org="cloudflare", repo="workers-sdk", labels=["good first issue"])
        self.assertEqual(org_monitor.classify_acceptance(vouch, acc, overrides)[0], "blocked")

    def test_acceptance_levels(self):
        acc = CONFIG["acceptance"]
        self.assertEqual(org_monitor.classify_acceptance(_issue(labels=["help wanted"]), acc, {})[0], "low")
        self.assertEqual(org_monitor.classify_acceptance(_issue(labels=["needs-triage"]), acc, {})[0], "high")
        self.assertEqual(org_monitor.classify_acceptance(_issue(), acc, {})[0], "medium")
        filed = _issue(labels=["help wanted"], author_association="MEMBER")
        level, reasons = org_monitor.classify_acceptance(filed, acc, {})
        self.assertEqual(level, "medium")
        self.assertIn("maintainer-filed", reasons)


class MonitorTests(unittest.TestCase):
    def _config(self):
        config = json.loads(json.dumps(CONFIG))
        config["orgs"] = ["acme"]
        config["search_pause_seconds"] = 0
        return config

    def test_get_only_marks_linked_prs_and_drops_bodies(self):
        calls = []
        main = [
            _raw(3, "Fix typo in docs", labels=["help wanted"]),
            _raw(2, "Crash on start"),
            _raw(1, "a pull request", pr=True),
        ]

        def runner(args):
            calls.append(args)
            self.assertEqual(args[:5], ["gh", "api", "--include", "--method", "GET"])
            query = urllib.parse.unquote(args[5])
            if "linked:pr" in query:
                return _proc({"total_count": 1, "incomplete_results": False, "items": [main[1]]})
            return _proc({"total_count": 3, "incomplete_results": False, "items": main})

        report = org_monitor.monitor(self._config(), "2026-11-18T01:00:00Z", runner=runner, sleeper=lambda _s: None)
        self.assertEqual(len(calls), 2)
        self.assertIn("org:acme is:issue is:open archived:false created:>=2026-11-17T01:00:00Z", urllib.parse.unquote(calls[0][5]))
        self.assertFalse(report["partial"])
        by_number = {i["number"]: i for i in report["issues"]}
        self.assertEqual(sorted(by_number), [2, 3])
        self.assertEqual((by_number[3]["fix"], by_number[3]["acceptance"]), ("low", "low"))
        self.assertEqual(by_number[2]["acceptance"], "blocked")
        self.assertTrue(by_number[2]["linked_pr"])
        dumped = json.dumps(report) + org_monitor.render_markdown(report)
        self.assertNotIn("SECRET-BODY-MARKER", dumped)
        self.assertNotIn("body", json.dumps(report["issues"]))

    def test_pagination_and_rate_limit_mark_unverified(self):
        page1 = [_raw(n, f"bug {n}") for n in range(200, 100, -1)]
        state = {"main": 0}

        def runner(args):
            query = urllib.parse.unquote(args[5])
            if "linked:pr" in query:
                return _proc({"total_count": 0, "incomplete_results": False, "items": []})
            state["main"] += 1
            if state["main"] == 1:
                return _proc({"total_count": 150, "incomplete_results": False, "items": page1})
            return _proc({"message": "rate limited"}, status=403)

        report = org_monitor.monitor(
            self._config(), "2026-11-18T01:00:00Z", runner=runner, sleeper=lambda _s: None, max_attempts=2
        )
        self.assertTrue(report["partial"])
        self.assertEqual(report["orgs"][0]["status"], "UNVERIFIED")
        self.assertEqual(len(report["issues"]), 100)
        self.assertEqual(state["main"], 3)

    def test_untrusted_title_cannot_inject_markdown(self):
        report = {
            "verified_at": "2026-11-18T01:00:00Z",
            "window_start": "2026-11-17T01:00:00Z",
            "partial": False,
            "orgs": [],
            "errors": [],
            "issues": [
                dict(
                    _issue(title="x | [click](https://evil) `rm -rf` <script>"),
                    fix="low",
                    fix_reasons=["default"],
                    acceptance="low",
                    acceptance_reasons=["default"],
                )
            ],
        }
        text = org_monitor.render_markdown(report)
        row = [line for line in text.splitlines() if "acme/widget#1" in line][0]
        self.assertNotIn("](https://evil)", row)
        self.assertNotIn("`rm", row)
        self.assertNotIn("<script>", row)
        self.assertEqual(row.count("|"), 7)

    def test_cli_writes_dated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "c.json"
            cfg = self._config()
            cfg["orgs"] = []
            config.write_text(json.dumps(cfg), encoding="utf-8")
            org_monitor.main(["--config", str(config), "--verified-at", "2026-11-18T01:00:00Z", "--out-dir", tmp])
            self.assertTrue((Path(tmp) / "2026-11-18.md").exists())
            self.assertTrue((Path(tmp) / "2026-11-18.json").exists())


if __name__ == "__main__":
    unittest.main()
