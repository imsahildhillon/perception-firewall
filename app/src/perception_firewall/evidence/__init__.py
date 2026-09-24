"""Evidence fusion layer.

Public entry point: ``EvidenceFusion``. See README.md in this directory
for the provenance model this layer enforces (RULE vs AI vs fused
evidence) and what fusion deliberately does NOT do.
"""

from perception_firewall.evidence.config import AI_EXPLANATION_TEMPLATES, FIELD_CATEGORY_MAP
from perception_firewall.evidence.fusion import EvidenceFusion

__all__ = [
    "AI_EXPLANATION_TEMPLATES",
    "EvidenceFusion",
    "FIELD_CATEGORY_MAP",
]
