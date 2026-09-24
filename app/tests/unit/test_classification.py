import pytest

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import EvidenceCategory


def test_valid_result():
    result = ClassificationResult(
        classification_id="cls-1",
        indicators=(EvidenceCategory.CREDENTIAL_REQUEST, EvidenceCategory.URGENCY),
        credential_request="Caller asked for a one-time passcode.",
        urgency_description="Caller emphasized acting before the code expires.",
        overall_assessment="Multiple pressure indicators observed in this segment.",
        uncertainty=0.2,
    )
    assert EvidenceCategory.CREDENTIAL_REQUEST in result.indicators
    assert result.credential_request is not None


def test_result_with_uncertainty_only():
    result = ClassificationResult(
        classification_id="cls-2",
        uncertainty=0.9,
    )
    assert result.uncertainty == 0.9
    assert result.indicators == ()
    assert result.overall_assessment is None


def test_no_indicators_is_valid():
    result = ClassificationResult(classification_id="cls-3")
    assert result.indicators == ()
    assert result.requested_action is None


def test_multiple_indicators():
    indicators = (
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.THREAT,
        EvidenceCategory.PAYMENT,
    )
    result = ClassificationResult(
        classification_id="cls-4",
        indicators=indicators,
    )
    assert result.indicators == indicators


@pytest.mark.parametrize("uncertainty", [-0.1, 1.1])
def test_uncertainty_out_of_bounds_raises(uncertainty):
    with pytest.raises(ValueError):
        ClassificationResult(classification_id="cls-5", uncertainty=uncertainty)


def test_indicators_must_be_evidence_categories():
    with pytest.raises(ValueError):
        ClassificationResult(classification_id="cls-6", indicators=("not-a-category",))
