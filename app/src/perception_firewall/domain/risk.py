"""Risk domain model.

RiskLevel and RiskAssessment represent the application's own engineering
judgment, fused from evidence — not a claim about the objective truth of
what is happening in a conversation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from perception_firewall.domain.evidence import Evidence, EvidenceCategory


class RiskLevel(Enum):
    """Discrete risk levels the application can report.

    Deliberately free of subjective labels such as "good" or "bad" — these
    name a level of concern the application has flagged, not a moral
    judgment.
    """

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskContribution:
    """One line item explaining part of a RiskAssessment's score.

    A per-category contribution has ``category`` set and
    ``interaction_points == 0``. An interaction-bonus contribution (which
    spans two categories, not one) has ``category`` set to ``None`` and
    ``base_points == 0``; ``reason`` is expected to name the categories
    involved in that case. Exactly one of ``base_points`` /
    ``interaction_points`` is expected to be non-zero for any given
    contribution, by construction of whatever produces it — this class
    itself only requires both to be non-negative.
    """

    category: Optional[EvidenceCategory]
    base_points: int
    interaction_points: int
    reason: str

    def __post_init__(self) -> None:
        if self.category is not None and not isinstance(
            self.category, EvidenceCategory
        ):
            raise ValueError(
                "RiskContribution.category must be None or an EvidenceCategory"
            )

        if self.base_points < 0:
            raise ValueError("RiskContribution.base_points must not be negative")

        if self.interaction_points < 0:
            raise ValueError(
                "RiskContribution.interaction_points must not be negative"
            )

        if not self.reason.strip():
            raise ValueError("RiskContribution.reason must not be empty")


@dataclass(frozen=True)
class RiskAssessment:
    """The application's current fused risk assessment for a session.

    The evidence that produced this assessment is preserved on the object
    itself, rather than only a final score, so any assessment shown to a
    user can be traced back to what was actually observed. ``contributions``
    additionally preserves *how* the score was built up — which categories
    and which category-interactions contributed, and how many points each
    contributed — so the score is not just a preserved evidence list but a
    fully explainable computation.
    """

    assessment_id: str
    session_id: str
    risk_level: RiskLevel
    score: float
    evidence: tuple[Evidence, ...]
    triggered_categories: tuple[EvidenceCategory, ...]
    explanation: str
    timestamp: datetime
    # Added after the original STEP 2 fields; defaults to an empty tuple so
    # existing keyword-argument construction of RiskAssessment remains
    # valid without passing this field.
    contributions: tuple[RiskContribution, ...] = ()

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("RiskAssessment.score must be within [0.0, 1.0]")

        if not self.explanation.strip():
            raise ValueError("RiskAssessment.explanation must not be empty")

        for item in self.evidence:
            if not isinstance(item, Evidence):
                raise ValueError(
                    "RiskAssessment.evidence must contain only Evidence values"
                )

        for category in self.triggered_categories:
            if not isinstance(category, EvidenceCategory):
                raise ValueError(
                    "RiskAssessment.triggered_categories must contain only "
                    "EvidenceCategory values"
                )

        for contribution in self.contributions:
            if not isinstance(contribution, RiskContribution):
                raise ValueError(
                    "RiskAssessment.contributions must contain only "
                    "RiskContribution values"
                )
