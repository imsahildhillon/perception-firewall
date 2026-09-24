from datetime import datetime, timezone

import pytest

from perception_firewall.domain.evidence import (
    Evidence,
    EvidenceCategory,
    EvidenceSource,
)


def test_valid_evidence():
    evidence = Evidence(
        evidence_id="ev-1",
        category=EvidenceCategory.CREDENTIAL_REQUEST,
        source=EvidenceSource.RULE,
        evidence_text="Give me the OTP immediately.",
        explanation="An OTP is being requested under time pressure.",
        confidence=0.8,
        timestamp=datetime.now(timezone.utc),
        segment_id="seg-1",
    )
    assert evidence.evidence_text != evidence.explanation
    assert evidence.category is EvidenceCategory.CREDENTIAL_REQUEST


@pytest.mark.parametrize("category", list(EvidenceCategory))
def test_each_category(category):
    evidence = Evidence(
        evidence_id="ev-cat",
        category=category,
        source=EvidenceSource.AI,
        evidence_text="observed text",
        explanation="an interpretation",
    )
    assert evidence.category is category


@pytest.mark.parametrize("source", list(EvidenceSource))
def test_each_source(source):
    evidence = Evidence(
        evidence_id="ev-src",
        category=EvidenceCategory.URGENCY,
        source=source,
        evidence_text="observed text",
        explanation="an interpretation",
    )
    assert evidence.source is source


def test_evidence_without_optional_timestamp():
    evidence = Evidence(
        evidence_id="ev-2",
        category=EvidenceCategory.THREAT,
        source=EvidenceSource.SYSTEM,
        evidence_text="observed text",
        explanation="an interpretation",
    )
    assert evidence.timestamp is None
    assert evidence.segment_id is None
    assert evidence.confidence is None


def test_empty_evidence_text_raises():
    with pytest.raises(ValueError):
        Evidence(
            evidence_id="ev-3",
            category=EvidenceCategory.PAYMENT,
            source=EvidenceSource.RULE,
            evidence_text="   ",
            explanation="an interpretation",
        )


def test_empty_explanation_raises():
    with pytest.raises(ValueError):
        Evidence(
            evidence_id="ev-4",
            category=EvidenceCategory.PAYMENT,
            source=EvidenceSource.RULE,
            evidence_text="observed text",
            explanation="",
        )


@pytest.mark.parametrize("confidence", [-0.01, 1.01, -1.0, 2.0])
def test_confidence_out_of_bounds_raises(confidence):
    with pytest.raises(ValueError):
        Evidence(
            evidence_id="ev-5",
            category=EvidenceCategory.SECRECY,
            source=EvidenceSource.AI,
            evidence_text="observed text",
            explanation="an interpretation",
            confidence=confidence,
        )


@pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0])
def test_confidence_within_bounds_is_allowed(confidence):
    evidence = Evidence(
        evidence_id="ev-6",
        category=EvidenceCategory.REMOTE_ACCESS,
        source=EvidenceSource.AI,
        evidence_text="observed text",
        explanation="an interpretation",
        confidence=confidence,
    )
    assert evidence.confidence == confidence
