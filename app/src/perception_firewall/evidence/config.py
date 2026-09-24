"""Centralized configuration for AI-interpretation -> Evidence fusion.

Maps specific ``ClassificationResult`` free-text fields to the
``EvidenceCategory`` they represent, and provides a stable, per-category
explanation template — mirroring the same centralized-configuration
pattern used by ``perception_firewall.prefilter.patterns`` and
``perception_firewall.risk.config``, for the same reason: no string
literals scattered through matching/fusion logic, and easy to extend.

Only these seven fields are mapped, exactly as specified for this step:
``authority_claim``, ``urgency_description``, ``payment_request``,
``credential_request``, ``remote_access_request``, ``secrecy_request``,
``identity_pressure``. ``requested_action``, ``overall_assessment``, and
``uncertainty`` are deliberately NOT mapped to any category — see
evidence/README.md "Fields intentionally not mapped".
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from perception_firewall.domain.evidence import EvidenceCategory

#: ClassificationResult attribute name -> the EvidenceCategory it maps to.
FIELD_CATEGORY_MAP: Mapping[str, EvidenceCategory] = MappingProxyType(
    {
        "authority_claim": EvidenceCategory.AUTHORITY,
        "urgency_description": EvidenceCategory.URGENCY,
        "payment_request": EvidenceCategory.PAYMENT,
        "credential_request": EvidenceCategory.CREDENTIAL_REQUEST,
        "remote_access_request": EvidenceCategory.REMOTE_ACCESS,
        "secrecy_request": EvidenceCategory.SECRECY,
        "identity_pressure": EvidenceCategory.IDENTITY_PRESSURE,
    }
)

#: Stable, category-level explanation for why a category was flagged from
#: AI interpretation. Deliberately generic/category-level (not built from
#: the classifier's own free text) so it stays stable regardless of
#: phrasing; the classifier's actual free-text finding is carried in
#: Evidence.evidence_text instead (clearly prefixed as an AI
#: interpretation, never as a transcript quote).
AI_EXPLANATION_TEMPLATES: Mapping[EvidenceCategory, str] = MappingProxyType(
    {
        EvidenceCategory.AUTHORITY: (
            "Structured classifier interpretation indicated a claim of "
            "institutional authority."
        ),
        EvidenceCategory.URGENCY: (
            "Structured classifier interpretation indicated urgency or "
            "time pressure."
        ),
        EvidenceCategory.PAYMENT: (
            "Structured classifier interpretation indicated a "
            "payment-related request."
        ),
        EvidenceCategory.CREDENTIAL_REQUEST: (
            "Structured classifier interpretation indicated a request for "
            "a sensitive credential or verification code."
        ),
        EvidenceCategory.REMOTE_ACCESS: (
            "Structured classifier interpretation indicated a request for "
            "remote device access."
        ),
        EvidenceCategory.SECRECY: (
            "Structured classifier interpretation indicated a request to "
            "keep the conversation secret."
        ),
        EvidenceCategory.IDENTITY_PRESSURE: (
            "Structured classifier interpretation indicated a request to "
            "verify identity or provide personal details."
        ),
    }
)
