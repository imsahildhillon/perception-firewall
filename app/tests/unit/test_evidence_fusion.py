from datetime import datetime, timezone

import pytest

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import Evidence, EvidenceCategory, EvidenceSource
from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.evidence import EvidenceFusion
from perception_firewall.interfaces.errors import EvidenceFusionError
from perception_firewall.prefilter import RuleBasedEvidenceProvider
from perception_firewall.risk.engine import DeterministicRiskEngine


def _rule_evidence(
    category: EvidenceCategory,
    evidence_id: str = "rule-1",
    segment_id: str = "seg-1",
    text: str = "Give me the OTP.",
    explanation: str = "A credential was requested.",
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        category=category,
        source=EvidenceSource.RULE,
        evidence_text=text,
        explanation=explanation,
        timestamp=datetime.now(timezone.utc),
        segment_id=segment_id,
    )


def _classification(**kwargs) -> ClassificationResult:
    defaults = dict(classification_id="cls-1")
    defaults.update(kwargs)
    return ClassificationResult(**defaults)


@pytest.fixture
def fusion():
    return EvidenceFusion()


def _by_source(evidence, source: EvidenceSource):
    return tuple(e for e in evidence if e.source is source)


# --- A. rule evidence passes through unchanged --------------------------------


def test_rule_evidence_passes_through_unchanged(fusion):
    rule_ev = _rule_evidence(EvidenceCategory.CREDENTIAL_REQUEST)
    result = fusion.fuse([rule_ev], classification_result=None)
    assert result == (rule_ev,)
    assert result[0] is rule_ev  # same object identity, not a copy


def test_multiple_rule_evidence_preserved_in_order(fusion):
    ev1 = _rule_evidence(EvidenceCategory.AUTHORITY, "rule-1", "seg-1")
    ev2 = _rule_evidence(EvidenceCategory.URGENCY, "rule-2", "seg-2")
    result = fusion.fuse([ev1, ev2], classification_result=None)
    assert result == (ev1, ev2)


# --- B-H. meaningful AI fields produce the right category ---------------------


