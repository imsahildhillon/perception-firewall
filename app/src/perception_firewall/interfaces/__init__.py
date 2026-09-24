"""Perception Firewall model/inference interface layer.

See README.md in this directory for the architectural boundary this layer
enforces: application code depends on these interfaces, never on a
specific model or runtime library directly.
"""

from perception_firewall.interfaces.audio import AudioChunk, AudioSource
from perception_firewall.interfaces.classifier import TextClassifier
from perception_firewall.interfaces.errors import (
    AudioSourceError,
    ClassificationError,
    EvidenceExtractionError,
    PerceptionFirewallError,
    RiskEngineError,
    SpeechRecognitionError,
)
from perception_firewall.interfaces.evidence_provider import EvidenceProvider
from perception_firewall.interfaces.risk_engine import RiskEngine
from perception_firewall.interfaces.speech_to_text import SpeechToTextEngine

__all__ = [
    "AudioChunk",
    "AudioSource",
    "AudioSourceError",
    "ClassificationError",
    "EvidenceExtractionError",
    "EvidenceProvider",
    "PerceptionFirewallError",
    "RiskEngine",
    "RiskEngineError",
    "SpeechRecognitionError",
    "SpeechToTextEngine",
    "TextClassifier",
]
