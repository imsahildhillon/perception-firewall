"""DeterministicRiskEngine — the deterministic evidence-aggregation engine.

IMPORTANT DESIGN PRINCIPLE: this component aggregates observed evidence
into an explainable risk STATE. It is NOT a fraud classifier and never
determines "this person is a scammer." It determines "given the
indicators currently observed, the current risk state is X" — see
risk/README.md.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from perception_firewall.domain.evidence import Evidence, EvidenceCategory
from perception_firewall.domain.risk import RiskAssessment, RiskContribution, RiskLevel
from perception_firewall.interfaces.errors import RiskEngineError
from perception_firewall.interfaces.risk_engine import RiskEngine
from perception_firewall.risk.config import (
    CATEGORY_WEIGHTS,
    INTERACTION_BONUSES,
    RISK_LEVEL_THRESHOLDS,
    SCORE_NORMALIZATION_CAP,
)
from perception_firewall.risk.explanations import build_explanation
from perception_firewall.risk.state import RiskStateTracker


def _level_for_raw_score(raw_score: int) -> RiskLevel:
    """Map a raw integer point total to a RiskLevel via RISK_LEVEL_THRESHOLDS."""
    level = RISK_LEVEL_THRESHOLDS[0][1]
    for minimum, candidate_level in RISK_LEVEL_THRESHOLDS:
        if raw_score >= minimum:
            level = candidate_level
        else:
            break
    return level


def _normalized_score(raw_score: int) -> float:
    """Map a raw integer point total into RiskAssessment's required
    [0.0, 1.0] range. The raw total remains fully recoverable by summing
    RiskContribution.base_points + interaction_points."""
    if raw_score <= 0:
        return 0.0
    return min(1.0, raw_score / SCORE_NORMALIZATION_CAP)


class DeterministicRiskEngine(RiskEngine):
    """Deterministic, configurable ``RiskEngine``.

    Stateful *per session_id* (for hysteresis — see ``risk/state.py``),
    but each session's state is fully isolated; different session_ids
    never share or leak state. See risk/README.md for the full scoring
    model, interaction bonuses, thresholds, and hysteresis design.
    """

    def __init__(self) -> None:
        self._state = RiskStateTracker()

    def assess(self, evidence: Sequence[Evidence], session_id: str) -> RiskAssessment:
        if session_id is None or not isinstance(session_id, str) or not session_id.strip():
            raise RiskEngineError(
                "DeterministicRiskEngine.assess() requires session_id to be "
                "a non-empty string"
            )

        if evidence is None:
            raise RiskEngineError(
                "DeterministicRiskEngine.assess() requires evidence to be a "
                "sequence, not None"
            )

        if not isinstance(evidence, (list, tuple)):
            raise RiskEngineError(
                "DeterministicRiskEngine.assess() requires evidence to be a "
                f"list or tuple, got {type(evidence).__name__!r}"
            )

        for item in evidence:
            if not isinstance(item, Evidence):
                raise RiskEngineError(
                    "DeterministicRiskEngine.assess() requires every element "
                    f"of evidence to be an Evidence, got {type(item).__name__!r}"
                )

        present_categories = {item.category for item in evidence}

        contributions: list[RiskContribution] = []
        base_score = 0
        # Canonical EvidenceCategory declaration order — not Python set
        # iteration order — so contributions/output are fully
        # deterministic across runs regardless of hash seed.
        for category in EvidenceCategory:
            if category in present_categories:
                weight = CATEGORY_WEIGHTS[category]
                base_score += weight
                contributions.append(
                    RiskContribution(
                        category=category,
                        base_points=weight,
                        interaction_points=0,
                        reason=(
                            f"{category.value} indicator observed "
                            f"(base weight {weight})."
                        ),
                    )
                )

        interaction_score = 0
        # INTERACTION_BONUSES is a literal module-level dict: insertion
        # order is fixed at definition time and stable across runs.
        for pair, bonus in INTERACTION_BONUSES.items():
            if pair.issubset(present_categories):
                interaction_score += bonus
                names = sorted(category.value for category in pair)
                contributions.append(
                    RiskContribution(
                        category=None,
                        base_points=0,
                        interaction_points=bonus,
                        reason=(
                            f"Interaction between {names[0]} and {names[1]} "
                            f"indicators (+{bonus})."
                        ),
                    )
                )

        raw_score = base_score + interaction_score
        instantaneous_level = _level_for_raw_score(raw_score)
        displayed_level = self._state.update(session_id, instantaneous_level)

        explanation = build_explanation(displayed_level, present_categories)

        triggered_categories = tuple(
            category for category in EvidenceCategory if category in present_categories
        )

        return RiskAssessment(
            assessment_id=f"risk-{session_id}-{uuid.uuid4()}",
            session_id=session_id,
            risk_level=displayed_level,
            score=_normalized_score(raw_score),
            evidence=tuple(evidence),
            triggered_categories=triggered_categories,
            explanation=explanation,
            timestamp=datetime.now(timezone.utc),
            contributions=tuple(contributions),
        )

    def reset_session(self, session_id: str) -> None:
        """Explicitly end/reset a session's hysteresis state.

        Not part of the ``RiskEngine`` interface — this is an addition
        specific to this stateful implementation (the interface itself
        was not changed), so a session can be explicitly reset per the
        STEP 5 "session handling" requirement. After this call, the next
        ``assess()`` for this ``session_id`` starts fresh, as if it were
        a brand-new session.
        """
        if session_id is None or not isinstance(session_id, str) or not session_id.strip():
            raise RiskEngineError(
                "DeterministicRiskEngine.reset_session() requires session_id "
                "to be a non-empty string"
            )
        self._state.reset(session_id)
