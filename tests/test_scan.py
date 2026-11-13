"""Fixture dry-run is reproducible. The workflow file stays read-only."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_report  # noqa: E402
import scan  # noqa: E402


def _config():
    return json.loads((ROOT / "config" / "targets.json").read_text(encoding="utf-8"))


class ScanTests(unittest.TestCase):
    def test_fixture_dry_run_is_reproducible(self):
        config = _config()
        first = scan.report_from_fixture(ROOT / "tests" / "fixtures" / "scan_fixture.json", config)
        second = scan.report_from_fixture(ROOT / "tests" / "fixtures" / "scan_fixture.json", config)
        self.assertEqual(first, second)
        self.assertEqual(render_report.render_markdown(first), render_report.render_markdown(second))
        self.assertEqual(len(first["targets"]), 8)
        self.assertNotIn("example/not-a-target", first["targets"])
        numbers = {item["number"] for item in first["new_qualifying"]}
        self.assertEqual(numbers, {200, 400})
        self.assertNotIn(201, numbers)
        self.assertNotIn(300, numbers)
        self.assertNotIn(9001, numbers)
        self.assertTrue(first["partial"])
        changes = {(item["number"], item["change"]) for item in first["material_changes"]}
        self.assertEqual(changes, {(101, "assignees"), (101, "comment_count")})
        blob = json.dumps(first)
        self.assertNotIn("untrusted", blob)
        self.assertNotIn("<script>", blob)
        self.assertNotIn("ignore previous instructions", blob)
        markdown = render_report.render_markdown(first)
        self.assertNotIn("`", markdown.split("React dashboard", 1)[1][:40])
        self.assertNotIn("<script>", markdown)
        self.assertNotIn("$(", markdown)

    def test_short_keyword_does_not_match_inside_a_word(self):
        self.assertIsNone(scan.keyword_hit("algorithm", [], ["Go"]))
        self.assertEqual(scan.keyword_hit("Go parser", [], ["Go"]), "Go")
        self.assertIsNone(scan.keyword_hit("Typo in the readme", ["good first issue"], ["dashboard"]))

    def test_excluded_collision_is_not_a_new_alert(self):
        config = _config()
        report = scan.build_report(
            observations=[
                {
                    "org": "aquasecurity",
                    "repo": "trivy",
                    "number": 11383,
                    "kind": "issue",
                    "title": "security parser regression",
                    "labels": [],
                    "assignees": [],
                    "github_state": "open",
                    "created_at": "2026-11-12T00:00:00Z",
                }
            ],
            errors=[],
            baseline={"verified_at": "2026-11-01T00:00:00Z", "items": []},
            baseline_path="reports/state/baseline.json",
            config=config,
            verified_at="2026-11-14T01:00:00Z",
        )
        self.assertEqual(report["new_qualifying"], [])
        self.assertEqual(report["stale_skipped"], 1)

    def test_missing_watermark_does_not_list_history(self):
        config = _config()
        baseline = json.loads((ROOT / "reports" / "state" / "baseline.json").read_text(encoding="utf-8"))
        self.assertIsNone(baseline["verified_at"])
        report = scan.build_report(
            observations=[
                {
                    "org": "apache",
                    "repo": "superset",
                    "number": 1,
                    "kind": "issue",
                    "title": "React dashboard from 2019",
                    "created_at": "2019-01-01T00:00:00Z",
                    "github_state": "open",
                }
            ],
            errors=[],
            baseline=baseline,
            baseline_path="reports/state/baseline.json",
            config=config,
            verified_at="2026-11-14T01:00:00Z",
        )
        self.assertEqual(report["new_qualifying"], [])
        self.assertIn("沒有列出歷史 issue", report["uncertainties"][0]["detail"])

    def test_live_fetch_uses_get_and_stops_without_watermark(self):
        config = _config()
        calls = []

        def runner(args):
            calls.append(args)
            return SimpleNamespace(returncode=0, stdout="HTTP/2.0 200 OK\n\n[]\n", stderr="")

        observations, errors, failed = scan.fetch_observations(
            config,
            None,
            runner=runner,
            sleeper=lambda _delay: None,
        )
        self.assertEqual(calls, [])
        self.assertEqual(observations, [])
        self.assertEqual(errors, [])
        self.assertEqual(failed, set())

        scan.fetch_observations(
            config,
            "2026-11-01T00:00:00Z",
            runner=runner,
            sleeper=lambda _delay: None,
        )
        self.assertEqual(len(calls), 8)
        joined = "\n".join(" ".join(call) for call in calls)
        self.assertIn("--method GET", joined)
        self.assertNotIn("POST", joined)
        self.assertIn("since=2026-11-01T00%3A00%3A00Z", joined)
        self.assertNotIn("example/not-a-target", joined)

    def test_cli_dry_run_bytes_match(self):
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_json = Path(first_dir) / "report.json"
            second_json = Path(second_dir) / "report.json"
            argv = [
                "--root",
                str(ROOT),
                "--fixture",
                str(ROOT / "tests" / "fixtures" / "scan_fixture.json"),
            ]
            scan.main(argv + ["--out", str(first_json)])
            scan.main(argv + ["--out", str(second_json)])
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            first_md = Path(first_dir) / "report.md"
            second_md = Path(second_dir) / "report.md"
            render_report.main(["--input", str(first_json), "--out", str(first_md)])
            render_report.main(["--input", str(second_json), "--out", str(second_md)])
            self.assertEqual(first_md.read_bytes(), second_md.read_bytes())


class WorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_and_scheduled(self):
        text = (ROOT / ".github" / "workflows" / "oss-monitor.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "0 1 * * *"', text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("contents: read", text)
        for forbidden in ("contents: write", "issues: write", "pull-requests: write"):
            self.assertNotIn(forbidden, text)
        for forbidden in ("git push", "git commit", "gh pr create", "gh issue create", "--method POST"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
