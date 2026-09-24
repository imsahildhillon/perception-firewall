"""Tests for tokenizer.py and feature_extraction.py.

transformers is not installed in this environment (confirmed as part of
STEP 10's dependency verification), so these tests genuinely exercise the
real "dependency unavailable" code path — not a simulation.
"""

from __future__ import annotations

import pytest

from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.runtime.config import WhisperTokenizerConfig
from perception_firewall.runtime.feature_extraction import (
    TransformersWhisperFeatureExtractor,
)
from perception_firewall.runtime.tokenizer import TransformersWhisperTokenizer


def test_transformers_not_installed_in_this_environment():
    with pytest.raises(ImportError):
        import transformers  # noqa: F401


# --- O. tokenizer dependency unavailable ------------------------------------------


def test_tokenizer_raises_speech_recognition_error_when_transformers_missing():
    config = WhisperTokenizerConfig(hf_model_id="openai/whisper-base")
    with pytest.raises(SpeechRecognitionError) as excinfo:
        TransformersWhisperTokenizer(config)
    message = str(excinfo.value).lower()
    assert "transformers" in message
    assert "not installed" in message or "optional" in message


def test_feature_extractor_raises_speech_recognition_error_when_transformers_missing():
    config = WhisperTokenizerConfig(hf_model_id="openai/whisper-base")
    with pytest.raises(SpeechRecognitionError) as excinfo:
        TransformersWhisperFeatureExtractor(config)
    message = str(excinfo.value).lower()
    assert "transformers" in message
    assert "not installed" in message or "optional" in message


def test_tokenizer_unavailability_error_does_not_expose_raw_import_error():
    config = WhisperTokenizerConfig(hf_model_id="openai/whisper-base")
    try:
        TransformersWhisperTokenizer(config)
        pytest.fail("expected SpeechRecognitionError")
    except SpeechRecognitionError as exc:
        # The application-level error is what callers see; the ImportError
        # is preserved only as __cause__, for diagnostics, not as the
        # primary exception type.
        assert isinstance(exc, SpeechRecognitionError)
        assert isinstance(exc.__cause__, ImportError)
