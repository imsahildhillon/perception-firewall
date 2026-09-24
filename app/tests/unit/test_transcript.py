import pytest

from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource


def test_valid_segment():
    segment = TranscriptSegment(
        segment_id="seg-1",
        text="Give me the OTP immediately.",
        start_time=0.0,
        end_time=2.5,
        source=TranscriptSource.LIVE_AUDIO,
    )
    assert segment.text == "Give me the OTP immediately."
    assert segment.duration == 2.5


def test_text_normalization_collapses_whitespace():
    segment = TranscriptSegment(
        segment_id="seg-2",
        text="  hello   world  \n",
        start_time=0.0,
        end_time=1.0,
        source=TranscriptSource.RECORDED_AUDIO,
    )
    assert segment.text == "hello world"


def test_empty_text_raises():
    with pytest.raises(ValueError):
        TranscriptSegment(
            segment_id="seg-3",
            text="   ",
            start_time=0.0,
            end_time=1.0,
            source=TranscriptSource.LIVE_AUDIO,
        )


def test_non_meaningful_text_raises():
    with pytest.raises(ValueError):
        TranscriptSegment(
            segment_id="seg-4",
            text="...???",
            start_time=0.0,
            end_time=1.0,
            source=TranscriptSource.LIVE_AUDIO,
        )


def test_negative_start_time_raises():
    with pytest.raises(ValueError):
        TranscriptSegment(
            segment_id="seg-5",
            text="hello",
            start_time=-1.0,
            end_time=1.0,
            source=TranscriptSource.LIVE_AUDIO,
        )


def test_end_before_start_raises():
    with pytest.raises(ValueError):
        TranscriptSegment(
            segment_id="seg-6",
            text="hello",
            start_time=5.0,
            end_time=1.0,
            source=TranscriptSource.LIVE_AUDIO,
        )


def test_zero_length_segment_is_allowed():
    segment = TranscriptSegment(
        segment_id="seg-7",
        text="hello",
        start_time=3.0,
        end_time=3.0,
        source=TranscriptSource.MANUAL_TEXT,
    )
    assert segment.duration == 0.0
