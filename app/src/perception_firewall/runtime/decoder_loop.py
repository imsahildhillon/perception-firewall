"""Autoregressive Whisper decoder loop — pure orchestration logic.

Models exactly the loop STEP 9 found in the Qualcomm reference harness
(``qai_hub_models.models.templates.hf_whisper.app.HfWhisperApp.
_transcribe_single_chunk``): run the encoder once, then run the decoder
once per output token, feeding the previous step's chosen token back in,
until EOT or a configured maximum length.

This module contains no tensor operations and imports no ML/runtime
library — it only tracks plain-Python state (a step counter, chosen
token IDs, and an opaque reference to whatever the session returns as the
updated KV cache) and calls whatever ``WhisperEncoderSession`` /
``WhisperDecoderSession`` it is given. That is exactly what makes it
fully unit-testable with a deterministic fake session and zero optional
dependencies — see ``app/tests/unit/test_whisper_decoder_loop.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from perception_firewall.runtime.sessions import (
    EncoderOutput,
    WhisperDecoderSession,
    WhisperEncoderSession,
)


@dataclass(frozen=True)
class DecodeResult:
    """The full sequence of decoded token IDs (including the leading
    start-of-transcript token and, if reached, the trailing EOT token),
    plus why decoding stopped."""

    token_ids: Tuple[int, ...]
    stopped_reason: str  # "eot" or "max_length"


def run_encoder(session: WhisperEncoderSession, input_features: object) -> EncoderOutput:
    """Run the encoder exactly once for one audio chunk."""
    return session.run(input_features)


def run_decoder_loop(
    session: WhisperDecoderSession,
    encoder_output: EncoderOutput,
    start_of_transcript_token_id: int,
    eot_token_id: int,
    max_decode_length: int,
) -> DecodeResult:
    """Run the autoregressive decode loop to completion.

    ``start_of_transcript_token_id`` and ``eot_token_id`` must come from
    tokenizer/model configuration (see ``tokenizer.py``) — this function
    never assumes or hard-codes a token ID value itself.
    """
    if max_decode_length <= 0:
        raise ValueError("max_decode_length must be positive")

    token_ids: list[int] = [start_of_transcript_token_id]
    self_attention_kv: Optional[Tuple[object, ...]] = None
    current_token_id = start_of_transcript_token_id

    for step_index in range(max_decode_length):
        output = session.run(
            step_index=step_index,
            input_token_id=current_token_id,
            self_attention_kv=self_attention_kv,
            cross_attention_kv=encoder_output.cross_attention_kv,
        )
        self_attention_kv = output.self_attention_kv
        next_token_id = session.select_next_token(output.logits)
        token_ids.append(next_token_id)

        if next_token_id == eot_token_id:
            return DecodeResult(token_ids=tuple(token_ids), stopped_reason="eot")

        current_token_id = next_token_id

    return DecodeResult(token_ids=tuple(token_ids), stopped_reason="max_length")
