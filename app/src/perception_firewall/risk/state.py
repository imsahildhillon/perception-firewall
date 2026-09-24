"""Per-session risk-level hysteresis.

Prevents a single benign evaluation from instantly clearing an elevated
risk level (HIGH -> SAFE -> HIGH -> SAFE...) just because one transcript
segment happened not to contain any indicator. Escalation is immediate;
de-escalation requires several consecutive lower-scoring evaluations, or
an explicit session reset.

This is a small, deterministic state machine — not a statistical model —
and reuses the existing domain ``RiskLevel`` enum as its state values
rather than introducing a separate NORMAL/SUSPICIOUS/HIGH_RISK/CRITICAL
enum, per the STEP 5 instruction to avoid unnecessary duplicate enums.

Not part of the ``RiskEngine`` interface — an internal implementation
detail of ``DeterministicRiskEngine``.
"""

from __future__ import annotations

from dataclasses import dataclass

from perception_firewall.domain.risk import RiskLevel
from perception_firewall.risk.config import DE_ESCALATION_STREAK_REQUIRED

#: Canonical ascending order of risk levels, used for escalation/
#: de-escalation comparisons. Explicit rather than relying on Enum
#: declaration order.
RISK_LEVEL_ORDER: tuple[RiskLevel, ...] = (
    RiskLevel.SAFE,
    RiskLevel.LOW,
    RiskLevel.MEDIUM,
    RiskLevel.HIGH,
    RiskLevel.CRITICAL,
)


def _ordinal(level: RiskLevel) -> int:
    return RISK_LEVEL_ORDER.index(level)


@dataclass
class _SessionState:
    displayed_level: RiskLevel = RiskLevel.SAFE
    consecutive_lower_evaluations: int = 0


class RiskStateTracker:
    """Tracks one hysteresis state per session_id.

    - A new session_id starts at SAFE with no history — sessions never
      leak state into each other.
    - Escalation (instantaneous level > displayed level) applies
      immediately.
    - De-escalation (instantaneous level < displayed level) only applies
      once ``DE_ESCALATION_STREAK_REQUIRED`` consecutive evaluations in a
      row have been lower than the displayed level; the displayed level
      then steps directly to the current instantaneous level (not one
      step at a time) and the streak resets.
    - An evaluation equal to the displayed level resets the streak
      without changing the displayed level.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, _SessionState] = {}

    def update(self, session_id: str, instantaneous_level: RiskLevel) -> RiskLevel:
        state = self._sessions.setdefault(session_id, _SessionState())
        instantaneous_ord = _ordinal(instantaneous_level)
        displayed_ord = _ordinal(state.displayed_level)

        if instantaneous_ord > displayed_ord:
            state.displayed_level = instantaneous_level
            state.consecutive_lower_evaluations = 0
        elif instantaneous_ord < displayed_ord:
            state.consecutive_lower_evaluations += 1
            if state.consecutive_lower_evaluations >= DE_ESCALATION_STREAK_REQUIRED:
                state.displayed_level = instantaneous_level
                state.consecutive_lower_evaluations = 0
        else:
            state.consecutive_lower_evaluations = 0

        return state.displayed_level

    def reset(self, session_id: str) -> None:
        """Explicitly clear a session's hysteresis state.

        The next ``update()`` call for this ``session_id`` behaves as if
        it were a brand-new session.
        """
        self._sessions.pop(session_id, None)
