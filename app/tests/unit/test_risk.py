from datetime import datetime, timezone

import pytest

from perception_firewall.domain.evidence import (
    Evidence,
    EvidenceCategory,
    EvidenceSource,
)
from perception_firewall.domain.risk import RiskAssessment, RiskLevel


def _evidence(evidence_id: str, category: EvidenceCategory) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        category=category,
        source=EvidenceSource.RULE,
        evidence_text="observed text",
        explanation="an interpretation",
    )


def test_safe_assessment_with_empty_evidence():
    assessment = RiskAssessment(
        assessment_id="ra-1",
        session_id="sess-1",
        risk_level=RiskLevel.SAFE,
        score=0.0,
        evidence=(),
        triggered_categories=(),
        explanation="No concerning indicators observed.",
        timestamp=datetime.now(timezone.utc),
    )
    assert assessment.risk_level is RiskLevel.SAFE
    assert assessment.evidence == ()


def test_high_assessment_with_multiple_evidence_items():
    evidence_items = (
        _evidence("ev-1", EvidenceCategory.URGENCY),
        _evidence("ev-2", EvidenceCategory.CREDENTIAL_REQUEST),
    )
    assessment = RiskAssessment(
        assessment_id="ra-2",
        session_id="sess-1",
        risk_level=RiskLevel.HIGH,
        score=0.75,
        evidence=evidence_items,
        triggered_categories=(EvidenceCategory.URGENCY, EvidenceCategory.CREDENTIAL_REQUEST),
        explanation="Multiple pressure indicators observed.",
        timestamp=datetime.now(timezone.utc),
    )
    assert assessment.risk_level is RiskLevel.HIGH
    assert len(assessment.evidence) == 2
    assert assessment.evidence[0].evidence_text == "observed text"


def test_critical_assessment():
    assessment = RiskAssessment(
        assessment_id="ra-3",
        session_id="sess-1",
        risk_level=RiskLevel.CRITICAL,
        score=0.98,
        evidence=(_evidence("ev-3", EvidenceCategory.THREAT),),
        triggered_categories=(EvidenceCategory.THREAT,),
        explanation="Direct threat language observed alongside a payment request.",
        timestamp=datetime.now(timezone.utc),
    )
    assert assessment.risk_level is RiskLevel.CRITICAL


@pytest.mark.parametrize("score", [-0.01, 1.01])
def test_score_out_of_bounds_raises(score):
    with pytest.raises(ValueError):
        RiskAssessment(
            assessment_id="ra-4",
            session_id="sess-1",
            risk_level=RiskLevel.LOW,
            score=score,
            evidence=(),
            triggered_categories=(),
            explanation="explanation",
            timestamp=datetime.now(timezone.utc),
        )


def test_empty_explanation_raises():
    with pytest.raises(ValueError):
        RiskAssessment(
            assessment_id="ra-5",
            session_id="sess-1",
            risk_level=RiskLevel.LOW,
            score=0.1,
            evidence=(),
            triggered_categories=(),
            explanation="   ",
            timestamp=datetime.now(timezone.utc),
        )


def test_evidence_preserved_not_only_score():
    single_evidence = (_evidence("ev-4", EvidenceCategory.SECRECY),)
    assessment = RiskAssessment(
        assessment_id="ra-6",
        session_id="sess-1",
        risk_level=RiskLevel.MEDIUM,
        score=0.5,
        evidence=single_evidence,
        triggered_categories=(EvidenceCategory.SECRECY,),
        explanation="Secrecy request observed.",
        timestamp=datetime.now(timezone.utc),
    )
    assert assessment.evidence is single_evidence
