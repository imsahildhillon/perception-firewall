"""Tests for the pure autoregressive decoder loop (decoder_loop.py).

Uses deterministic fake WhisperEncoderSession/WhisperDecoderSession TEST
DOUBLES only — never the real ONNX Runtime + QNN implementation
(onnx_sessions.py). These fakes are not used by WhisperRuntimeAdapter in
production; they exist solely to prove decoder_loop.py's orchestration
logic is correct, independent of any concrete inference backend.
"""

from __future__ import annotations

from typing import Optional, Tuple

import pytest

from perception_firewall.runtime.decoder_loop import run_decoder_loop, run_encoder
from perception_firewall.runtime.sessions import (
    DecoderStepOutput,
    EncoderOutput,
    WhisperDecoderSession,
    WhisperEncoderSession,
)

START_TOKEN = 50258  # arbitrary, test-only value — never asserted as a real Whisper constant
EOT_TOKEN = 50257  # arbitrary, test-only value


class _FakeEncoderSession(WhisperEncoderSession):
    """TEST DOUBLE. Records calls, returns a fixed cross-attention KV."""

    def __init__(self, cross_attention_kv: Tuple[object, ...] = ("cross-kv",)):
        self.calls: list[object] = []
        self._cross_attention_kv = cross_attention_kv

    def run(self, input_features: object) -> EncoderOutput:
        self.calls.append(input_features)
        return EncoderOutput(cross_attention_kv=self._cross_attention_kv)


class _ScriptedDecoderSession(WhisperDecoderSession):
    """TEST DOUBLE. Emits a scripted sequence of next-token IDs, one per
    call, and records every call's arguments for assertions."""

    def __init__(self, scripted_next_tokens: Tuple[int, ...]):
        self._scripted_next_tokens = list(scripted_next_tokens)
        self.calls: list[dict] = []
        self._call_index = 0

    def run(
        self,
        step_index: int,
        input_token_id: int,
        self_attention_kv: Optional[Tuple[object, ...]],
        cross_attention_kv: Tuple[object, ...],
    ) -> DecoderStepOutput:
        self.calls.append(
            {
                "step_index": step_index,
                "input_token_id": input_token_id,
                "self_attention_kv": self_attention_kv,
                "cross_attention_kv": cross_attention_kv,
            }
        )
        updated_kv = (f"kv-after-step-{step_index}",)
        # "logits" here is just this call's index, used by
        # select_next_token below to look up the scripted next token.
        return DecoderStepOutput(logits=self._call_index, self_attention_kv=updated_kv)

    def select_next_token(self, logits: object) -> int:
        token = self._scripted_next_tokens[logits]  # logits == call index
        self._call_index += 1
        return token


# --- run_encoder ------------------------------------------------------------------


def test_run_encoder_calls_session_once():
    session = _FakeEncoderSession()
    output = run_encoder(session, "fake-input-features")
    assert len(session.calls) == 1
    assert session.calls[0] == "fake-input-features"
    assert output.cross_attention_kv == ("cross-kv",)


# --- G. decoder loop initialization ------------------------------------------------


def test_first_step_has_no_self_attention_kv():
    decoder = _ScriptedDecoderSession((EOT_TOKEN,))
    run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    assert decoder.calls[0]["self_attention_kv"] is None


def test_first_step_input_token_is_start_of_transcript():
    decoder = _ScriptedDecoderSession((EOT_TOKEN,))
    run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    assert decoder.calls[0]["input_token_id"] == START_TOKEN


