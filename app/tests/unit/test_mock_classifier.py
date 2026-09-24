import pytest

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import EvidenceCategory
from perception_firewall.interfaces.errors import ClassificationError
from perception_firewall.interfaces.mocks import MockTextClassifier


@pytest.fixture
def classifier():
    return MockTextClassifier()


def test_normal_scenario(classifier):
    result = classifier.classify(
        "Hello, how are you? I wanted to confirm tomorrow's meeting."
    )
    assert isinstance(result, ClassificationResult)
    assert result.indicators == ()


def test_bank_otp_scenario(classifier):
    result = classifier.classify(
        "Your bank account will be blocked today. Give me the OTP immediately."
    )
    assert EvidenceCategory.CREDENTIAL_REQUEST in result.indicators
    assert EvidenceCategory.URGENCY in result.indicators
    assert result.credential_request is not None


def test_remote_access_scenario(classifier):
    result = classifier.classify(
        "Install AnyDesk and give me remote access so I can verify your account."
    )
    assert EvidenceCategory.REMOTE_ACCESS in result.indicators
    assert result.remote_access_request is not None


def test_authority_payment_scenario(classifier):
    result = classifier.classify(
        "I am calling from the authorities. You need to transfer the "
        "payment immediately or legal action will follow."
    )
    assert EvidenceCategory.AUTHORITY in result.indicators
    assert EvidenceCategory.PAYMENT in result.indicators
    assert result.authority_claim is not None
    assert result.payment_request is not None


def test_result_is_valid_classification_result(classifier):
    result = classifier.classify("some arbitrary transcript text")
    assert isinstance(result, ClassificationResult)
    assert result.classification_id
    assert result.uncertainty is not None and 0.0 <= result.uncertainty <= 1.0


def test_empty_transcript_raises(classifier):
    with pytest.raises(ClassificationError):
        classifier.classify("")


def test_whitespace_only_transcript_raises(classifier):
    with pytest.raises(ClassificationError):
        classifier.classify("   \n\t  ")


def test_none_transcript_raises(classifier):
    with pytest.raises(ClassificationError):
        classifier.classify(None)


def test_classification_is_deterministic(classifier):
    text = "Give me the OTP immediately, your bank account will be blocked."
    first = classifier.classify(text)
    second = classifier.classify(text)
    assert first.indicators == second.indicators
    assert first.overall_assessment == second.overall_assessment
