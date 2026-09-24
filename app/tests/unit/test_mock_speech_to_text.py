import pytest

from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.interfaces.audio import AudioChunk
from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.interfaces.mocks import MockSpeechToTextEngine


def _chunk(fixture_id):
    return AudioChunk(data=b"", sample_rate_hz=16000, channels=1, fixture_id=fixture_id)


def test_mock_returns_deterministic_segments_for_known_fixture():
    engine = MockSpeechToTextEngine()
    segments = engine.transcribe(_chunk("demo_normal"))
    assert len(segments) == 1
    assert isinstance(segments[0], TranscriptSegment)
    assert "confirm tomorrow" in segments[0].text


def test_mock_is_deterministic_across_calls():
    engine = MockSpeechToTextEngine()
    first = engine.transcribe(_chunk("demo_bank_otp"))
    second = engine.transcribe(_chunk("demo_bank_otp"))
    assert first == second


def test_mock_handles_empty_fixture():
    engine = MockSpeechToTextEngine()
    segments = engine.transcribe(_chunk("demo_silence"))
    assert segments == ()


def test_mock_rejects_none_audio():
    engine = MockSpeechToTextEngine()
    with pytest.raises(SpeechRecognitionError):
        engine.transcribe(None)


def test_mock_rejects_chunk_without_fixture_id():
    engine = MockSpeechToTextEngine()
    with pytest.raises(SpeechRecognitionError):
        engine.transcribe(_chunk(None))


def test_mock_rejects_unknown_fixture_id():
    engine = MockSpeechToTextEngine()
    with pytest.raises(SpeechRecognitionError):
        engine.transcribe(_chunk("not_a_real_fixture"))


def test_mock_accepts_custom_fixtures():
    custom_segment = TranscriptSegment(
        segment_id="custom-1",
        text="custom fixture text",
        start_time=0.0,
        end_time=1.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    engine = MockSpeechToTextEngine(fixtures={"my_fixture": (custom_segment,)})
    result = engine.transcribe(_chunk("my_fixture"))
    assert result == (custom_segment,)
