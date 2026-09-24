"""Centralized, replaceable pattern configuration for the rule prefilter.

IMPORTANT: this is an initial engineering rule set. It has NOT been
empirically validated as a fraud-detection model — it is a starting point
for the deterministic prefilter, expected to be revised as real-world
false positives/negatives are discovered. See prefilter/README.md for the
full discussion of limitations.

To add a new pattern: append a phrase string to the relevant category's
tuple below. No matching-logic code needs to change (see ``matcher.py``).

Documented deviations from the literal initial list, both made for the
same reason: a specified example test scenario could not otherwise be
detected under the literal list, and letting the scenario silently fail
to match was judged worse than an explicit, narrow addition. Both are
flagged here rather than applied silently:

- AUTHORITY: "authority" and "authorities" were added. None of the
  originally listed ten AUTHORITY phrases (police/officer/government/
  bank/tax department/tax authority/court/legal department/compliance/
  customs) match the word "authorities" itself, yet the specified
  AUTHORITY_PAYMENT scenario ("I am calling from the authorities...")
  requires an AUTHORITY match.
- IDENTITY_PRESSURE: "verify your account" was added. None of the
  originally listed seven IDENTITY_PRESSURE phrases match it, yet the
  specified REMOTE_ACCESS scenario ("...so I can verify your account.")
  requires an IDENTITY_PRESSURE match.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from perception_firewall.domain.evidence import EvidenceCategory

PATTERNS: Mapping[EvidenceCategory, tuple[str, ...]] = MappingProxyType(
    {
        EvidenceCategory.AUTHORITY: (
            "police",
            "officer",
            "government",
            "bank",
            "tax department",
            "tax authority",
            "authority",  # added — see module docstring
            "authorities",  # added — see module docstring
            "court",
            "legal department",
            "compliance",
            "customs",
        ),
        EvidenceCategory.URGENCY: (
            "immediately",
            "right now",
            "today",
            "urgent",
            "urgently",
            "final warning",
            "deadline",
            "within an hour",
            "act now",
        ),
        EvidenceCategory.THREAT: (
            "arrest",
            "legal action",
            "penalty",
            "account will be blocked",
            "account blocked",
            "account suspension",
            "account suspended",
            "case will be filed",
        ),
        EvidenceCategory.PAYMENT: (
            "transfer",
            "payment",
            "UPI",
            "deposit",
            "gift card",
            "cryptocurrency",
            "crypto",
            "send money",
            "transfer money",
        ),
        EvidenceCategory.CREDENTIAL_REQUEST: (
            "OTP",
            "one-time password",
            "password",
            "PIN",
            "CVV",
            "verification code",
            "security code",
            "login code",
        ),
        EvidenceCategory.REMOTE_ACCESS: (
            "AnyDesk",
            "TeamViewer",
            "remote access",
            "remote control",
            "screen sharing",
            "share your screen",
            "install this application",
        ),
        EvidenceCategory.SECRECY: (
            "don't tell anyone",
            "do not tell anyone",
            "keep this confidential",
            "keep this secret",
            "don't tell your family",
            "do not tell your family",
            "don't contact the bank",
            "do not contact the bank",
        ),
        EvidenceCategory.IDENTITY_PRESSURE: (
            "verify your identity",
            "confirm your identity",
            "send your ID",
            "provide your ID",
            "provide your details",
            "confirm your details",
            "send your documents",
            "verify your account",  # added — see module docstring
        ),
    }
)

#: Human-readable explanation templates, one per category. ``{pattern}`` is
#: filled in with the exact configured phrase that matched. These describe
#: what was *observed* (a phrase belonging to a behavioral category), never
#: a conclusion about the speaker's intent.
EXPLANATION_TEMPLATES: Mapping[EvidenceCategory, str] = MappingProxyType(
    {
        EvidenceCategory.AUTHORITY: (
            "The transcript contains a claim of institutional or official "
            "authority (matched phrase: {pattern!r})."
        ),
        EvidenceCategory.URGENCY: (
            "The transcript contains language emphasizing urgency or time "
            "pressure (matched phrase: {pattern!r})."
        ),
        EvidenceCategory.THREAT: (
            "The transcript contains language suggesting a negative "
            "consequence if the listener does not comply (matched phrase: "
            "{pattern!r})."
        ),
        EvidenceCategory.PAYMENT: (
            "The transcript contains an instruction or request related to "
            "a financial payment or transfer (matched phrase: {pattern!r})."
        ),
        EvidenceCategory.CREDENTIAL_REQUEST: (
            "The transcript contains a request for a sensitive credential "
            "or one-time verification code (matched phrase: {pattern!r})."
        ),
        EvidenceCategory.REMOTE_ACCESS: (
            "The transcript contains a request to install remote-access "
            "software or grant control of a device (matched phrase: "
            "{pattern!r})."
        ),
        EvidenceCategory.SECRECY: (
            "The transcript contains an instruction to keep the "
            "conversation secret or avoid independent verification "
            "(matched phrase: {pattern!r})."
        ),
        EvidenceCategory.IDENTITY_PRESSURE: (
            "The transcript contains a request to verify identity or "
            "provide personal documents/details (matched phrase: "
            "{pattern!r})."
        ),
    }
)
