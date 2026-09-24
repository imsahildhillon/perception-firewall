"""Risk engine interface.

This is the contract only — no scoring logic is implemented here or by any
class in this step. Fusing evidence into a ``RiskAssessment`` is deferred
to a later stage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from perception_firewall.domain.evidence import Evidence
from perception_firewall.domain.risk import RiskAssessment


class RiskEngine(ABC):
    """Fuses evidence into a single risk assessment for a session.

    Implementations must raise ``RiskEngineError`` (see
    ``perception_firewall.interfaces.errors``) on failure.
    """

    @abstractmethod
    def assess(self, evidence: Sequence[Evidence], session_id: str) -> RiskAssessment:
        """Produce a risk assessment for the given evidence."""
        raise NotImplementedError
