import pytest

from perception_firewall.domain.evidence import EvidenceCategory, EvidenceSource
from perception_firewall.domain.risk import RiskLevel
from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.evidence import EvidenceFusion
from perception_firewall.interfaces.audio import AudioChunk
from perception_firewall.interfaces.errors import (
    PerceptionFirewallError,
    SessionError,
    TranscriptBufferError,
)
from perception_firewall.interfaces.mocks import MockSpeechToTextEngine, MockTextClassifier
from perception_firewall.pipeline import ApplicationPipeline, Session
from perception_firewall.prefilter import RuleBasedEvidenceProvider
from perception_firewall.risk.engine import DeterministicRiskEngine


def _new_pipeline():
    return ApplicationPipeline(
        speech_to_text=MockSpeechToTextEngine(),
        text_classifier=MockTextClassifier(),
        evidence_provider=RuleBasedEvidenceProvider(),
        evidence_fusion=EvidenceFusion(),
        risk_engine=DeterministicRiskEngine(),
    )


def _chunk(fixture_id, sequence_number=0):
    return AudioChunk(
        data=b"", sample_rate_hz=16000, channels=1,
        sequence_number=sequence_number, fixture_id=fixture_id,
    )


def _active_session(session_id):
    session = Session(session_id)
    session.start()
    return session


# --- A. benign conversation -----------------------------------------------------


def test_scenario_a_benign_conversation():
    pipeline = _new_pipeline()
    session = _active_session("scenario-a")

    assessment = pipeline.process_audio_chunk(session, _chunk("demo_normal"))

    assert session.buffer.size() == 1
    assert assessment.risk_level is RiskLevel.SAFE
    assert assessment.contributions == ()


# --- B. bank OTP / social-engineering conversation -------------------------------


def test_scenario_b_bank_otp():
    pipeline = _new_pipeline()
    session = _active_session("scenario-b")

    assessment = pipeline.process_audio_chunk(session, _chunk("demo_bank_otp"))

    sources = {e.source for e in assessment.evidence}
    assert sources == {EvidenceSource.RULE, EvidenceSource.AI}
    categories = {e.category for e in assessment.evidence}
    assert EvidenceCategory.CREDENTIAL_REQUEST in categories
    assert EvidenceCategory.URGENCY in categories
    assert assessment.risk_level is RiskLevel.CRITICAL


# --- C. remote-access conversation ------------------------------------------------


def test_scenario_c_remote_access():
    pipeline = _new_pipeline()
    session = _active_session("scenario-c")

    assessment = pipeline.process_audio_chunk(session, _chunk("demo_remote_access"))

    categories = {e.category for e in assessment.evidence}
    assert EvidenceCategory.REMOTE_ACCESS in categories
    assert EvidenceCategory.IDENTITY_PRESSURE in categories
    # REMOTE_ACCESS (4) + IDENTITY_PRESSURE (2) = 6 raw points; no
    # interaction bonus is configured for this pair (see risk/config.py),
    # so this lands at HIGH, not CRITICAL.
    assert assessment.risk_level is RiskLevel.HIGH


# --- D. authority + payment conversation ------------------------------------------


def test_scenario_d_authority_payment():
    pipeline = _new_pipeline()
    session = _active_session("scenario-d")

    assessment = pipeline.process_audio_chunk(session, _chunk("demo_authority_payment"))

    categories = {e.category for e in assessment.evidence}
    assert EvidenceCategory.AUTHORITY in categories
    assert EvidenceCategory.URGENCY in categories
    assert EvidenceCategory.THREAT in categories
    assert EvidenceCategory.PAYMENT in categories
    assert assessment.risk_level is RiskLevel.CRITICAL


# --- E. session isolation -----------------------------------------------------------