def test_cross_attention_kv_passed_unchanged_every_step():
    decoder = _ScriptedDecoderSession((111, 222, EOT_TOKEN))
    encoder_output = EncoderOutput(cross_attention_kv=("stable-cross-kv",))
    run_decoder_loop(
        decoder,
        encoder_output,
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    assert all(c["cross_attention_kv"] == ("stable-cross-kv",) for c in decoder.calls)


# --- H. decoder loop token progression ----------------------------------------------


def test_next_token_fed_back_as_next_input():
    decoder = _ScriptedDecoderSession((111, 222, EOT_TOKEN))
    run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    input_tokens = [c["input_token_id"] for c in decoder.calls]
    assert input_tokens == [START_TOKEN, 111, 222]


# --- I. EOT termination ----------------------------------------------------------------


def test_stops_immediately_on_eot():
    decoder = _ScriptedDecoderSession((EOT_TOKEN,))
    result = run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=100,
    )
    assert result.stopped_reason == "eot"
    assert result.token_ids == (START_TOKEN, EOT_TOKEN)
    assert len(decoder.calls) == 1


def test_stops_on_eot_after_several_tokens():
    decoder = _ScriptedDecoderSession((1, 2, 3, EOT_TOKEN, 999))
    result = run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=100,
    )
    assert result.stopped_reason == "eot"
    assert result.token_ids == (START_TOKEN, 1, 2, 3, EOT_TOKEN)
    assert len(decoder.calls) == 4  # never calls for the 999 that follows EOT


# --- J. maximum-length termination ------------------------------------------------------


def test_stops_at_max_decode_length_without_eot():
    decoder = _ScriptedDecoderSession((1, 2, 3, 4, 5))
    result = run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=3,
    )
    assert result.stopped_reason == "max_length"
    assert result.token_ids == (START_TOKEN, 1, 2, 3)
    assert len(decoder.calls) == 3


def test_max_decode_length_of_one():
    decoder = _ScriptedDecoderSession((1, 2, 3))
    result = run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=1,
    )
    assert result.stopped_reason == "max_length"
    assert result.token_ids == (START_TOKEN, 1)


def test_non_positive_max_decode_length_raises():
    decoder = _ScriptedDecoderSession((1,))
    with pytest.raises(ValueError):
        run_decoder_loop(
            decoder,
            EncoderOutput(cross_attention_kv=("x",)),
            start_of_transcript_token_id=START_TOKEN,
            eot_token_id=EOT_TOKEN,
            max_decode_length=0,
        )


# --- K. KV cache propagation --------------------------------------------------------------


def test_self_attention_kv_propagates_from_previous_step_output():
    decoder = _ScriptedDecoderSession((1, 2, EOT_TOKEN))
    run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    # step 0 gets None; step 1 gets step 0's output; step 2 gets step 1's output
    assert decoder.calls[0]["self_attention_kv"] is None
    assert decoder.calls[1]["self_attention_kv"] == ("kv-after-step-0",)
    assert decoder.calls[2]["self_attention_kv"] == ("kv-after-step-1",)


# --- L. position ID progression (modeled via step_index) --------------------------------


def test_step_index_increments_by_one_each_call():
    decoder = _ScriptedDecoderSession((1, 2, 3, EOT_TOKEN))
    run_decoder_loop(
        decoder,
        EncoderOutput(cross_attention_kv=("x",)),
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    step_indices = [c["step_index"] for c in decoder.calls]
    assert step_indices == [0, 1, 2, 3]


# --- M. attention-mask progression -------------------------------------------------------
# Attention-mask construction is owned entirely by the concrete session
# (see sessions.py / onnx_sessions.py docstrings) — the pure loop only
# supplies step_index, from which a real backend derives the sliding
# attention mask. Progression is therefore proven at the loop level via
# monotonically increasing step_index (test_step_index_increments_by_one_
# each_call above); the real backend's mask-construction math itself is
# covered separately in test_runtime_onnx_sessions.py.


# --- N. deterministic output --------------------------------------------------------------


def test_identical_scripts_produce_identical_results():
    encoder_output = EncoderOutput(cross_attention_kv=("x",))
    first = run_decoder_loop(
        _ScriptedDecoderSession((1, 2, EOT_TOKEN)),
        encoder_output,
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    second = run_decoder_loop(
        _ScriptedDecoderSession((1, 2, EOT_TOKEN)),
        encoder_output,
        start_of_transcript_token_id=START_TOKEN,
        eot_token_id=EOT_TOKEN,
        max_decode_length=10,
    )
    assert first == second
