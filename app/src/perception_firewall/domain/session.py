"""Session lifecycle domain model."""

from __future__ import annotations

from enum import Enum


class SessionState(Enum):
    """The lifecycle state of a monitoring session."""

    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"
