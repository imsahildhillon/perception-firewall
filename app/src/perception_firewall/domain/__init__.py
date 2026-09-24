"""Perception Firewall domain layer.

Model-independent application concepts. See README.md in this directory
for the boundary this layer enforces.
"""

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import (
    Evidence,
    EvidenceCategory,
    EvidenceSource,
)
from perception_firewall.domain.risk import RiskAssessment, RiskContribution, RiskLevel
from perception_firewall.domain.session import SessionState
from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource

__all__ = [
    "ClassificationResult",
    "Evidence",
    "EvidenceCategory",
    "EvidenceSource",
    "RiskAssessment",
    "RiskContribution",
    "RiskLevel",
    "SessionState",
    "TranscriptSegment",
    "TranscriptSource",
]