def test_scenario_e_session_isolation_suspicious_then_benign():
    pipeline = _new_pipeline()

    session_a = _active_session("isolation-a")
    result_a = pipeline.process_audio_chunk(session_a, _chunk("demo_bank_otp"))
    assert result_a.risk_level is RiskLevel.CRITICAL

    pipeline.reset_session(session_a)

    session_b = Session("isolation-b")
    session_b.start()
    result_b = pipeline.process_audio_chunk(session_b, _chunk("demo_normal"))

    assert result_b.risk_level is RiskLevel.SAFE
    assert session_b.buffer.size() == 1
    # No evidence from session A's bank/OTP transcript leaked into B.
    assert all(
        e.segment_id is None or not e.segment_id.startswith("demo_bank_otp")
        for e in result_b.evidence
    )
    assert session_a.session_id != session_b.session_id


def test_scenario_e_session_isolation_benign_then_suspicious():
    pipeline = _new_pipeline()

    session_a = _active_session("isolation-benign")
    result_a = pipeline.process_audio_chunk(session_a, _chunk("demo_normal"))
    assert result_a.risk_level is RiskLevel.SAFE

    session_b = _active_session("isolation-suspicious")
    result_b = pipeline.process_audio_chunk(session_b, _chunk("demo_bank_otp"))

    # A prior benign session must not dampen a later, unrelated suspicious one.
    assert result_b.risk_level is RiskLevel.CRITICAL


def test_scenario_e_buffers_are_fully_independent():
    pipeline = _new_pipeline()
    session_a = _active_session("buf-a")
    session_b = _active_session("buf-b")

    pipeline.process_audio_chunk(session_a, _chunk("demo_bank_otp"))
    assert session_b.buffer.size() == 0
    assert session_b.buffer.text() == ""


def test_reset_session_clears_hysteresis_not_just_buffer():
    pipeline = _new_pipeline()
    session = _active_session("reset-hysteresis")
    high = pipeline.process_audio_chunk(session, _chunk("demo_bank_otp"))
    assert high.risk_level is RiskLevel.CRITICAL

    pipeline.reset_session(session)
    session.start()
    after_reset = pipeline.process_audio_chunk(session, _chunk("demo_normal"))
    assert after_reset.risk_level is RiskLevel.SAFE


# --- F. repeated processing --------------------------------------------------------


def test_scenario_f_repeated_processing_is_deterministic():
    pipeline = _new_pipeline()
    session = _active_session("repeat")

    first = pipeline.process_audio_chunk(session, _chunk("demo_bank_otp", 0))
    second_categories_first_call = {e.category for e in first.evidence}

    # Process the exact same fixture content again (simulating a repeat).
    session_2 = _active_session("repeat-2")
    second = pipeline.process_audio_chunk(session_2, _chunk("demo_bank_otp", 0))

    assert second_categories_first_call == {e.category for e in second.evidence}
    assert first.risk_level == second.risk_level


