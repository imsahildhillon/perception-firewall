"""Deterministic, non-ML development implementations of the interface layer.

Everything in this package is a TEST DOUBLE for use during Mac-based
development, never a real model or a claim of Snapdragon NPU execution.
"""

from perception_firewall.interfaces.mocks.mock_classifier import MockTextClassifier
from perception_firewall.interfaces.mocks.mock_speech_to_text import (
    DEFAULT_FIXTURES,
    MockSpeechToTextEngine,
)

__all__ = [
    "DEFAULT_FIXTURES",
    "MockSpeechToTextEngine",
    "MockTextClassifier",
]
