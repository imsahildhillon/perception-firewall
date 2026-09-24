import pytest

from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.interfaces.errors import TranscriptBufferError
from perception_firewall.transcript.buffer import TranscriptBuffer


def _segment(segment_id, text, start_time, end_time=None):
    return TranscriptSegment(
        segment_id=segment_id,
        text=text,
        start_time=start_time,
        end_time=end_time if end_time is not None else start_time + 1.0,
        source=TranscriptSource.RECORDED_AUDIO,
    )


@pytest.fixture
def buffer():
    return TranscriptBuffer()


def test_append_accepts_transcript_segment(buffer):
    seg = _segment("seg-1", "hello", 0.0)
    buffer.append(seg)
    assert buffer.size() == 1
    assert buffer.segments() == (seg,)


def test_append_preserves_original_object(buffer):
    seg = _segment("seg-1", "hello", 0.0)
    buffer.append(seg)
    assert buffer.segments()[0] is seg


def test_append_rejects_non_segment(buffer):
    with pytest.raises(TranscriptBufferError):
        buffer.append("not a segment")


def test_append_rejects_none(buffer):
    with pytest.raises(TranscriptBufferError):
        buffer.append(None)


def test_segments_returns_immutable_snapshot(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0))
    result = buffer.segments()
    assert isinstance(result, tuple)
    with pytest.raises((AttributeError, TypeError)):
        result.append(_segment("seg-2", "world", 1.0))  # tuples have no .append


def test_mutating_returned_snapshot_does_not_affect_buffer(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0))
    snapshot = buffer.segments()
    buffer.append(_segment("seg-2", "world", 1.0))
    assert len(snapshot) == 1  # the earlier snapshot is unaffected
    assert buffer.size() == 2


def test_text_joins_in_chronological_order(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0))
    buffer.append(_segment("seg-2", "world", 1.0))
    assert buffer.text() == "hello world"


def test_text_uses_deterministic_default_separator(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0))
    buffer.append(_segment("seg-2", "world", 1.0))
    assert buffer.text(separator=" | ") == "hello | world"


def test_text_does_not_rewrite_segment_text(buffer):
    original = "Give me the OTP,   IMMEDIATELY!!"
    seg = _segment("seg-1", original, 0.0)
    buffer.append(seg)
    assert buffer.text() == seg.text  # exactly as stored on the segment


def test_clear_removes_all_segments(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0))
    buffer.append(_segment("seg-2", "world", 1.0))
    buffer.clear()
    assert buffer.size() == 0
    assert buffer.segments() == ()
    assert buffer.text() == ""


def test_size_reflects_segment_count(buffer):
    assert buffer.size() == 0
    buffer.append(_segment("seg-1", "hello", 0.0))
    assert buffer.size() == 1
    buffer.append(_segment("seg-2", "world", 1.0))
    assert buffer.size() == 2


# --- PART 9: transcript order --------------------------------------------------


def test_segments_retained_in_chronological_order(buffer):
    seg1 = _segment("seg-1", "first", 0.0)
    seg2 = _segment("seg-2", "second", 1.0)
    seg3 = _segment("seg-3", "third", 2.0)
    buffer.append(seg1)
    buffer.append(seg2)
    buffer.append(seg3)
    assert buffer.segments() == (seg1, seg2, seg3)


def test_transcript_text_is_deterministic_across_calls(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0))
    buffer.append(_segment("seg-2", "world", 1.0))
    assert buffer.text() == buffer.text()


def test_segment_ids_remain_intact(buffer):
    buffer.append(_segment("seg-alpha", "hello", 0.0))
    buffer.append(_segment("seg-beta", "world", 1.0))
    assert [s.segment_id for s in buffer.segments()] == ["seg-alpha", "seg-beta"]


def test_timestamps_remain_intact(buffer):
    buffer.append(_segment("seg-1", "hello", 0.0, end_time=1.5))
    buffer.append(_segment("seg-2", "world", 1.5, end_time=3.0))
    starts = [s.start_time for s in buffer.segments()]
    ends = [s.end_time for s in buffer.segments()]
    assert starts == [0.0, 1.5]
    assert ends == [1.5, 3.0]


def test_multiple_chunks_create_one_coherent_transcript(buffer):
    # Simulates segments arriving in separate append() calls (e.g. from
    # separate audio chunks), not all at once.
    buffer.append(_segment("seg-1", "Your bank account will be blocked today.", 0.0))
    buffer.append(_segment("seg-2", "Give me the OTP immediately.", 3.0))
    assert buffer.text() == (
        "Your bank account will be blocked today. Give me the OTP immediately."
    )


def test_clear_removes_previous_transcript_content_before_reuse(buffer):
    buffer.append(_segment("seg-1", "old content", 0.0))
    buffer.clear()
    buffer.append(_segment("seg-2", "new content", 0.0))
    assert buffer.text() == "new content"
    assert buffer.size() == 1


def test_no_cross_buffer_leakage_between_separate_instances():
    buffer_a = TranscriptBuffer()
    buffer_b = TranscriptBuffer()
    buffer_a.append(_segment("seg-1", "session A content", 0.0))
    assert buffer_b.size() == 0
    assert buffer_b.text() == ""


# --- out-of-order policy ------------------------------------------------------


def test_out_of_order_segment_is_rejected(buffer):
    buffer.append(_segment("seg-1", "second in time", 5.0))
    with pytest.raises(TranscriptBufferError):
        buffer.append(_segment("seg-2", "earlier in time", 1.0))


def test_out_of_order_rejection_does_not_corrupt_existing_buffer(buffer):
    seg1 = _segment("seg-1", "second in time", 5.0)
    buffer.append(seg1)
    with pytest.raises(TranscriptBufferError):
        buffer.append(_segment("seg-2", "earlier in time", 1.0))
    assert buffer.segments() == (seg1,)  # unchanged after the rejection


def test_equal_start_time_is_allowed():
    buffer = TranscriptBuffer()
    seg1 = _segment("seg-1", "first", 2.0, end_time=2.0)  # zero-length, allowed by domain
    seg2 = _segment("seg-2", "second", 2.0)
    buffer.append(seg1)
    buffer.append(seg2)  # equal start_time is not "out of order"
    assert buffer.size() == 2
