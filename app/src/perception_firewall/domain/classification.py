"""Classification result domain model.

Represents structured output from an AI classifier (in practice, the
Qwen3-1.7B classifier stage), described in model-independent terms. Nothing
here names Qwen, transformers, or any runtime — this is the contract the
application pipeline depends on, not the model that fills it in.

The fields here deliberately keep each detected indicator as a separate,
optional, free-text description rather than a single verdict. A classifier
can report "a credential request was made" without this model turning that
into "this is a scam" — that judgment belongs to risk fusion, not here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from perception_firewall.domain.evidence import EvidenceCategory


@dataclass(frozen=True)
class ClassificationResult:
    """Structured, model-independent output of a single classification pass."""

    classification_id: str

    # Structured indicators the classifier detected, as domain categories
    # (not free text) so downstream risk fusion can reason over them.
    indicators: tuple[EvidenceCategory, ...] = field(default_factory=tuple)

    # Each of the following is a free-text description of what the
    # classifier observed for that specific concern, or None if it wasn't
    # detected. These are interpretations, not verbatim transcript quotes.
    requested_action: Optional[str] = None
    authority_claim: Optional[str] = None
    urgency_description: Optional[str] = None
    payment_request: Optional[str] = None
    credential_request: Optional[str] = None
    remote_access_request: Optional[str] = None
    secrecy_request: Optional[str] = None
    identity_pressure: Optional[str] = None

    # The classifier's own free-text summary of what it observed. This is
    # an assessment of behavior, not a verdict on the person, and must not
    # be treated as proof of fraud by any downstream consumer.
    overall_assessment: Optional[str] = None

    # The classifier's self-reported uncertainty about this result, in
    # [0.0, 1.0]. None means the classifier did not report one.
    uncertainty: Optional[float] = None

    segment_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.uncertainty is not None and not (0.0 <= self.uncertainty <= 1.0):
            raise ValueError(
                "ClassificationResult.uncertainty must be within [0.0, 1.0]"
            )

        for indicator in self.indicators:
            if not isinstance(indicator, EvidenceCategory):
                raise ValueError(
                    "ClassificationResult.indicators must contain only "
                    "EvidenceCategory values"
                )
