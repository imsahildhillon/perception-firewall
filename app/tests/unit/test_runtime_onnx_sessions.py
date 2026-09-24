"""Tests for onnx_sessions.py.

Two kinds of tests here:

1. Dependency-unavailable behavior (P): simulated via a temporary
   builtins.__import__ patch that makes `import onnxruntime` fail,
   regardless of whether onnxruntime happens to be installed in the
   environment these tests run in. This proves the *code path* — the
   clear SpeechRecognitionError translation — works, without requiring
   an environment that genuinely lacks the package.

2. Direct tests of the real tensor-shaping helper logic
   (`_zero_self_attention_kv`, `_attention_mask_for_step`) on
   `WhisperOnnxDecoderSession`, constructed via `object.__new__` (bypassing
   `__init__`, which needs a real ONNX Runtime session) with just the
   attributes those two methods need, set manually. This exercises real
   production code — not a mock of it — using the real `numpy` this
   environment happens to have, without needing onnxruntime-qnn or real
   Snapdragon hardware. These tests do NOT exercise ONNX Runtime
   inference itself and prove nothing about real QNN execution.
"""

from __future__ import annotations

import builtins

import pytest

from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.runtime.onnx_sessions import (
    WhisperOnnxDecoderSession,
    WhisperOnnxEncoderSession,
)


def _blocking_import(blocked_name: str):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == blocked_name or name.startswith(blocked_name + "."):
            raise ImportError(f"simulated: {blocked_name!r} is not installed")
        return real_import(name, *args, **kwargs)

    return fake_import


# --- P. runtime dependency unavailable -----------------------------------------------


def test_encoder_session_raises_speech_recognition_error_when_onnxruntime_missing(
    monkeypatch,
):
    monkeypatch.setattr(builtins, "__import__", _blocking_import("onnxruntime"))
    with pytest.raises(SpeechRecognitionError):
        WhisperOnnxEncoderSession("does-not-matter.onnx")


def test_decoder_session_raises_speech_recognition_error_when_onnxruntime_missing(
    monkeypatch,
):
    monkeypatch.setattr(builtins, "__import__", _blocking_import("onnxruntime"))
    with pytest.raises(SpeechRecognitionError):
        WhisperOnnxDecoderSession("does-not-matter.onnx", max_decode_length=200)


def test_dependency_unavailable_error_message_is_clear(monkeypatch):
    monkeypatch.setattr(builtins, "__import__", _blocking_import("onnxruntime"))
    with pytest.raises(SpeechRecognitionError) as excinfo:
        WhisperOnnxEncoderSession("does-not-matter.onnx")
    message = str(excinfo.value).lower()
    assert "onnxruntime" in message
    assert "not installed" in message or "optional" in message


# --- direct tensor-shaping helper tests (real numpy, no onnxruntime needed) ------------


def _make_bare_decoder_session(
    self_kv_names=("k_cache_self_0", "v_cache_self_0"),
    self_kv_shape=(2, 1, 4, 3),
    attention_mask_shape=(1, 1, 1, 5),
):
    numpy = pytest.importorskip("numpy")
    session = object.__new__(WhisperOnnxDecoderSession)
    session._np = numpy
    session._self_kv_in_names = list(self_kv_names)
    session._self_kv_shapes = {name: self_kv_shape for name in self_kv_names}
    session._attention_mask_shape = attention_mask_shape
    return session, numpy


def test_zero_self_attention_kv_shapes_and_dtype():
    session, np = _make_bare_decoder_session()
    zeros = session._zero_self_attention_kv()
    assert len(zeros) == 2
    for tensor in zeros:
        assert tensor.shape == (2, 1, 4, 3)
        assert tensor.dtype == np.float16
        assert (tensor == 0).all()


def test_attention_mask_for_first_step_unmasks_only_last_position():
    session, np = _make_bare_decoder_session()
    mask = session._attention_mask_for_step(0)
    assert mask.shape == (1, 1, 1, 5)
    # Only the single most-recent position (index -1) is unmasked at step 0.
    assert mask[..., -1] == 0.0
    assert (mask[..., :-1] < 0).all()


def test_attention_mask_visibility_grows_with_step_index():
    session, np = _make_bare_decoder_session()
    mask_step_0 = session._attention_mask_for_step(0)
    mask_step_2 = session._attention_mask_for_step(2)
    visible_0 = int((mask_step_0 == 0.0).sum())
    visible_2 = int((mask_step_2 == 0.0).sum())
    assert visible_2 > visible_0
    assert visible_0 == 1
    assert visible_2 == 3


def test_attention_mask_visibility_caps_at_mask_width():
    session, np = _make_bare_decoder_session(attention_mask_shape=(1, 1, 1, 5))
    mask = session._attention_mask_for_step(100)  # far beyond width 5
    assert (mask == 0.0).all()  # fully visible, never exceeds tensor bounds