def test_scenario_f_repeated_processing_does_not_uncontrolled_escalate():
    pipeline = _new_pipeline()
    session = _active_session("no-runaway-escalation")

    first = pipeline.process_audio_chunk(session, _chunk("demo_bank_otp", 0))
    assert first.risk_level is RiskLevel.CRITICAL
    raw_first = sum(c.base_points + c.interaction_points for c in first.contributions)

    # Continue the same session's transcript with more segments repeating
    # the same categories (later in time, so the buffer's chronological
    # ordering is respected). Repeated categories must not multiply the
    # score, and CRITICAL is already the ceiling.
    repeat_segment = TranscriptSegment(
        segment_id="repeat-otp",
        text="Please give me the OTP again, immediately.",
        start_time=10.0,
        end_time=12.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    second = pipeline.process_segments(session, [repeat_segment])
    assert second.risk_level is RiskLevel.CRITICAL
    raw_second = sum(c.base_points + c.interaction_points for c in second.contributions)
    assert raw_second == raw_first  # no growth from reprocessing the same categories


# --- direct process_segments() contract --------------------------------------------


def test_process_segments_accepts_transcript_segments_directly():
    pipeline = _new_pipeline()
    session = _active_session("direct-segments")
    segment = TranscriptSegment(
        segment_id="seg-1",
        text="Give me the OTP immediately.",
        start_time=0.0,
        end_time=2.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    assessment = pipeline.process_segments(session, [segment])
    assert session.buffer.size() == 1
    assert assessment.risk_level is not None


def test_process_segments_with_none_reassesses_existing_buffer():
    pipeline = _new_pipeline()
    session = _active_session("reassess")
    segment = TranscriptSegment(
        segment_id="seg-1",
        text="Give me the OTP immediately.",
        start_time=0.0,
        end_time=2.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    pipeline.process_segments(session, [segment])
    second = pipeline.process_segments(session, None)  # no new input
    assert session.buffer.size() == 1  # nothing new appended
    assert second.risk_level is not None


def test_process_segments_appended_in_multiple_calls_forms_one_transcript():
    pipeline = _new_pipeline()
    session = _active_session("multi-call")
    seg1 = TranscriptSegment(
        segment_id="seg-1", text="Your bank account will be blocked today.",
        start_time=0.0, end_time=2.0, source=TranscriptSource.MANUAL_TEXT,
    )
    seg2 = TranscriptSegment(
        segment_id="seg-2", text="Give me the OTP immediately.",
        start_time=2.0, end_time=4.0, source=TranscriptSource.MANUAL_TEXT,
    )
    pipeline.process_segments(session, [seg1])
    assessment = pipeline.process_segments(session, [seg2])
    assert session.buffer.size() == 2
    assert session.buffer.text() == (
        "Your bank account will be blocked today. Give me the OTP immediately."
    )
    assert assessment.risk_level is RiskLevel.CRITICAL


# --- PART 7: error handling ---------------------------------------------------------


def test_process_requires_active_session():
    pipeline = _new_pipeline()
    session = Session("not-started")  # still IDLE
    with pytest.raises(SessionError):
        pipeline.process_audio_chunk(session, _chunk("demo_normal"))


def test_process_rejects_non_session_object():
    pipeline = _new_pipeline()
    with pytest.raises(SessionError):
        pipeline.process_segments("not a session", [])


def test_unknown_fixture_id_raises_speech_recognition_error_and_marks_error():
    pipeline = _new_pipeline()
    session = _active_session("bad-fixture")
    with pytest.raises(PerceptionFirewallError):
        pipeline.process_audio_chunk(session, _chunk("no_such_fixture"))
    from perception_firewall.domain.session import SessionState

    assert session.state is SessionState.ERROR


def test_malformed_segments_type_raises_and_marks_error():
    pipeline = _new_pipeline()
    session = _active_session("bad-segments")
    with pytest.raises(TranscriptBufferError):
        pipeline.process_segments(session, "not a sequence")
    from perception_firewall.domain.session import SessionState

    assert session.state is SessionState.ERROR


def test_out_of_order_segment_raises_and_marks_error():
    pipeline = _new_pipeline()
    session = _active_session("out-of-order")
    seg_late = TranscriptSegment(
        segment_id="seg-1", text="later", start_time=10.0, end_time=11.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    seg_early = TranscriptSegment(
        segment_id="seg-2", text="earlier", start_time=1.0, end_time=2.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    pipeline.process_segments(session, [seg_late])
    with pytest.raises(TranscriptBufferError):
        pipeline.process_segments(session, [seg_early])
    from perception_firewall.domain.session import SessionState

    assert session.state is SessionState.ERROR


def test_failure_does_not_produce_a_partial_risk_assessment():
    pipeline = _new_pipeline()
    session = _active_session("no-partial-result")
    try:
        pipeline.process_audio_chunk(session, _chunk("no_such_fixture"))
        assert False, "expected an exception"
    except PerceptionFirewallError:
        pass
    # The failed call must not have produced any usable return value; the
    # exception is the only outcome. Nothing further to assert on a
    # non-existent return value — the try/except above is the proof.
