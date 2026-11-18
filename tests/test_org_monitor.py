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
            if "/timeline" in query:
                return _proc([])
            if "no:assignee" in query:
                return _proc({"total_count": 0, "incomplete_results": False, "items": []})
            if "linked:pr" in query:
                return _proc({"total_count": 1, "incomplete_results": False, "items": [main[1]]})
            return _proc({"total_count": 3, "incomplete_results": False, "items": main})

        report = org_monitor.monitor(self._config(), "2026-11-18T01:00:00Z", runner=runner, sleeper=lambda _s: None)
        searches = [c for c in calls if "/timeline" not in c[5]]
        timelines = [c for c in calls if "/timeline" in c[5]]
        self.assertEqual(len(searches), 4)  # main, linked:pr, PR mentions of #3, starter pool
        self.assertEqual(len(timelines), 1)  # #2 is blocked by its linked PR, so only #3 is checked
        self.assertIn("org:acme is:issue is:open archived:false created:>=2026-11-17T01:00:00Z", urllib.parse.unquote(calls[0][5]))
        self.assertFalse(report["partial"])
        by_number = {i["number"]: i for i in report["issues"]}
        self.assertEqual(sorted(by_number), [2, 3])
        self.assertEqual((by_number[3]["fix"], by_number[3]["acceptance"]), ("low", "low"))
        self.assertEqual(by_number[3]["taken"], "free")
        self.assertEqual(by_number[2]["taken"], "open_pr")
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
            if "/timeline" in query or "is:pr" in query:
                return _proc([] if "/timeline" in query else {"total_count": 0, "items": []})
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
        self.assertEqual(row.count("|"), 9)

    def test_cli_writes_dated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "c.json"
            cfg = self._config()
            cfg["orgs"] = []
            cfg["starter_labels"] = []
            config.write_text(json.dumps(cfg), encoding="utf-8")
            org_monitor.main(["--config", str(config), "--verified-at", "2026-11-18T01:00:00Z", "--out-dir", tmp])
            self.assertTrue((Path(tmp) / "2026-11-18.md").exists())
            self.assertTrue((Path(tmp) / "2026-11-18.json").exists())


