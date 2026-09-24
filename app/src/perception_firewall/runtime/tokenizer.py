"""Whisper tokenizer/config boundary.

STEP 9 confirmed, by direct inspection of the installed Qualcomm SDK
(``qai_hub_models.models.templates.hf_whisper.app.HfWhisperApp.__init__``
and its imports from ``.model``), that the reference harness resolves the
tokenizer, decoder-start-token/EOT-token IDs, and feature-extractor
config via ``transformers`` (``WhisperConfig.from_pretrained``,
``get_tokenizer``). This module defines that same boundary as an abstract
contract, so ``WhisperRuntimeAdapter`` and ``decoder_loop.py`` never
import ``transformers`` directly or assume any token ID value themselves.

The concrete, transformers-backed implementation below imports
``transformers`` lazily, inside ``__init__`` — never at module import
time — and fails clearly with ``SpeechRecognitionError`` if it is not
installed. It does NOT fall back to a fake/guessed tokenizer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.runtime.config import WhisperTokenizerConfig


class WhisperTokenizer(ABC):
    """What the decode loop and adapter need from a tokenizer — nothing
    about how any particular tokenizer library works."""

    @property
    @abstractmethod
    def start_of_transcript_token_id(self) -> int:
        """The token ID the decoder loop must feed as its very first
        input (STEP 9: ``self.config.decoder_start_token_id``)."""
        raise NotImplementedError

    @property
    @abstractmethod
    def eot_token_id(self) -> int:
        """The token ID that ends decoding (STEP 9:
        ``self.config.eos_token_id``)."""
        raise NotImplementedError

    @abstractmethod
    def decode(self, token_ids: Sequence[int]) -> str:
        """Convert a sequence of token IDs into text."""
        raise NotImplementedError


class TransformersWhisperTokenizer(WhisperTokenizer):
    """Concrete ``WhisperTokenizer`` backed by ``transformers`` — the
    same library STEP 9 found the Qualcomm reference harness itself
    depends on for this exact purpose.
    """

    def __init__(self, tokenizer_config: WhisperTokenizerConfig) -> None:
        try:
            from transformers import WhisperConfig, WhisperTokenizerFast
        except ImportError as exc:
            raise SpeechRecognitionError(
                "The Whisper Snapdragon runtime's tokenizer boundary requires "
                "the optional 'transformers' package, which is not installed "
                "in this environment. transformers is intentionally not a "
                "core application dependency — see runtime/README.md."
            ) from exc

        source = tokenizer_config.source
        try:
            self._tokenizer = WhisperTokenizerFast.from_pretrained(source)
            self._config = WhisperConfig.from_pretrained(source)
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Failed to load the Whisper tokenizer/config from {source!r}: "
                f"{exc}"
            ) from exc

    @property
    def start_of_transcript_token_id(self) -> int:
        return self._config.decoder_start_token_id

    @property
    def eot_token_id(self) -> int:
        return self._config.eos_token_id

    def decode(self, token_ids: Sequence[int]) -> str:
        try:
            return self._tokenizer.decode(
                list(token_ids), skip_special_tokens=True
            ).strip()
        except Exception as exc:
            raise SpeechRecognitionError(
                f"Whisper token decoding failed: {exc}"
            ) from exc
