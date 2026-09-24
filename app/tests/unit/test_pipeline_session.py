import pytest

from perception_firewall.domain.session import SessionState
from perception_firewall.interfaces.errors import SessionError
from perception_firewall.pipeline.session import Session


def test_new_session_starts_idle_with_given_id():
    session = Session("s1")
    assert session.session_id == "s1"
    assert session.state is SessionState.IDLE
    assert session.buffer.size() == 0


@pytest.mark.parametrize("session_id", [None, "", "   ", 123])
def test_invalid_session_id_raises(session_id):
    with pytest.raises(SessionError):
        Session(session_id)


def test_start_transitions_idle_to_active():
    session = Session("s1")
    session.start()
    assert session.state is SessionState.ACTIVE


def test_pause_then_resume_returns_to_active():
    session = Session("s1")
    session.start()
    session.pause()
    assert session.state is SessionState.PAUSED
    session.resume()
    assert session.state is SessionState.ACTIVE


def test_full_lifecycle_active_paused_active_ended():
    session = Session("s1")
    session.start()
    session.pause()
    session.resume()
    session.end()
    assert session.state is SessionState.ENDED


def test_start_from_active_is_invalid():
    session = Session("s1")
    session.start()
    with pytest.raises(SessionError):
        session.start()


def test_pause_from_idle_is_invalid():
    session = Session("s1")
    with pytest.raises(SessionError):
        session.pause()


def test_resume_from_idle_is_invalid():
    session = Session("s1")
    with pytest.raises(SessionError):
        session.resume()


def test_end_from_idle_is_invalid():
    session = Session("s1")
    with pytest.raises(SessionError):
        session.end()


def test_operations_on_ended_session_are_invalid():
    session = Session("s1")
    session.start()
    session.end()
    with pytest.raises(SessionError):
        session.start()
    with pytest.raises(SessionError):
        session.pause()
    with pytest.raises(SessionError):
        session.end()


def test_mark_error_from_active():
    session = Session("s1")
    session.start()
    session.mark_error()
    assert session.state is SessionState.ERROR


def test_mark_error_from_paused():
    session = Session("s1")
    session.start()
    session.pause()
    session.mark_error()
    assert session.state is SessionState.ERROR


def test_mark_error_from_idle():
    session = Session("s1")
    session.mark_error()
    assert session.state is SessionState.ERROR


def test_mark_error_on_ended_session_raises():
    session = Session("s1")
    session.start()
    session.end()
    with pytest.raises(SessionError):
        session.mark_error()


def test_reset_from_error_returns_to_idle():
    session = Session("s1")
    session.start()
    session.mark_error()
    session.reset()
    assert session.state is SessionState.IDLE


def test_reset_from_ended_returns_to_idle():
    session = Session("s1")
    session.start()
    session.end()
    session.reset()
    assert session.state is SessionState.IDLE


def test_reset_from_active_returns_to_idle():
    session = Session("s1")
    session.start()
    session.reset()
    assert session.state is SessionState.IDLE


def test_reset_preserves_session_id():
    session = Session("s1")
    session.start()
    session.end()
    session.reset()
    assert session.session_id == "s1"


def test_reset_clears_buffer():
    from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource

    session = Session("s1")
    session.start()
    session.buffer.append(
        TranscriptSegment(
            segment_id="seg-1",
            text="hello",
            start_time=0.0,
            end_time=1.0,
            source=TranscriptSource.RECORDED_AUDIO,
        )
    )
    assert session.buffer.size() == 1
    session.reset()
    assert session.buffer.size() == 0


def test_session_id_immutable_across_reset_and_lifecycle():
    session = Session("stable-id")
    session.start()
    session.pause()
    session.resume()
    session.end()
    session.reset()
    session.start()
    assert session.session_id == "stable-id"
