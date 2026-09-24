"""Session — deterministic lifecycle management for one monitoring session.

Wraps a ``session_id``, its ``SessionState``, and a per-session
``TranscriptBuffer``, enforcing valid state transitions. A ``Session``
does not itself perform speech recognition, evidence extraction,
classification, or risk scoring — see ``pipeline/orchestrator.py`` for
that. See pipeline/README.md for the full lifecycle diagram and rationale.
"""

from __future__ import annotations

from perception_firewall.domain.session import SessionState
from perception_firewall.interfaces.errors import SessionError
from perception_firewall.transcript.buffer import TranscriptBuffer


class Session:
    """One monitoring session: identity, lifecycle state, and transcript.

    ``session_id`` is fixed for the life of this object (including across
    ``reset()`` — a reset session is the same identity starting over, not
    a new one). Two ``Session`` objects with different ``session_id``
    values never share any state: each owns its own ``TranscriptBuffer``,
    and a ``RiskEngine``'s own per-session hysteresis (see
    ``risk/state.py``) is likewise keyed by ``session_id``.
    """

    def __init__(self, session_id: str) -> None:
        if session_id is None or not isinstance(session_id, str) or not session_id.strip():
            raise SessionError("Session requires a non-empty session_id")
        self._session_id = session_id
        self._state = SessionState.IDLE
        self._buffer = TranscriptBuffer()

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def buffer(self) -> TranscriptBuffer:
        return self._buffer

    def _require_state(self, *expected: SessionState, operation: str) -> None:
        if self._state not in expected:
            expected_names = " or ".join(state.value for state in expected)
            raise SessionError(
                f"Cannot {operation}(): session is {self._state.value}, "
                f"expected {expected_names} (session_id={self._session_id!r})"
            )

    def start(self) -> None:
        """IDLE -> ACTIVE."""
        self._require_state(SessionState.IDLE, operation="start")
        self._state = SessionState.ACTIVE

    def pause(self) -> None:
        """ACTIVE -> PAUSED."""
        self._require_state(SessionState.ACTIVE, operation="pause")
        self._state = SessionState.PAUSED

    def resume(self) -> None:
        """PAUSED -> ACTIVE.

        Deliberately distinct from ``start()`` even though both land on
        ACTIVE: ``resume()`` is only valid from PAUSED — resuming a
        session that was never paused (e.g. from IDLE) is rejected, so
        the two operations cannot be used interchangeably.
        """
        self._require_state(SessionState.PAUSED, operation="resume")
        self._state = SessionState.ACTIVE

    def end(self) -> None:
        """ACTIVE or PAUSED -> ENDED (terminal)."""
        self._require_state(SessionState.ACTIVE, SessionState.PAUSED, operation="end")
        self._state = SessionState.ENDED

    def mark_error(self) -> None:
        """Explicitly transition to ERROR (terminal via ordinary
        transitions). Allowed from any state except ENDED — an ended
        session is already terminal and cannot subsequently fail.

        Not gated by ``_VALID_TRANSITIONS`` because a failure can occur
        during any operation the session is otherwise willing to accept;
        this is the mechanism by which the orchestrator (see
        ``pipeline/orchestrator.py``) reports a component failure onto
        the session, per the "session should enter ERROR where
        appropriate" requirement.
        """
        if self._state is SessionState.ENDED:
            raise SessionError(
                f"Cannot mark an ENDED session as ERROR "
                f"(session_id={self._session_id!r})"
            )
        self._state = SessionState.ERROR

    def reset(self) -> None:
        """Clear this session's buffered transcript and return it to IDLE.

        Allowed unconditionally, from any state — including ERROR and
        ENDED — as the designated escape hatch from those terminal
        states. ``session_id`` is preserved.

        This clears buffer and lifecycle state only. Clearing a
        ``RiskEngine``'s hysteresis state for this ``session_id`` is a
        separate concern (the engine, not the session, owns that state)
        — see ``ApplicationPipeline.reset_session()`` in
        ``pipeline/orchestrator.py`` for the combined operation.
        """
        self._buffer.clear()
        self._state = SessionState.IDLE
