"""Audio -> mel-spectrogram feature extraction boundary.

STEP 9 found the encoder's expected input is ``input_features``, shape
``[1, 80, 3000]``, float16 (per the real, tracked
``experiments/whisper_base_x_elite_npu/.../metadata.json``), produced
upstream — outside the compiled graph — by ``transformers``'
``WhisperFeatureExtractor`` in the reference harness
(``HfWhisperApp.__init__``: ``self.feature_extractor =
get_feature_extractor(hf_model_id)``).

This module defines that same boundary abstractly. The concrete
implementation is backed by ``transformers`` — it does NOT reimplement
Whisper's mel-filterbank algorithm independently. STEP 9 found no
evidence justifying a different algorithm, and reimplementing one without
that evidence would risk a numerical mismatch against the compiled
encoder graph, which was explicitly forbidden ("Do NOT invent a different
Whisper preprocessing algorithm").
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.runtime.config import WhisperTokenizerConfig


class WhisperFeatureExtractor(ABC):
    """Converts raw audio samples into the encoder's expected
    ``input_features`` tensor (``[1, 80, 3000]`` per STEP 9 evidence)."""

    @abstractmethod
    def extract(self, audio_samples: object, sample_rate_hz: int) -> object:
        """Return an opaque ``input_features`` tensor ready for
        ``WhisperEncoderSession.run()``. The concrete tensor type is
        backend-specific (e.g. a numpy array for the transformers-backed
        implementation below)."""
        raise NotImplementedError


class TransformersWhisperFeatureExtractor(WhisperFeatureExtractor):
    """Concrete ``WhisperFeatureExtractor`` backed by ``transformers``'
    own ``WhisperFeatureExtractor`` — the same class STEP 9 found the
    Qualcomm reference harness itself uses. Imported lazily, inside
    ``__init__``; fails clearly if ``transformers`` is not installed.
    """

    def __init__(self, tokenizer_config: WhisperTokenizerConfig) -> None:
        try:
            from transformers import (
                WhisperFeatureExtractor as _HFWhisperFeatureExtractor,
            )
        except ImportError as exc:
            raise SpeechRecognitionError(
                "The Whisper Snapdragon runtime's feature-extraction boundary "
                "requires the optional 'transformers' package, which is not "
                "installed in this environment. transformers is intentionally "
                "not a core application dependency — see runtime/README.md."
            ) from exc

        source = tokenizer_config.source
        try:
            self._feature_extractor = _HFWhisperFeatureExtractor.from_pretrained(
                source
            )
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Failed to load the Whisper feature extractor from "
                f"{source!r}: {exc}"
            ) from exc

    def extract(self, audio_samples: object, sample_rate_hz: int) -> object:
        try:
            return self._feature_extractor(
                audio_samples, sampling_rate=sample_rate_hz, return_tensors="np"
            )["input_features"]
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Whisper feature extraction failed: {exc}"
            ) from exc
