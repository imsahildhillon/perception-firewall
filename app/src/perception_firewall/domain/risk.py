"""Risk domain model.

RiskLevel and RiskAssessment represent the application's own engineering
judgment, fused from evidence — not a claim about the objective truth of
what is happening in a conversation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
class RiskAssessment:
    """The application's current fused risk assessment for a session.

    The evidence that produced this assessment is preserved on the object
    itself, rather than only a final score, so any assessment shown to a
    user can be traced back to what was actually observed.
    """

    assessment_id: str
    session_id: str
    risk_level: RiskLevel
    score: float
    evidence: tuple[Evidence, ...]
    triggered_categories: tuple[EvidenceCategory, ...]
    explanation: str
    timestamp: datetime

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
