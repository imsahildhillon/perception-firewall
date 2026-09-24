import pytest

from perception_firewall.domain.session import SessionState


@pytest.mark.parametrize(
    "state",
    [
        SessionState.IDLE,
        SessionState.ACTIVE,
        SessionState.PAUSED,
        SessionState.ENDED,
        SessionState.ERROR,
    ],
)
def test_all_valid_states(state):
    assert isinstance(state, SessionState)


def test_state_values_are_stable_strings():
    assert SessionState.IDLE.value == "idle"
    assert SessionState.ACTIVE.value == "active"
    assert SessionState.PAUSED.value == "paused"
    assert SessionState.ENDED.value == "ended"
    assert SessionState.ERROR.value == "error"
