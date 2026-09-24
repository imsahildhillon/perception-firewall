"""Evidence domain model.

Evidence represents a single observed or inferred indicator surfaced by the
rule prefilter or the AI classifier. It deliberately keeps the raw observed
text separate from any interpretation of it, and never asserts that an
indicator proves fraud — only that it was observed or inferred.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EvidenceCategory(Enum):
    """Behavioral indicators the application watches for.

    These name patterns of *behavior*, not conclusions about a person.
    Observing one does not mean the speaker is a scammer.
    """

    AUTHORITY = "authority"
    URGENCY = "urgency"
    THREAT = "threat"
    PAYMENT = "payment"
    CREDENTIAL_REQUEST = "credential_request"
    REMOTE_ACCESS = "remote_access"
    SECRECY = "secrecy"
    IDENTITY_PRESSURE = "identity_pressure"


class EvidenceSource(Enum):
    """Where a piece of evidence came from, preserved for provenance."""

    RULE = "rule"
    AI = "ai"
    SYSTEM = "system"


@dataclass(frozen=True)
class Evidence:
    """An observed or inferred indicator.

    ``evidence_text`` is the observed material (e.g. a transcript quote).
    ``explanation`` is the interpretation of why it matters. These are kept
    as separate fields on purpose: collapsing them would make it impossible
    to tell what was actually said from what the system concluded about it.
    """

    evidence_id: str
    category: EvidenceCategory
    source: EvidenceSource
    evidence_text: str
    explanation: str
    confidence: Optional[float] = None
    timestamp: Optional[datetime] = None
    segment_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.evidence_text.strip():
            raise ValueError("Evidence.evidence_text must not be empty")

        if not self.explanation.strip():
            raise ValueError("Evidence.explanation must not be empty")

        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Evidence.confidence must be within [0.0, 1.0]")
