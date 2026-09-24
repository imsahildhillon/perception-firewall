"""Application-level error model.

Every interface in this package raises one of these errors, never a raw
runtime/ML exception. Future concrete adapters (e.g. a Qualcomm Whisper or
Qwen3 adapter) are responsible for catching their own runtime-specific
exceptions and translating them into one of these types at the boundary, so
nothing above the interface layer ever needs to know what raised the
original error.
"""

from __future__ import annotations


class PerceptionFirewallError(Exception):
    """Base class for all application-level errors."""


class AudioSourceError(PerceptionFirewallError):
    """Raised when an audio source cannot provide audio (e.g. unreadable
    device or file, invalid/missing chunk data)."""


class SpeechRecognitionError(PerceptionFirewallError):
    """Raised when a speech-to-text engine cannot produce transcript
    segments for the given audio."""


class ClassificationError(PerceptionFirewallError):
    """Raised when a text classifier cannot produce a classification
    result for the given input."""


class EvidenceExtractionError(PerceptionFirewallError):
    """Raised when an evidence source cannot analyze the given transcript
    content."""


class RiskEngineError(PerceptionFirewallError):
    """Raised when a risk engine cannot produce an assessment for the
    given evidence."""
