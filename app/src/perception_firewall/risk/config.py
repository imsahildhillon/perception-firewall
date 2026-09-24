"""Centralized, replaceable RiskEngine configuration.

IMPORTANT: the category weights, interaction bonuses, risk-level
thresholds, score-normalization cap, and de-escalation streak length
below are engineering heuristics for this prototype. They have NOT been
empirically validated against real fraud/scam data. See risk/README.md.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import FrozenSet, Mapping, Tuple

from perception_firewall.domain.evidence import EvidenceCategory
from perception_firewall.domain.risk import RiskLevel

#: Base points awarded once per distinct EvidenceCategory present in a
#: session's evidence, regardless of how many Evidence objects carry that
#: category. Prototype values, not empirically validated.
CATEGORY_WEIGHTS: Mapping[EvidenceCategory, int] = MappingProxyType(
    {
        EvidenceCategory.AUTHORITY: 1,
        EvidenceCategory.URGENCY: 2,
        EvidenceCategory.THREAT: 3,
        EvidenceCategory.PAYMENT: 3,
        EvidenceCategory.CREDENTIAL_REQUEST: 4,
        EvidenceCategory.REMOTE_ACCESS: 4,
        EvidenceCategory.SECRECY: 3,
        EvidenceCategory.IDENTITY_PRESSURE: 2,
    }
)

#: Extra points awarded once when BOTH categories of a pair are present
#: (by category, not by occurrence count — a pair present 10 times each
#: still contributes its bonus exactly once). Prototype values, not
#: empirically validated.
InteractionPair = FrozenSet[EvidenceCategory]

INTERACTION_BONUSES: Mapping[InteractionPair, int] = MappingProxyType(
    {
        frozenset({EvidenceCategory.URGENCY, EvidenceCategory.CREDENTIAL_REQUEST}): 3,
        frozenset({EvidenceCategory.THREAT, EvidenceCategory.PAYMENT}): 4,
        frozenset({EvidenceCategory.AUTHORITY, EvidenceCategory.PAYMENT}): 3,
        frozenset(
            {EvidenceCategory.REMOTE_ACCESS, EvidenceCategory.CREDENTIAL_REQUEST}
        ): 4,
        frozenset({EvidenceCategory.SECRECY, EvidenceCategory.PAYMENT}): 3,
    }
)

#: Ascending (minimum_raw_score_inclusive, RiskLevel) thresholds applied
#: to the raw integer point total (base + interaction points), NOT to the
#: normalized [0.0, 1.0] RiskAssessment.score — see
#: risk/README.md "Thresholds" and "Score transparency". A score is
#: assigned the level of the highest threshold it meets or exceeds.
#: Matches the example mapping given in the STEP 5 task spec exactly:
#: 0 -> SAFE, 1-2 -> LOW, 3-5 -> MEDIUM, 6-8 -> HIGH, 9+ -> CRITICAL.
RISK_LEVEL_THRESHOLDS: Tuple[Tuple[int, RiskLevel], ...] = (
    (0, RiskLevel.SAFE),
    (1, RiskLevel.LOW),
    (3, RiskLevel.MEDIUM),
    (6, RiskLevel.HIGH),
    (9, RiskLevel.CRITICAL),
)

#: Divisor used to normalize the raw integer point total into the
#: RiskAssessment.score field's required [0.0, 1.0] range
#: (score = min(1.0, raw_total / SCORE_NORMALIZATION_CAP)). The raw,
#: unnormalized total remains fully recoverable from
#: RiskAssessment.contributions. Prototype value, not empirically
#: validated — see risk/README.md.
SCORE_NORMALIZATION_CAP: int = 12

#: Number of consecutive evaluations with a lower instantaneous risk
#: level required before the session's displayed (sticky) risk level is
#: allowed to step down. Escalation is always immediate; de-escalation is
#: deliberately slower. Prototype value, not empirically validated — see
#: risk/README.md "State/hysteresis behavior".
DE_ESCALATION_STREAK_REQUIRED: int = 2
