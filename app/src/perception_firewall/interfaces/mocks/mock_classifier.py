"""MockTextClassifier — a TEST DOUBLE, not a fraud-detection model.

This class performs simple, fully deterministic keyword matching against a
small, fixed set of fixture scenarios. It exists purely so the rest of the
application pipeline can be built and tested on the developer's Mac, which
cannot run the real Qwen3-1.7B-on-Qualcomm-NPU classifier.

Its output must never be presented as, or confused with, real model
inference, and its keyword matching must never be mistaken for an actual
scam-detection algorithm. ``uncertainty`` on its results reflects only
"this mock matched a known fixture pattern" — it does not represent
calibrated model confidence of any kind.
"""

from __future__ import annotations

import uuid
from typing import Optional, Sequence

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import EvidenceCategory
from perception_firewall.domain.transcript import TranscriptSegment
from perception_firewall.interfaces.classifier import TextClassifier
from perception_firewall.interfaces.errors import ClassificationError


class MockTextClassifier(TextClassifier):
    """TEST DOUBLE. Deterministic keyword matching over fixture scenarios.

    Recognizes four scenarios: NORMAL (fallback), BANK_OTP, REMOTE_ACCESS,
    and AUTHORITY_PAYMENT. Not a fraud-detection model.
    """

    def classify(
        self,
        transcript_text: str,
        segments: Optional[Sequence[TranscriptSegment]] = None,
    ) -> ClassificationResult:
        if transcript_text is None:
            raise ClassificationError(
                "MockTextClassifier.classify() received no transcript_text"
            )

        normalized = " ".join(transcript_text.split()).lower()
        if not normalized:
            raise ClassificationError(
                "MockTextClassifier.classify() received empty transcript_text"
            )

        classification_id = f"mock-{uuid.uuid4()}"
        segment_id = segments[0].segment_id if segments else None

        if "otp" in normalized and (
            "bank" in normalized or "blocked" in normalized
        ):
            return ClassificationResult(
                classification_id=classification_id,
                indicators=(
                    EvidenceCategory.CREDENTIAL_REQUEST,
                    EvidenceCategory.URGENCY,
                ),
                credential_request="Caller asked for a one-time passcode (OTP).",
                urgency_description=(
                    "Caller stated the account will be blocked today."
                ),
                overall_assessment=(
                    "Mock scenario BANK_OTP: an OTP request framed with "
                    "urgency about account blocking."
                ),
                uncertainty=0.0,
                segment_id=segment_id,
            )

        if "anydesk" in normalized or "remote access" in normalized:
            return ClassificationResult(
                classification_id=classification_id,
                indicators=(EvidenceCategory.REMOTE_ACCESS,),
                remote_access_request=(
                    "Caller asked to install remote-access software "
                    "(AnyDesk) and grant remote access."
                ),
                overall_assessment=(
                    "Mock scenario REMOTE_ACCESS: a request to install "
                    "remote-access software."
                ),
                uncertainty=0.0,
                segment_id=segment_id,
            )

        if "authorities" in normalized or (
            "payment" in normalized
            and ("immediately" in normalized or "legal action" in normalized)
        ):
            return ClassificationResult(
                classification_id=classification_id,
                indicators=(
                    EvidenceCategory.AUTHORITY,
                    EvidenceCategory.PAYMENT,
                    EvidenceCategory.URGENCY,
                ),
                authority_claim="Caller claimed to be calling from the authorities.",
                payment_request="Caller demanded an immediate payment.",
                urgency_description=(
                    "Caller threatened legal action if payment is not "
                    "made immediately."
                ),
                overall_assessment=(
                    "Mock scenario AUTHORITY_PAYMENT: a claimed-authority "
                    "caller demanding immediate payment under threat."
                ),
                uncertainty=0.0,
                segment_id=segment_id,
            )

        return ClassificationResult(
            classification_id=classification_id,
            indicators=(),
            overall_assessment=(
                "Mock scenario NORMAL: no fixture keyword pattern matched "
                "this transcript."
            ),
            uncertainty=0.0,
            segment_id=segment_id,
        )
