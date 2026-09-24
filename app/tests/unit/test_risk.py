from datetime import datetime, timezone

import pytest

from perception_firewall.domain.evidence import (
    Evidence,
    EvidenceCategory,
    EvidenceSource,
)
from perception_firewall.domain.risk import RiskAssessment, RiskContribution, RiskLevel


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


# --- RiskContribution --------------------------------------------------------


def test_valid_category_contribution():
    contribution = RiskContribution(
        category=EvidenceCategory.URGENCY,
        base_points=2,
        interaction_points=0,
        reason="urgency indicator observed (base weight 2).",
    )
    assert contribution.category is EvidenceCategory.URGENCY
    assert contribution.base_points == 2


def test_valid_interaction_contribution_has_no_category():
    contribution = RiskContribution(
        category=None,
        base_points=0,
        interaction_points=3,
        reason="Interaction between credential_request and urgency indicators (+3).",
    )
    assert contribution.category is None
    assert contribution.interaction_points == 3


def test_contribution_rejects_negative_base_points():
    with pytest.raises(ValueError):
        RiskContribution(
            category=EvidenceCategory.THREAT,
            base_points=-1,
            interaction_points=0,
            reason="reason",
        )


def test_contribution_rejects_negative_interaction_points():
    with pytest.raises(ValueError):
        RiskContribution(
            category=None,
            base_points=0,
            interaction_points=-1,
            reason="reason",
        )


def test_contribution_rejects_empty_reason():
    with pytest.raises(ValueError):
        RiskContribution(
            category=EvidenceCategory.THREAT,
            base_points=3,
            interaction_points=0,
            reason="   ",
        )


def test_contribution_rejects_non_category_type():
    with pytest.raises(ValueError):
        RiskContribution(
            category="not-a-category",
            base_points=1,
            interaction_points=0,
            reason="reason",
        )


# --- RiskAssessment.contributions ---------------------------------------------


def test_contributions_defaults_to_empty_tuple_for_backward_compatibility():
    assessment = RiskAssessment(
        assessment_id="ra-7",
        session_id="sess-1",
        risk_level=RiskLevel.SAFE,
        score=0.0,
        evidence=(),
        triggered_categories=(),
        explanation="No concerning indicators observed.",
        timestamp=datetime.now(timezone.utc),
    )
    assert assessment.contributions == ()


def test_contributions_are_preserved():
    contributions = (
        RiskContribution(
            category=EvidenceCategory.URGENCY,
            base_points=2,
            interaction_points=0,
            reason="urgency indicator observed (base weight 2).",
        ),
        RiskContribution(
            category=EvidenceCategory.CREDENTIAL_REQUEST,
            base_points=4,
            interaction_points=0,
            reason="credential_request indicator observed (base weight 4).",
        ),
        RiskContribution(
            category=None,
            base_points=0,
            interaction_points=3,
            reason="Interaction between credential_request and urgency indicators (+3).",
        ),
    )
    assessment = RiskAssessment(
        assessment_id="ra-8",
        session_id="sess-1",
        risk_level=RiskLevel.MEDIUM,
        score=0.5,
        evidence=(
            _evidence("ev-5", EvidenceCategory.URGENCY),
            _evidence("ev-6", EvidenceCategory.CREDENTIAL_REQUEST),
        ),
        triggered_categories=(EvidenceCategory.URGENCY, EvidenceCategory.CREDENTIAL_REQUEST),
        explanation="Urgency and a credential request were observed together.",
        timestamp=datetime.now(timezone.utc),
        contributions=contributions,
    )
    assert assessment.contributions is contributions
    assert sum(c.base_points + c.interaction_points for c in assessment.contributions) == 9


def test_contributions_must_contain_only_risk_contribution_values():
    with pytest.raises(ValueError):
        RiskAssessment(
            assessment_id="ra-9",
            session_id="sess-1",
            risk_level=RiskLevel.LOW,
            score=0.1,
            evidence=(),
            triggered_categories=(),
            explanation="explanation",
            timestamp=datetime.now(timezone.utc),
            contributions=("not-a-contribution",),
        )