class TakenTests(unittest.TestCase):
    MAINT = {"MEMBER", "OWNER", "COLLABORATOR"}
    SINCE = "2026-09-19T00:00:00Z"

    def _taken(self, events, **issue):
        return org_monitor.taken_from_timeline(
            _issue(**issue), events, maintainer_associations=self.MAINT, claim_since=self.SINCE
        )

    @staticmethod
    def _xref(url, state="open", merged=None):
        return {"event": "cross-referenced", "source": {"issue": {
            "html_url": url, "state": state, "pull_request": {"merged_at": merged}}}}

    @staticmethod
    def _comment(body, *, login="dev", assoc="NONE", at="2026-11-10T00:00:00Z", bot=False):
        return {"event": "commented", "body": body, "created_at": at, "author_association": assoc,
                "user": {"login": login, "type": "Bot" if bot else "User"}}

    def test_free_when_nothing_found(self):
        self.assertEqual(self._taken([self._comment("Same here, +1")]), ("free", ""))

    def test_open_and_merged_prs_in_same_repo(self):
        self.assertEqual(self._taken([self._xref("https://github.com/acme/widget/pull/9")]), ("open_pr", "#9"))
        merged = self._xref("https://github.com/acme/widget/pull/7", state="closed", merged="2026-11-01T00:00:00Z")
        self.assertEqual(self._taken([self._xref("https://github.com/acme/widget/pull/9"), merged]), ("merged_pr", "#7"))

    def test_ignores_closed_prs_forks_and_issues(self):
        events = [
            self._xref("https://github.com/acme/widget/pull/5", state="closed"),
            self._xref("https://github.com/someone/widget/pull/1", state="closed", merged="2026-11-01T00:00:00Z"),
            {"event": "cross-referenced", "source": {"issue": {"html_url": "https://github.com/acme/widget/issues/4", "state": "open"}}},
        ]
        self.assertEqual(self._taken(events), ("free", ""))

    def test_claim_comments(self):
        for body in ("Hi! I would like to take this one.", "Can I work on this?", "/assign", "I\u2019d like to work on this",
                     "Please assign this to me", "I'm working on this", "Have a fix ready."):
            self.assertEqual(self._taken([self._comment(body)]), ("claimed", "dev"), body)

    def test_claim_ignores_maintainers_bots_and_old_comments(self):
        events = [
            self._comment("I'd like to work on this", assoc="MEMBER"),
            self._comment("I'd like to work on this", login="ci[bot]", bot=True),
            self._comment("I'd like to work on this", at="2025-01-01T00:00:00Z"),
        ]
        self.assertEqual(self._taken(events), ("free", ""))

    def test_assignee_and_priority(self):
        self.assertEqual(self._taken([], assignees=["bob"]), ("assigned", "bob"))
        events = [self._comment("can i take this?"), self._xref("https://github.com/acme/widget/pull/9")]
        self.assertEqual(self._taken(events, assignees=["bob"]), ("open_pr", "#9"))

    def test_taken_makes_acceptance_blocked(self):
        issue = dict(_issue(labels=["good first issue"]), fix="low", fix_reasons=[], acceptance="low", acceptance_reasons=["label:good first issue"])
        org_monitor._apply_taken(issue, "claimed", "dev")
        self.assertEqual(issue["acceptance"], "blocked")
        self.assertEqual(issue["acceptance_reasons"][0], "claimed:dev")

    REAL_CLAIMS = (
        # go-contrib#10320 body
        "I can open a PR with this fix and regression test.",
        # iceberg-go#2633 body
        "I already reproduced this issue locally and working on a fix for this.",
        # iceberg-go#2629 comment (missing "to")
        "@badalprasadsingh I would like pick up this issue.",
        # iceberg-go#2629 body
        "Lets not let this block v0.8.0 RC, **Status** : will try to pick this up",
        # airflow#77240 issue template
        "### Are you willing to submit PR?\n\n- [x] Yes I am willing to submit a PR!",
        # iceberg-go#2416 comment
        "Before I open the PR, I'd like to check what NotStartsWith should do with a NULL value.",
        # airflow#77243: template answer kept without a checkbox
        "### Are you willing to submit PR?\n\nYes I am willing to submit a PR!",
        # cloudflare/agents#2910
        "Happy to open a PR if that helps.",
        # rocketmq-clients#1497
        "This PR fixes all nine with unit tests.",
    )
    NOT_CLAIMS = (
        # python-contrib#5353 template answer
        "### Would you like to implement a fix?\n\nNo",
        # unchecked airflow template box
        "### Are you willing to submit PR?\n\n- [ ] Yes I am willing to submit a PR!",
        "The fix is already in main, see the linked commit.",
        "Thanks for the report, the working group will discuss it.",
    )

    def test_real_claim_phrases(self):
        for text in self.REAL_CLAIMS:
            self.assertTrue(org_monitor.is_claim(text), text)
        for text in self.NOT_CLAIMS:
            self.assertFalse(org_monitor.is_claim(text), text)

    def _runner(self, timeline, pr_items):
        def runner(args):
            url = urllib.parse.unquote(args[5])
            if "/timeline" in url:
                return _proc(timeline)
            return _proc({"total_count": len(pr_items), "incomplete_results": False, "items": pr_items})
        return runner

    def _check(self, issue, timeline=(), pr_items=()):
        return org_monitor.check_taken(
            issue, runner=self._runner(list(timeline), list(pr_items)), sleeper=lambda _s: None, max_attempts=1,
            maintainer_associations=self.MAINT, claim_since=self.SINCE,
        )

    def test_body_claim_by_reporter(self):
        issue = _issue(number=2633, author="Shruthirdy", self_claim=True)
        self.assertEqual(self._check(issue), ("claimed", "Shruthirdy(body)"))

    def test_open_pr_that_names_the_issue(self):
        # parquet-java#3866 is titled "GH-3969: ..."; trivy-style "Fixes #3147" in the body also counts.
        prs = [
            {"number": 3866, "title": "GH-3969: Fix leading CLI --conf", "body": "", "pull_request": {}},
        ]
        self.assertEqual(self._check(_issue(number=3969), pr_items=prs), ("open_pr", "#3866"))
        prs = [{"number": 9, "title": "fix", "body": "Fixes #3147.", "pull_request": {}}]
        self.assertEqual(self._check(_issue(number=3147), pr_items=prs), ("open_pr", "#9"))

    def test_pr_mention_must_match_the_whole_number(self):
        prs = [
            {"number": 9, "title": "fix #31470", "body": "see #3147x", "pull_request": {}},
            {"number": 10, "title": "issue #3147 itself", "body": ""},  # an issue, not a PR
        ]
        self.assertEqual(self._check(_issue(number=3147), pr_items=prs), ("free", ""))

    def test_starter_query_and_timeline_failure(self):
        query = org_monitor._starter_query("acme", ["good first issue", "help wanted"])
        self.assertEqual(query, 'org:acme is:issue is:open archived:false label:"good first issue","help wanted" no:assignee -linked:pr')

        def runner(args):
            return _proc({"message": "nope"}, status=403)

        status, _detail = org_monitor.check_taken(
            _issue(), runner=runner, sleeper=lambda _s: None, max_attempts=1,
            maintainer_associations=self.MAINT, claim_since=self.SINCE,
        )
        self.assertEqual(status, "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
