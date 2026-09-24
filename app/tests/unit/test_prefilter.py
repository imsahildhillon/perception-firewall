import datetime as dt

import pytest

from perception_firewall.domain.evidence import Evidence, EvidenceCategory, EvidenceSource
from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.interfaces.errors import EvidenceExtractionError
from perception_firewall.prefilter import RuleBasedEvidenceProvider


def _segment(text: str, segment_id: str = "seg-1", **kwargs) -> TranscriptSegment:
    defaults = dict(start_time=0.0, end_time=1.0, source=TranscriptSource.RECORDED_AUDIO)
    defaults.update(kwargs)
    return TranscriptSegment(segment_id=segment_id, text=text, **defaults)


@pytest.fixture
def provider():
    return RuleBasedEvidenceProvider()


def _categories(evidence):
    return {e.category for e in evidence}


# --- 1. empty transcript ---------------------------------------------------


def test_empty_segments_list_returns_no_evidence(provider):
    assert provider.analyze("", segments=[]) == ()


def test_no_segments_argument_returns_no_evidence(provider):
    assert provider.analyze("") == ()


# --- 2. benign conversation --------------------------------------------------


def test_benign_conversation_documents_known_false_positives(provider):
    """Known limitation (see prefilter/README.md section 8): 'bank' and
    'today' are broad common words present in the v1 pattern set, so this
    literally benign sentence still triggers AUTHORITY and URGENCY under
    the current rules. Captured here as an explicit regression, not a
    surprise.
    """
    segment = _segment(
        "Hi, how are you? The bank branch near my house is crowded today."
    )
    evidence = provider.analyze("", segments=[segment])
    assert _categories(evidence) == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.URGENCY,
    }


def test_truly_benign_conversation_with_no_keywords_produces_no_evidence(provider):
    segment = _segment("Hey, it was great catching up with you last weekend!")
    evidence = provider.analyze("", segments=[segment])
    assert evidence == ()


# --- 3-10. each category individually ---------------------------------------


