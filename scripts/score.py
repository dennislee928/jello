#!/usr/bin/env python3
"""Keep acceptance and impact scores separate. Hard gates override both."""

from __future__ import annotations

import json
from pathlib import Path


def load_scoring(root):
    return json.loads((Path(root) / "config" / "scoring.json").read_text(encoding="utf-8"))


def _check_score(value, scoring, label):
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer or null")
    low = scoring["score_min"]
    high = scoring["score_max"]
    if value < low or value > high:
        raise ValueError(f"{label} must be between {low} and {high}")


def combine(acceptance, impact, scoring):
    """Weighted planning estimate. ``None`` when either score is missing."""
    if acceptance is None or impact is None:
        return None
    return (scoring["acceptance_weight"] * acceptance) + (scoring["impact_weight"] * impact)


def evaluate(status, acceptance, impact, scoring, *, confidence="low"):
    """Return the two scores, the estimate, and whether a hard gate blocks ready.

    A high combined estimate does not clear ``hard_gate_statuses`` while
    ``hard_gates_override`` is true. ``REPRODUCED`` is the first status that
    can become ``ready_to_implement``.
    """
    _check_score(acceptance, scoring, "acceptance_score")
    _check_score(impact, scoring, "impact_score")
    gate = status in set(scoring["hard_gate_statuses"])
    override = bool(scoring.get("hard_gates_override"))
    blocked = gate and override
    combined = combine(acceptance, impact, scoring)
    ready = (not blocked) and status == "REPRODUCED" and combined is not None
    if blocked:
        rationale = "硬門檻覆寫分數。acceptance 與 impact 仍分開保存，但不能進入 READY_TO_IMPLEMENT。"
    elif acceptance is None or impact is None:
        rationale = "分數缺一項。不把缺的那項當成 0，也不估計使用量。"
    else:
        rationale = "acceptance 與 impact 分開計。合併值只是計畫估算。"
    return {
        "acceptance_score": acceptance,
        "impact_score": impact,
        "combined": combined,
        "confidence": confidence,
        "hard_gate_failed": blocked,
        "ready_to_implement": ready,
        "score_rationale": rationale,
    }
