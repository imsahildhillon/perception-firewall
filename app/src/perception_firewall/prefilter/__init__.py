"""Deterministic lexical/rule prefilter.

Public entry point: ``RuleBasedEvidenceProvider``, an ``EvidenceProvider``
implementation. See README.md in this directory for the design rationale.
"""

from perception_firewall.prefilter.patterns import EXPLANATION_TEMPLATES, PATTERNS
from perception_firewall.prefilter.provider import RuleBasedEvidenceProvider

__all__ = [
    "EXPLANATION_TEMPLATES",
    "PATTERNS",
    "RuleBasedEvidenceProvider",
]
