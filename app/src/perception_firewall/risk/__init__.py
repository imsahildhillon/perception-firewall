"""Deterministic risk-aggregation engine.

Public entry point: ``DeterministicRiskEngine``, a ``RiskEngine``
implementation. See README.md in this directory for the scoring model,
interaction bonuses, thresholds, and hysteresis design.
"""

from perception_firewall.risk.config import (
    CATEGORY_WEIGHTS,
    DE_ESCALATION_STREAK_REQUIRED,
    INTERACTION_BONUSES,
    RISK_LEVEL_THRESHOLDS,
    SCORE_NORMALIZATION_CAP,
)
from perception_firewall.risk.engine import DeterministicRiskEngine

__all__ = [
    "CATEGORY_WEIGHTS",
    "DE_ESCALATION_STREAK_REQUIRED",
    "DeterministicRiskEngine",
    "INTERACTION_BONUSES",
    "RISK_LEVEL_THRESHOLDS",
    "SCORE_NORMALIZATION_CAP",
]