def test_authority_category(provider):
    segment = _segment("I am calling from the police department.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.AUTHORITY in _categories(evidence)


def test_urgency_category(provider):
    segment = _segment("You must act now, this is urgent.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.URGENCY in _categories(evidence)


def test_threat_category(provider):
    segment = _segment("If you don't comply, legal action will follow.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.THREAT in _categories(evidence)


def test_payment_category(provider):
    segment = _segment("Please make the payment via UPI right away.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.PAYMENT in _categories(evidence)


def test_credential_request_category(provider):
    segment = _segment("Can you read me the OTP you just received?")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.CREDENTIAL_REQUEST in _categories(evidence)


def test_remote_access_category(provider):
    segment = _segment("Please install AnyDesk so I can access your screen.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.REMOTE_ACCESS in _categories(evidence)


def test_secrecy_category(provider):
    segment = _segment("Please don't tell anyone about this call.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.SECRECY in _categories(evidence)


def test_identity_pressure_category(provider):
    segment = _segment("I need you to verify your identity first.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.IDENTITY_PRESSURE in _categories(evidence)


# --- 11. multiple categories in one segment ---------------------------------


def test_multiple_categories_in_one_segment(provider):
    segment = _segment(
        "Your bank account will be blocked today. Give me the OTP immediately."
    )
    evidence = provider.analyze("", segments=[segment])
    assert _categories(evidence) == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.THREAT,
        EvidenceCategory.CREDENTIAL_REQUEST,
        EvidenceCategory.URGENCY,
    }


# --- 12. repeated pattern in one segment ------------------------------------


def test_repeated_identical_pattern_in_one_segment_is_not_duplicated(provider):
    segment = _segment("This is urgent. I repeat, this is urgent, very urgent.")
    evidence = provider.analyze("", segments=[segment])
    urgency_evidence = [e for e in evidence if e.category is EvidenceCategory.URGENCY]
    assert len(urgency_evidence) == 1


# --- 13. repeated evidence across separate segments -------------------------


def test_repeated_pattern_across_separate_segments_is_preserved(provider):
    seg1 = _segment("This is urgent.", segment_id="seg-a")
    seg2 = _segment("I said this is urgent.", segment_id="seg-b")
    evidence = provider.analyze("", segments=[seg1, seg2])
    urgency_evidence = [e for e in evidence if e.category is EvidenceCategory.URGENCY]
    assert len(urgency_evidence) == 2
    assert {e.segment_id for e in urgency_evidence} == {"seg-a", "seg-b"}


# --- 14. case-insensitive matching ------------------------------------------


@pytest.mark.parametrize(
    "text",
    ["Give me the OTP now", "give me the otp now", "Give me the Otp now"],
)
def test_case_insensitive_matching(provider, text):
    evidence = provider.analyze("", segments=[_segment(text)])
    assert EvidenceCategory.CREDENTIAL_REQUEST in _categories(evidence)


def test_bank_matches_regardless_of_capitalization(provider):
    evidence = provider.analyze("", segments=[_segment("Bank policy requires this.")])
    assert EvidenceCategory.AUTHORITY in _categories(evidence)


# --- 15. punctuation ---------------------------------------------------------


def test_punctuation_does_not_block_match(provider):
    # Trailing punctuation ("blocked,") must not prevent the phrase
    # "account will be blocked" from matching, nor "immediately!" from
    # matching "immediately" — \b treats punctuation as a boundary, not
    # as part of the word.
    segment = _segment("Your account will be blocked, immediately!")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.THREAT in _categories(evidence)
    assert EvidenceCategory.URGENCY in _categories(evidence)


def test_punctuation_at_phrase_boundary_does_not_block_match(provider):
    segment = _segment("Give me the OTP, please.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.CREDENTIAL_REQUEST in _categories(evidence)


def test_multiword_phrase_with_trailing_punctuation(provider):
    segment = _segment("You need to transfer the payment immediately or legal action will follow.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.THREAT in _categories(evidence)


# --- 16. whitespace normalization -------------------------------------------


def test_irregular_whitespace_in_multiword_phrase(provider):
    segment = _segment("You need to transfer  the   payment or legal    action will follow.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.THREAT in _categories(evidence)


def test_newlines_and_tabs_between_words(provider):
    segment = _segment("legal\n\taction will follow immediately")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.THREAT in _categories(evidence)


# --- 17. substring false-positive protection --------------------------------


def test_pin_does_not_match_spinach(provider):
    segment = _segment("I bought spinach and napkins at the store.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.CREDENTIAL_REQUEST not in _categories(evidence)


def test_pin_does_not_match_pinpoint(provider):
    segment = _segment("Can you pinpoint the exact location on the map?")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.CREDENTIAL_REQUEST not in _categories(evidence)


def test_pin_matches_as_standalone_word(provider):
    segment = _segment("Please enter your PIN to continue.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.CREDENTIAL_REQUEST in _categories(evidence)


def test_court_does_not_match_courtyard(provider):
    segment = _segment("We had coffee in the courtyard this morning.")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.AUTHORITY not in _categories(evidence)


# --- 18. Unicode text ---------------------------------------------------------


def test_unicode_surrounding_text_does_not_break_matching(provider):
    segment = _segment("यह बहुत urgent है, कृपया जल्दी reply करें।")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.URGENCY in _categories(evidence)


def test_unicode_with_emoji_does_not_break_matching(provider):
    segment = _segment("🚨 Your account will be blocked today 🚨")
    evidence = provider.analyze("", segments=[segment])
    assert EvidenceCategory.THREAT in _categories(evidence)


# --- 19. timestamp propagation ------------------------------------------------


def test_timestamp_is_set_and_recent(provider):
    before = dt.datetime.now(dt.timezone.utc)
    evidence = provider.analyze("", segments=[_segment("Please provide your OTP.")])
    after = dt.datetime.now(dt.timezone.utc)
    assert len(evidence) >= 1
    for item in evidence:
        assert item.timestamp is not None
        assert before <= item.timestamp <= after


# --- 20. segment ID propagation -----------------------------------------------


def test_segment_id_is_propagated(provider):
    segment = _segment("Please provide your OTP.", segment_id="custom-seg-id")
    evidence = provider.analyze("", segments=[segment])
    assert len(evidence) >= 1
    assert all(e.segment_id == "custom-seg-id" for e in evidence)


# --- 21. EvidenceSource.RULE provenance ---------------------------------------


def test_all_evidence_has_rule_provenance(provider):
    segment = _segment(
        "I am calling from the authorities. You need to transfer the "
        "payment immediately or legal action will follow."
    )
    evidence = provider.analyze("", segments=[segment])
    assert len(evidence) >= 1
    assert all(e.source is EvidenceSource.RULE for e in evidence)


# --- 22. evidence_text preserves original transcript --------------------------


def test_evidence_text_preserves_original_segment_text_exactly(provider):
    # TranscriptSegment itself normalizes whitespace at construction time
    # (domain layer, STEP 2) — "original" here means segment.text as
    # stored on the domain object, not the raw pre-construction string.
    segment = _segment("Give me the OTP,   IMMEDIATELY!!")
    evidence = provider.analyze("", segments=[segment])
    assert len(evidence) >= 1
    assert all(e.evidence_text == segment.text for e in evidence)
    assert segment.text == "Give me the OTP, IMMEDIATELY!!"


# --- 23. no unsupported "scam" verdict -----------------------------------------


FORBIDDEN_VERDICT_TERMS = ("scam", "scammer", "fraud", "fraudulent", "criminal")


def test_explanation_templates_never_assert_a_verdict():
    from perception_firewall.prefilter.patterns import EXPLANATION_TEMPLATES

    for template in EXPLANATION_TEMPLATES.values():
        lowered = template.lower()
        for term in FORBIDDEN_VERDICT_TERMS:
            assert term not in lowered


def test_produced_evidence_never_asserts_a_verdict(provider):
    segment = _segment(
        "I am calling from the authorities. You need to transfer the "
        "payment immediately or legal action will follow. Give me the "
        "OTP and don't tell anyone, and install AnyDesk to verify your "
        "identity."
    )
    evidence = provider.analyze("", segments=[segment])
    assert len(evidence) >= 1
    for item in evidence:
        lowered = item.explanation.lower()
        for term in FORBIDDEN_VERDICT_TERMS:
            assert term not in lowered


# --- 24. multiple transcript segments ------------------------------------------


def test_multiple_segments_each_attributed_correctly(provider):
    seg1 = _segment("Please provide your OTP.", segment_id="seg-1")
    seg2 = _segment("Install AnyDesk immediately.", segment_id="seg-2")
    evidence = provider.analyze("", segments=[seg1, seg2])

    seg1_evidence = [e for e in evidence if e.segment_id == "seg-1"]
    seg2_evidence = [e for e in evidence if e.segment_id == "seg-2"]

    assert any(e.category is EvidenceCategory.CREDENTIAL_REQUEST for e in seg1_evidence)
    assert any(e.category is EvidenceCategory.REMOTE_ACCESS for e in seg2_evidence)
    assert any(e.category is EvidenceCategory.URGENCY for e in seg2_evidence)


# --- 25. empty/whitespace-only transcript segment ------------------------------


def test_transcript_segment_rejects_whitespace_only_text_at_domain_layer():
    """The domain layer (STEP 2) already guards against this — a
    TranscriptSegment cannot be constructed with empty/whitespace-only
    text, so the prefilter never actually receives one.
    """
    with pytest.raises(ValueError):
        TranscriptSegment(
            segment_id="seg-empty",
            text="   ",
            start_time=0.0,
            end_time=1.0,
            source=TranscriptSource.RECORDED_AUDIO,
        )


# --- 26. malformed input / error handling --------------------------------------


def test_none_transcript_text_raises(provider):
    with pytest.raises(EvidenceExtractionError):
        provider.analyze(None, segments=[])


def test_non_string_transcript_text_raises(provider):
    with pytest.raises(EvidenceExtractionError):
        provider.analyze(12345, segments=[])


def test_string_passed_as_segments_raises(provider):
    with pytest.raises(EvidenceExtractionError):
        provider.analyze("", segments="not a list of segments")


def test_non_sequence_segments_raises(provider):
    with pytest.raises(EvidenceExtractionError):
        provider.analyze("", segments={"not": "a sequence"})


def test_segments_containing_non_transcript_segment_raises(provider):
    with pytest.raises(EvidenceExtractionError):
        provider.analyze("", segments=[_segment("valid segment"), "not a segment"])


def test_segments_containing_plain_dict_raises(provider):
    with pytest.raises(EvidenceExtractionError):
        provider.analyze("", segments=[{"text": "fake segment"}])


# --- Domain example scenarios from the task spec --------------------------------


def test_scenario_bank_otp(provider):
    segment = _segment(
        "Your bank account will be blocked today. Give me the OTP immediately."
    )
    evidence = provider.analyze("", segments=[segment])
    assert _categories(evidence) == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.THREAT,
        EvidenceCategory.CREDENTIAL_REQUEST,
        EvidenceCategory.URGENCY,
    }


def test_scenario_remote_access(provider):
    segment = _segment(
        "Install AnyDesk and give me remote access so I can verify your account."
    )
    evidence = provider.analyze("", segments=[segment])
    assert _categories(evidence) == {
        EvidenceCategory.REMOTE_ACCESS,
        EvidenceCategory.IDENTITY_PRESSURE,
    }


def test_scenario_authority_payment(provider):
    segment = _segment(
        "I am calling from the authorities. You need to transfer the "
        "payment immediately or legal action will follow."
    )
    evidence = provider.analyze("", segments=[segment])
    assert _categories(evidence) == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.PAYMENT,
        EvidenceCategory.URGENCY,
        EvidenceCategory.THREAT,
    }


# --- interface contract sanity ---------------------------------------------


def test_returns_evidence_sequence(provider):
    result = provider.analyze("", segments=[_segment("Please provide your OTP.")])
    assert isinstance(result, tuple)
    assert all(isinstance(item, Evidence) for item in result)
