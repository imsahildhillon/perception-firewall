"""Encoder/decoder session abstraction.

Isolates the decoder loop (``decoder_loop.py``) and
``WhisperRuntimeAdapter`` from any concrete inference backend. The real
backend (ONNX Runtime + the Qualcomm QNN Execution Provider, per STEP 9)
lives in ``onnx_sessions.py``, imported lazily and only when a
``WhisperRuntimeAdapter`` is actually constructed — never at module
import time. Nothing in this module imports ``onnxruntime``.

Tensor types here are deliberately opaque (``object``): this abstraction
does not depend on numpy, onnxruntime, or any specific tensor library —
that is exactly what lets ``decoder_loop.py`` be unit-tested with a
deterministic fake session and no optional dependency installed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class EncoderOutput:
    """Cross-attention K/V tensors produced by one encoder run.

    STEP 9 found exactly 12 such tensors in the real, tracked experiment
    metadata (``k_cache_cross_0..5`` / ``v_cache_cross_0..5``, each
    ``[8,1,64,1500]`` / ``[8,1,1500,64]``, float16) — but the count and
    shapes are whisper-base-specific, so this class only requires an
    ordered tuple of opaque tensors, not a fixed length.
    """

    cross_attention_kv: Tuple[object, ...]


@dataclass(frozen=True)
class DecoderStepOutput:
    """One decoder invocation's output: logits plus the updated
    self-attention K/V cache (STEP 9's decoder output tensor list:
    ``k_cache_self_N_out`` / ``v_cache_self_N_out`` + ``logits``)."""

    logits: object
    self_attention_kv: Tuple[object, ...]


class WhisperEncoderSession(ABC):
    """``input_features`` -> cross-attention KV outputs, one run per
    audio chunk (STEP 9: encoder input ``[1,80,3000]`` float16)."""

    @abstractmethod
    def run(self, input_features: object) -> EncoderOutput:
        raise NotImplementedError


class WhisperDecoderSession(ABC):
    """One autoregressive decode step.

    This class — not the decoder loop — owns all backend-specific tensor
    construction: zero-initializing the self-attention KV cache on the
    first step, and building the correctly-shaped, sliding-window
    ``attention_mask`` and ``position_ids`` for a given ``step_index``
    (matching the exact behavior STEP 9 found in the reference harness,
    ``HfWhisperApp._transcribe_single_chunk``). Keeping that logic here,
    rather than in the loop, is what lets ``decoder_loop.py`` remain pure
    Python with no tensor-library dependency at all.
    """

    @abstractmethod
    def run(
        self,
        step_index: int,
        input_token_id: int,
        self_attention_kv: Optional[Tuple[object, ...]],
        cross_attention_kv: Tuple[object, ...],
    ) -> DecoderStepOutput:
        """Run one autoregressive decode step.

        Parameters
        ----------
        step_index
            0-based index of this decode step. Used by the backend to
            build ``position_ids`` and the sliding ``attention_mask``.
        input_token_id
            The single token ID to feed as ``input_ids`` for this step.
        self_attention_kv
            The self-attention KV cache from the previous step's output,
            or ``None`` on the first step (``step_index == 0``), meaning
            the backend must zero-initialize it (matching STEP 9's
            evidence of ``k_cache_self``/``v_cache_self`` zero-init on
            the decoder's first call).
        cross_attention_kv
            The encoder's cross-attention KV output. Unchanged across
            every decode step for one audio chunk.
        """
        raise NotImplementedError

    @abstractmethod
    def select_next_token(self, logits: object) -> int:
        """Select the next token ID from this step's logits (e.g.
        argmax). Backend-owned because the logits tensor's concrete type
        is backend-specific."""
        raise NotImplementedError
