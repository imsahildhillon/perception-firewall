"""Configuration for the Whisper Snapdragon runtime adapter.

Every path, tokenizer identifier, and decode parameter the adapter needs
comes from this module's dataclasses — nothing is hard-coded inside
``adapter.py``, ``onnx_sessions.py``, ``tokenizer.py``, or
``feature_extraction.py``. This mirrors the rest of the codebase's
centralized-configuration convention (``prefilter/patterns.py``,
``risk/config.py``, ``evidence/config.py``).

These dataclasses validate only their own *structure* (non-empty strings,
positive numbers, etc.) — they never check the filesystem or network.
Operational conditions (a path that doesn't exist, a host that isn't
Windows-on-Snapdragon) are checked later, by ``WhisperRuntimeAdapter``
itself, which raises ``SpeechRecognitionError`` for those — see
runtime/README.md for the reasoning behind that split.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class WhisperModelPaths:
    """Local filesystem paths to the two compiled Whisper artifact files.

    These are exactly the encoder/decoder ONNX-wrapped-QNN-context-binary
    pair the STEP 9 investigation found
    (``experiments/whisper_base_x_elite_npu/.../metadata.json``:
    ``encoder.onnx`` + ``encoder_qairt_context.bin``, ``decoder.onnx`` +
    ``decoder_qairt_context.bin`` — the ``.bin`` is referenced from inside
    the ``.onnx`` file, so only the ``.onnx`` path is needed here).
    """

    encoder_path: str
    decoder_path: str

    def __post_init__(self) -> None:
        if not isinstance(self.encoder_path, str) or not self.encoder_path.strip():
            raise ValueError(
                "WhisperModelPaths.encoder_path must be a non-empty string"
            )
        if not isinstance(self.decoder_path, str) or not self.decoder_path.strip():
            raise ValueError(
                "WhisperModelPaths.decoder_path must be a non-empty string"
            )


@dataclass(frozen=True)
class WhisperTokenizerConfig:
    """Identifies which tokenizer/feature-extractor/config to load.

    STEP 9 found the Qualcomm reference harness (``HfWhisperApp``)
    resolves the tokenizer, decoder start/EOT token IDs, and feature
    extractor via a Hugging Face model identifier (e.g.
    ``"openai/whisper-base"``) passed to ``transformers``. ``hf_model_id``
    mirrors that. ``local_path`` is the offline alternative: a local
    directory holding the same tokenizer/config files. Exactly one of the
    two must be set.
    """

    hf_model_id: Optional[str] = None
    local_path: Optional[str] = None

    def __post_init__(self) -> None:
        provided = [v for v in (self.hf_model_id, self.local_path) if v]
        if len(provided) != 1:
            raise ValueError(
                "WhisperTokenizerConfig requires exactly one of hf_model_id "
                "or local_path to be set"
            )

    @property
    def source(self) -> str:
        """The single resolved source string, whichever was provided."""
        assert self.hf_model_id or self.local_path
        return self.hf_model_id or self.local_path  # type: ignore[return-value]


@dataclass(frozen=True)
class WhisperDecodeConfig:
    """Autoregressive decode-loop parameters.

    ``max_decode_length`` defaults to 200, matching the attention-mask
    and self-KV-cache tensor shapes STEP 9 found in the real, tracked
    experiment metadata (``attention_mask: [1,1,1,200]``,
    ``k_cache_self_*: [8,1,64,199]`` — 199 == 200 - 1). This is not an
    independently assumed Whisper constant; it is the value implied by
    our own verified compiled-artifact evidence, kept configurable so a
    differently-exported artifact isn't silently mismatched.
    """

    max_decode_length: int = 200

    def __post_init__(self) -> None:
        if self.max_decode_length <= 0:
            raise ValueError(
                "WhisperDecodeConfig.max_decode_length must be positive"
            )


@dataclass(frozen=True)
class WhisperRuntimeConfig:
    """Full configuration for ``WhisperRuntimeAdapter``."""

    model_paths: WhisperModelPaths
    tokenizer_config: WhisperTokenizerConfig
    decode_config: WhisperDecodeConfig = field(default_factory=WhisperDecodeConfig)

    def __post_init__(self) -> None:
        if not isinstance(self.model_paths, WhisperModelPaths):
            raise ValueError(
                "WhisperRuntimeConfig.model_paths must be a WhisperModelPaths"
            )
        if not isinstance(self.tokenizer_config, WhisperTokenizerConfig):
            raise ValueError(
                "WhisperRuntimeConfig.tokenizer_config must be a "
                "WhisperTokenizerConfig"
            )
        if not isinstance(self.decode_config, WhisperDecodeConfig):
            raise ValueError(
                "WhisperRuntimeConfig.decode_config must be a WhisperDecodeConfig"
            )
