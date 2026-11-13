"""Collision fixtures, including duplicates that do not use Fixes #ID."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import dedup  # noqa: E402


def _load():
    return json.loads((ROOT / "tests" / "fixtures" / "collisions.json").read_text(encoding="utf-8"))


class DedupTests(unittest.TestCase):
    def setUp(self):
        self.fixture = _load()

    def test_bun_lock_duplicate_without_fixes_keyword(self):
        issue = self.fixture["issue_11502"]
        result = dedup.classify_against_corpus(issue, [self.fixture["pr_11482"]])
        self.assertEqual(result["overlap"], dedup.DEFINITE)
        self.assertFalse(result["fixes_reference"])
        self.assertEqual(result["matches"][0]["number"], 11482)
        self.assertNotIn("Fixes #11502", self.fixture["pr_11482"]["body"])
        self.assertNotIn("Close #11502", self.fixture["pr_11482"]["body"])

    def test_yarn_resolutions_duplicate_without_fixes_keyword(self):
        issue = self.fixture["issue_11568"]
        result = dedup.classify_against_corpus(issue, [self.fixture["pr_11523"]])
        self.assertEqual(result["overlap"], dedup.DEFINITE)
        self.assertFalse(result["fixes_reference"])
        self.assertEqual(result["matches"][0]["number"], 11523)

    def test_issue_text_without_corpus_stays_unverified(self):
        for key in ("issue_11502", "issue_11568"):
            result = dedup.classify_against_corpus(self.fixture[key], None)
            self.assertEqual(result["overlap"], dedup.UNVERIFIED)
            self.assertEqual(result["matches"], [])

    def test_empty_corpus_is_not_proof_of_no_duplicate(self):
        result = dedup.classify_against_corpus(self.fixture["issue_11502"], [])
        self.assertEqual(result["overlap"], dedup.UNVERIFIED)
        self.assertEqual(result["matches"], [])

    def test_keyword_search_noise_is_not_a_duplicate(self):
        result = dedup.classify_against_corpus(
            self.fixture["noise_issue"],
            [self.fixture["noise_pr"]],
        )
        self.assertEqual(result["overlap"], dedup.NONE)
        self.assertFalse(result["fixes_reference"])

    def test_weak_title_echo_without_files_is_not_definite(self):
        pr = {
            "org": "aquasecurity",
            "repo": "trivy",
            "number": 11482,
            "title": "parse bun entries",
            "body": "No file list is available.",
        }
        result = dedup.classify_against_corpus(self.fixture["issue_11502"], [pr])
        self.assertIn(result["overlap"], {dedup.POSSIBLE, dedup.UNVERIFIED})
        self.assertNotEqual(result["overlap"], dedup.DEFINITE)

    def test_classification_is_deterministic(self):
        issue = self.fixture["issue_11502"]
        corpus = [self.fixture["pr_11482"], self.fixture["noise_pr"]]
        self.assertEqual(
            dedup.classify_against_corpus(issue, corpus),
            dedup.classify_against_corpus(issue, list(reversed(corpus))),
        )


if __name__ == "__main__":
    unittest.main()
