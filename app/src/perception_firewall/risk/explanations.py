"""Human-readable, advisory-only explanation text for RiskAssessment.

Never asserts a verdict ("this is a scam", "this caller is a scammer").
At most offers advisory guidance to independently verify the other party
through an official channel — the decision remains the user's.
"""

from __future__ import annotations

from typing import Iterable

from perception_firewall.domain.evidence import EvidenceCategory
from perception_firewall.domain.risk import RiskLevel

#: Human-readable label for each category, used to build explanation text.
CATEGORY_LABELS: dict[EvidenceCategory, str] = {
    EvidenceCategory.AUTHORITY: "a claim of institutional authority",
    EvidenceCategory.URGENCY: "time pressure",
    EvidenceCategory.THREAT: "language suggesting a negative consequence",
    EvidenceCategory.PAYMENT: "a payment-related request",
    EvidenceCategory.CREDENTIAL_REQUEST: (
        "a request for a sensitive credential or verification code"
    ),
    EvidenceCategory.REMOTE_ACCESS: "a request for remote device access",
    EvidenceCategory.SECRECY: "a request to keep the conversation secret",
    EvidenceCategory.IDENTITY_PRESSURE: (
        "a request to verify identity or provide personal details"
    ),
}


def _label_list(categories: Iterable[EvidenceCategory]) -> str:
    present = set(categories)
    # Canonical EvidenceCategory declaration order, not set iteration
    # order, so the same input always produces the same text.
    labels = [CATEGORY_LABELS[c] for c in EvidenceCategory if c in present]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def build_explanation(
    risk_level: RiskLevel, present_categories: Iterable[EvidenceCategory]
) -> str:
    """Build the human-readable explanation for a RiskAssessment.

    ``risk_level`` is the session's current *displayed* (hysteresis-
    adjusted) level; ``present_categories`` are the categories observed
    in *this* call's evidence, which may be empty even while
    ``risk_level`` remains elevated because of earlier evidence in the
    session (see risk/state.py).
    """
    categories = list(present_categories)

    if not categories:
        if risk_level is RiskLevel.SAFE:
            return "No configured behavioral indicators were detected."
        return (
            "No behavioral indicators were detected in the current "
            f"evidence, but the session risk level remains "
            f"{risk_level.value.upper()} because of indicators observed "
            "earlier in this session."
        )

    label_list = _label_list(categories)

    if risk_level is RiskLevel.SAFE:
        # Not expected in normal operation (any observed category has a
        # weight of at least 1, so a non-empty category set implies a
        # non-zero instantaneous score) — handled defensively.
        return f"Indicator(s) observed ({label_list}); current risk level is SAFE."

    if risk_level is RiskLevel.LOW:
        return (
            f"A behavioral indicator was detected: {label_list}. This is "
            "currently a low level of concern under the configured rules."
        )

    if risk_level is RiskLevel.MEDIUM:
        return (
            "Several behavioral indicators were detected, including "
            f"{label_list}. Consider watching for additional signals."
        )

    if risk_level is RiskLevel.HIGH:
        return (
            "Multiple behavioral indicators were detected, including "
            f"{label_list}. Consider independently verifying the caller "
            "through an official channel before sharing sensitive "
            "information."
        )

    # CRITICAL
    return (
        "Multiple strong behavioral indicators were detected, including "
        f"{label_list}. Strongly consider ending the call and "
        "independently verifying through an official channel before "
        "taking any requested action."
    )