def test_meaningful_payment_request_produces_ai_payment_evidence(fusion):
    result = fusion.fuse([], _classification(payment_request="Caller demanded a UPI transfer."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.PAYMENT
    assert ai[0].source is EvidenceSource.AI
    assert ai[0].evidence_text.startswith("AI interpretation: ")
    assert "UPI transfer" in ai[0].evidence_text


def test_meaningful_credential_request_produces_ai_credential_evidence(fusion):
    result = fusion.fuse([], _classification(credential_request="Caller asked for the OTP."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.CREDENTIAL_REQUEST


def test_meaningful_remote_access_request_produces_ai_remote_access_evidence(fusion):
    result = fusion.fuse([], _classification(remote_access_request="Caller asked to install AnyDesk."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.REMOTE_ACCESS


def test_meaningful_secrecy_request_produces_ai_secrecy_evidence(fusion):
    result = fusion.fuse([], _classification(secrecy_request="Caller asked to keep this confidential."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.SECRECY


def test_meaningful_identity_pressure_produces_ai_identity_pressure_evidence(fusion):
    result = fusion.fuse([], _classification(identity_pressure="Caller asked to verify identity."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.IDENTITY_PRESSURE


def test_meaningful_urgency_description_produces_ai_urgency_evidence(fusion):
    result = fusion.fuse([], _classification(urgency_description="Caller emphasized acting immediately."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.URGENCY


def test_meaningful_authority_claim_produces_ai_authority_evidence(fusion):
    result = fusion.fuse([], _classification(authority_claim="Caller claimed to be a police officer."))
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].category is EvidenceCategory.AUTHORITY


# --- I. empty AI fields produce no evidence ------------------------------------


def test_all_none_fields_produce_no_ai_evidence(fusion):
    result = fusion.fuse([], _classification())
    assert _by_source(result, EvidenceSource.AI) == ()


# --- J. whitespace AI fields produce no evidence --------------------------------


def test_whitespace_only_fields_produce_no_ai_evidence(fusion):
    result = fusion.fuse(
        [],
        _classification(
            payment_request="   ",
            credential_request="\t\n",
            urgency_description="",
        ),
    )
    assert _by_source(result, EvidenceSource.AI) == ()


# --- K. overall_assessment does not become evidence -----------------------------


def test_overall_assessment_does_not_become_evidence(fusion):
    result = fusion.fuse(
        [], _classification(overall_assessment="Several pressure indicators observed.")
    )
    assert _by_source(result, EvidenceSource.AI) == ()


# --- L. uncertainty does not become evidence -------------------------------------


def test_uncertainty_does_not_become_evidence(fusion):
    result = fusion.fuse([], _classification(uncertainty=0.9))
    assert _by_source(result, EvidenceSource.AI) == ()


def test_uncertainty_never_becomes_confidence_even_when_evidence_is_produced(fusion):
    result = fusion.fuse(
        [], _classification(payment_request="Caller demanded payment.", uncertainty=0.1)
    )
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 1
    assert ai[0].confidence is None


# --- M. RULE and AI evidence for same category can coexist -----------------------


def test_rule_and_ai_evidence_for_same_category_coexist(fusion):
    rule_ev = _rule_evidence(
        EvidenceCategory.CREDENTIAL_REQUEST, "rule-otp", "seg-1", "Send me your OTP."
    )
    classification = _classification(
        credential_request="The conversation appears to involve a credential request."
    )
    result = fusion.fuse([rule_ev], classification)
    credential_items = [e for e in result if e.category is EvidenceCategory.CREDENTIAL_REQUEST]
    assert len(credential_items) == 2
    assert {e.source for e in credential_items} == {EvidenceSource.RULE, EvidenceSource.AI}


# --- N. AI evidence never fabricates transcript timestamps -----------------------


def test_ai_evidence_has_no_timestamp_when_classification_result_has_none(fusion):
    result = fusion.fuse([], _classification(payment_request="Caller demanded payment."))
    ai = _by_source(result, EvidenceSource.AI)
    assert ai[0].timestamp is None


def test_ai_evidence_propagates_classification_result_timestamp_when_present(fusion):
    ts = datetime.now(timezone.utc)
    result = fusion.fuse(
        [], _classification(payment_request="Caller demanded payment.", timestamp=ts)
    )
    ai = _by_source(result, EvidenceSource.AI)
    assert ai[0].timestamp == ts


# --- O. AI evidence never fabricates segment IDs ----------------------------------


def test_ai_evidence_has_no_segment_id_when_classification_result_has_none(fusion):
    result = fusion.fuse([], _classification(payment_request="Caller demanded payment."))
    ai = _by_source(result, EvidenceSource.AI)
    assert ai[0].segment_id is None


def test_ai_evidence_propagates_classification_result_segment_id_when_present(fusion):
    result = fusion.fuse(
        [], _classification(payment_request="Caller demanded payment.", segment_id="seg-42")
    )
    ai = _by_source(result, EvidenceSource.AI)
    assert ai[0].segment_id == "seg-42"


def test_dangling_segment_id_is_dropped_not_propagated(fusion):
    real_segment = TranscriptSegment(
        segment_id="seg-real",
        text="Please send the payment.",
        start_time=0.0,
        end_time=1.0,
        source=TranscriptSource.RECORDED_AUDIO,
    )
    classification = _classification(
        payment_request="Caller demanded payment.", segment_id="seg-does-not-exist"
    )
    result = fusion.fuse([], classification, transcript_segments=[real_segment])
    ai = _by_source(result, EvidenceSource.AI)
    assert ai[0].segment_id is None


def test_matching_segment_id_is_propagated_when_validated(fusion):
    real_segment = TranscriptSegment(
        segment_id="seg-real",
        text="Please send the payment.",
        start_time=0.0,
        end_time=1.0,
        source=TranscriptSource.RECORDED_AUDIO,
    )
    classification = _classification(
        payment_request="Caller demanded payment.", segment_id="seg-real"
    )
    result = fusion.fuse([], classification, transcript_segments=[real_segment])
    ai = _by_source(result, EvidenceSource.AI)
    assert ai[0].segment_id == "seg-real"


# --- P. fusion is deterministic ----------------------------------------------------


def test_fusion_is_deterministic():
    rule_ev = _rule_evidence(EvidenceCategory.URGENCY)
    classification = _classification(
        payment_request="Caller demanded payment.",
        authority_claim="Caller claimed to be from the bank.",
    )
    first = EvidenceFusion().fuse([rule_ev], classification)
    second = EvidenceFusion().fuse([rule_ev], classification)
    assert first == second


# --- Q. repeated invocation does not create different output -----------------------


def test_repeated_invocation_on_same_instance_is_stable(fusion):
    rule_ev = _rule_evidence(EvidenceCategory.URGENCY)
    classification = _classification(payment_request="Caller demanded payment.")
    results = [fusion.fuse([rule_ev], classification) for _ in range(5)]
    assert all(r == results[0] for r in results)


# --- R. duplicate AI findings are not unnecessarily duplicated ---------------------


def test_fully_populated_classification_produces_exactly_one_item_per_category(fusion):
    classification = _classification(
        authority_claim="a",
        urgency_description="b",
        payment_request="c",
        credential_request="d",
        remote_access_request="e",
        secrecy_request="f",
        identity_pressure="g",
    )
    result = fusion.fuse([], classification)
    ai = _by_source(result, EvidenceSource.AI)
    assert len(ai) == 7
    categories = [e.category for e in ai]
    assert len(categories) == len(set(categories))  # no duplicates


# --- S. existing risk engine can consume fused evidence -----------------------------


def test_risk_engine_can_consume_fused_evidence(fusion):
    rule_ev = _rule_evidence(EvidenceCategory.URGENCY, text="This is urgent.")
    classification = _classification(
        credential_request="Caller asked for the OTP.",
    )
    fused = fusion.fuse([rule_ev], classification)

    engine = DeterministicRiskEngine()
    assessment = engine.assess(fused, session_id="s-fusion-consume")
    assert len(assessment.evidence) == 2
    assert assessment.risk_level is not None


# --- T. existing tests continue passing --------------------------------------------
# (verified by running the full suite — see the STEP 6 report)


# --- validation / error handling -----------------------------------------------------


def test_none_rule_evidence_raises(fusion):
    with pytest.raises(EvidenceFusionError):
        fusion.fuse(None, None)


def test_non_sequence_rule_evidence_raises(fusion):
    with pytest.raises(EvidenceFusionError):
        fusion.fuse("not a sequence", None)


def test_rule_evidence_containing_non_evidence_raises(fusion):
    with pytest.raises(EvidenceFusionError):
        fusion.fuse([_rule_evidence(EvidenceCategory.AUTHORITY), "not evidence"], None)


def test_invalid_classification_result_type_raises(fusion):
    with pytest.raises(EvidenceFusionError):
        fusion.fuse([], "not a classification result")


def test_non_sequence_transcript_segments_raises(fusion):
    with pytest.raises(EvidenceFusionError):
        fusion.fuse([], None, transcript_segments="not a sequence")


def test_transcript_segments_containing_wrong_type_raises(fusion):
    with pytest.raises(EvidenceFusionError):
        fusion.fuse([], None, transcript_segments=["not a segment"])


# --- integration test: prefilter -> AI classification -> fusion -> risk engine ------


def test_end_to_end_authority_urgency_payment_scenario():
    """Transcript -> RuleBasedEvidenceProvider -> RULE evidence, plus a
    synthetic ClassificationResult -> AI evidence, fused together and fed
    to DeterministicRiskEngine. No real LLM is used — the
    ClassificationResult is hand-constructed to simulate one.
    """
    segment = TranscriptSegment(
        segment_id="seg-e2e-1",
        text=(
            "I am calling from the authorities. You need to transfer the "
            "payment immediately or legal action will follow."
        ),
        start_time=0.0,
        end_time=5.0,
        source=TranscriptSource.RECORDED_AUDIO,
    )
    rule_evidence = RuleBasedEvidenceProvider().analyze("", segments=[segment])
    assert {e.category for e in rule_evidence} == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.URGENCY,
        EvidenceCategory.THREAT,
        EvidenceCategory.PAYMENT,
    }
    assert all(e.source is EvidenceSource.RULE for e in rule_evidence)

    classification = ClassificationResult(
        classification_id="cls-e2e-1",
        indicators=(EvidenceCategory.AUTHORITY, EvidenceCategory.PAYMENT),
        authority_claim="Caller claims to be calling from a government authority.",
        payment_request="Caller is demanding an immediate payment.",
        overall_assessment="Caller combines an authority claim with a payment demand.",
        uncertainty=0.15,
        segment_id="seg-e2e-1",
    )

    fusion = EvidenceFusion()
    fused = fusion.fuse(rule_evidence, classification, transcript_segments=[segment])

    rule_items = _by_source(fused, EvidenceSource.RULE)
    ai_items = _by_source(fused, EvidenceSource.AI)
    assert len(rule_items) == len(rule_evidence)
    assert len(ai_items) == 2  # authority_claim, payment_request
    assert {e.category for e in ai_items} == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.PAYMENT,
    }
    for item in ai_items:
        assert item.segment_id == "seg-e2e-1"  # validated against real segment

    engine = DeterministicRiskEngine()
    first_assessment = engine.assess(fused, session_id="s-e2e-1")
    second_assessment = DeterministicRiskEngine().assess(fused, session_id="s-e2e-2")

    # Deterministic: two independent engine instances given the same
    # fused evidence produce the same raw contribution breakdown.
    first_raw = sum(c.base_points + c.interaction_points for c in first_assessment.contributions)
    second_raw = sum(c.base_points + c.interaction_points for c in second_assessment.contributions)
    assert first_raw == second_raw
    assert first_assessment.risk_level is second_assessment.risk_level

    # AUTHORITY, URGENCY, THREAT, PAYMENT categories all present (AI items
    # duplicate AUTHORITY/PAYMENT by category but risk scoring dedupes by
    # category presence regardless of source, so this doesn't change which
    # categories are triggered vs. RULE evidence alone).
    assert set(first_assessment.triggered_categories) == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.URGENCY,
        EvidenceCategory.THREAT,
        EvidenceCategory.PAYMENT,
    }
