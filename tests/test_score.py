"""Acceptance and impact stay separate. Hard gates override the estimate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import score  # noqa: E402


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.scoring = score.load_scoring(ROOT)

    def test_config_weights_and_override(self):
        self.assertEqual(self.scoring["acceptance_weight"], 0.5)
        self.assertEqual(self.scoring["impact_weight"], 0.5)
        self.assertTrue(self.scoring["hard_gates_override"])

    def test_scores_stay_separate_when_gate_blocks_ready(self):
        result = score.evaluate("BLOCKED", 5, 4, self.scoring)
        self.assertEqual(result["acceptance_score"], 5)
        self.assertEqual(result["impact_score"], 4)
        self.assertEqual(result["combined"], 4.5)
        self.assertTrue(result["hard_gate_failed"])
        self.assertFalse(result["ready_to_implement"])

    def test_reproduced_high_scores_can_be_ready(self):
        result = score.evaluate("REPRODUCED", 4, 4, self.scoring, confidence="medium")
        self.assertFalse(result["hard_gate_failed"])
        self.assertTrue(result["ready_to_implement"])
        self.assertEqual(result["confidence"], "medium")
        self.assertEqual(result["combined"], 4.0)

    def test_missing_impact_is_not_zero(self):
        result = score.evaluate("REPRODUCED", 1, None, self.scoring)
        self.assertIsNone(result["impact_score"])
        self.assertIsNone(result["combined"])
        self.assertFalse(result["ready_to_implement"])

    def test_out_of_range_score_is_rejected(self):
        with self.assertRaises(ValueError):
            score.evaluate("REPRODUCED", 6, 1, self.scoring)
        with self.assertRaises(ValueError):
            score.evaluate("REPRODUCED", 1, -1, self.scoring)


if __name__ == "__main__":
    unittest.main()
