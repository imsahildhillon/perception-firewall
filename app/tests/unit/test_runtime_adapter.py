"""Tests for WhisperRuntimeAdapter.

Uses only injected TEST DOUBLES (fake tokenizer, feature extractor,
encoder/decoder sessions) — never the real transformers/onnxruntime-backed
implementations, and never real Snapdragon hardware. These tests prove
the adapter's orchestration/error-handling architecture and its
compatibility with the existing SpeechToTextEngine interface and
ApplicationPipeline — they do NOT prove Whisper runtime inference works
on real hardware.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional, Sequence, Tuple

import pytest

from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.evidence import EvidenceFusion
from perception_firewall.interfaces.audio import AudioChunk
from perception_firewall.interfaces.errors import SpeechRecognitionError
from perception_firewall.interfaces.mocks import MockTextClassifier
from perception_firewall.interfaces.speech_to_text import SpeechToTextEngine
from perception_firewall.pipeline import ApplicationPipeline, Session
from perception_firewall.prefilter import RuleBasedEvidenceProvider
from perception_firewall.risk.engine import DeterministicRiskEngine
from perception_firewall.runtime.adapter import WhisperRuntimeAdapter
from perception_firewall.runtime.config import (
    WhisperDecodeConfig,
    WhisperModelPaths,
    WhisperRuntimeConfig,
    WhisperTokenizerConfig,
)
from perception_firewall.runtime.platform_guard import PlatformInfo
from perception_firewall.runtime.sessions import (
    DecoderStepOutput,
    EncoderOutput,
    WhisperDecoderSession,
    WhisperEncoderSession,
)
from perception_firewall.runtime.tokenizer import WhisperTokenizer
from perception_firewall.runtime.feature_extraction import WhisperFeatureExtractor

_COMPATIBLE_HOST = PlatformInfo(os_name="nt", processor="Qualcomm Snapdragon X Elite")
_INCOMPATIBLE_HOST = PlatformInfo(os_name="posix", processor="arm")


class _FakeTokenizer(WhisperTokenizer):
    """TEST DOUBLE — not used in production."""

    def __init__(self, text: str = "hello world", start_id: int = 1, eot_id: int = 2):
        self._text = text
        self._start_id = start_id
        self._eot_id = eot_id

    @property
    def start_of_transcript_token_id(self) -> int:
        return self._start_id

    @property
    def eot_token_id(self) -> int:
        return self._eot_id

    def decode(self, token_ids: Sequence[int]) -> str:
        return self._text


class _FakeFeatureExtractor(WhisperFeatureExtractor):
    """TEST DOUBLE — not used in production."""

    def extract(self, audio_samples: object, sample_rate_hz: int) -> object:
        return "fake-input-features"


class _FakeEncoderSession(WhisperEncoderSession):
    """TEST DOUBLE — not used in production."""

    def run(self, input_features: object) -> EncoderOutput:
        return EncoderOutput(cross_attention_kv=("fake-cross-kv",))


class _FakeDecoderSession(WhisperDecoderSession):
    """TEST DOUBLE — not used in production. Emits EOT on the first call."""

    def __init__(self, eot_token_id: int = 2):
        self._eot_token_id = eot_token_id

    def run(
        self,
        step_index: int,
        input_token_id: int,
        self_attention_kv: Optional[Tuple[object, ...]],
        cross_attention_kv: Tuple[object, ...],
    ) -> DecoderStepOutput:
        return DecoderStepOutput(logits="fake-logits", self_attention_kv=())

    def select_next_token(self, logits: object) -> int:
        return self._eot_token_id


class _FailingFeatureExtractor(WhisperFeatureExtractor):
    def extract(self, audio_samples: object, sample_rate_hz: int) -> object:
        raise RuntimeError("simulated preprocessing failure")


@pytest.fixture
def model_paths(tmp_path: Path) -> WhisperModelPaths:
    encoder = tmp_path / "encoder.onnx"
    decoder = tmp_path / "decoder.onnx"
    encoder.write_bytes(b"")
    decoder.write_bytes(b"")
    return WhisperModelPaths(str(encoder), str(decoder))


def _build_adapter(model_paths, platform_info=_COMPATIBLE_HOST, **overrides):
    config = WhisperRuntimeConfig(
        model_paths=model_paths,
        tokenizer_config=WhisperTokenizerConfig(hf_model_id="openai/whisper-base"),
        decode_config=WhisperDecodeConfig(max_decode_length=5),
    )
    kwargs = dict(
        config=config,
        platform_info=platform_info,
        tokenizer=_FakeTokenizer(),
        feature_extractor=_FakeFeatureExtractor(),
        encoder_session=_FakeEncoderSession(),
        decoder_session=_FakeDecoderSession(),
    )
    kwargs.update(overrides)
    return WhisperRuntimeAdapter(**kwargs)


def _chunk(sequence_number: int = 0) -> AudioChunk:
    return AudioChunk(data=b"\x00" * 10, sample_rate_hz=16000, channels=1, sequence_number=sequence_number)


# --- B/C. missing encoder / decoder path -------------------------------------------


def test_missing_encoder_path_raises(tmp_path: Path):
    decoder = tmp_path / "decoder.onnx"
    decoder.write_bytes(b"")
    paths = WhisperModelPaths(
        str(tmp_path / "does-not-exist-encoder.onnx"), str(decoder)
    )
    with pytest.raises(SpeechRecognitionError) as excinfo:
        _build_adapter(paths)
    assert "encoder" in str(excinfo.value).lower()


def test_missing_decoder_path_raises(tmp_path: Path):
    encoder = tmp_path / "encoder.onnx"
    encoder.write_bytes(b"")
    paths = WhisperModelPaths(
        str(encoder), str(tmp_path / "does-not-exist-decoder.onnx")
    )
    with pytest.raises(SpeechRecognitionError) as excinfo:
        _build_adapter(paths)
    assert "decoder" in str(excinfo.value).lower()


# --- E/F (adapter-level): device guard enforcement ----------------------------------


def test_adapter_rejects_incompatible_host(model_paths):
    with pytest.raises(SpeechRecognitionError) as excinfo:
        _build_adapter(model_paths, platform_info=_INCOMPATIBLE_HOST)
    assert "compatible" in str(excinfo.value).lower()


def test_adapter_accepts_compatible_host(model_paths):
    adapter = _build_adapter(model_paths, platform_info=_COMPATIBLE_HOST)
    assert isinstance(adapter, WhisperRuntimeAdapter)


def test_adapter_requires_both_sessions_together(model_paths):
    config = WhisperRuntimeConfig(
        model_paths=model_paths,
        tokenizer_config=WhisperTokenizerConfig(hf_model_id="openai/whisper-base"),
    )
    with pytest.raises(SpeechRecognitionError):
        WhisperRuntimeAdapter(
            config=config,
            platform_info=_COMPATIBLE_HOST,
            tokenizer=_FakeTokenizer(),
            feature_extractor=_FakeFeatureExtractor(),
            encoder_session=_FakeEncoderSession(),
            decoder_session=None,
        )


# --- interface implementation ----------------------------------------------------------


def test_adapter_is_a_speech_to_text_engine(model_paths):
    adapter = _build_adapter(model_paths)
    assert isinstance(adapter, SpeechToTextEngine)


def test_rejects_wrong_config_type():
    with pytest.raises(SpeechRecognitionError):
        WhisperRuntimeAdapter(config="not-a-config")  # type: ignore[arg-type]


# --- R. TranscriptSegment construction --------------------------------------------------


def test_transcribe_returns_transcript_segment(model_paths):
    adapter = _build_adapter(model_paths)
    result = adapter.transcribe(_chunk())
    assert len(result) == 1
    segment = result[0]
    assert isinstance(segment, TranscriptSegment)
    assert segment.text == "hello world"
    assert segment.source is TranscriptSource.LIVE_AUDIO
    assert segment.start_time == 0.0
    assert segment.end_time == 0.0  # documented timing limitation


def test_transcribe_segment_id_reflects_sequence_number(model_paths):
    adapter = _build_adapter(model_paths)
    result = adapter.transcribe(_chunk(sequence_number=7))
    assert "7" in result[0].segment_id


def test_transcribe_empty_text_returns_no_segments(model_paths):
    adapter = _build_adapter(model_paths, tokenizer=_FakeTokenizer(text="   "))
    result = adapter.transcribe(_chunk())
    assert result == ()


# --- Q. error conversion to SpeechRecognitionError ----------------------------------------


def test_transcribe_rejects_non_audio_chunk(model_paths):
    adapter = _build_adapter(model_paths)
    with pytest.raises(SpeechRecognitionError):
        adapter.transcribe("not an audio chunk")  # type: ignore[arg-type]


def test_transcribe_wraps_feature_extraction_failure(model_paths):
    adapter = _build_adapter(model_paths, feature_extractor=_FailingFeatureExtractor())
    with pytest.raises(SpeechRecognitionError) as excinfo:
        adapter.transcribe(_chunk())
    assert isinstance(excinfo.value.__cause__, RuntimeError)


def test_transcribe_never_leaks_raw_exception_type(model_paths):
    adapter = _build_adapter(model_paths, feature_extractor=_FailingFeatureExtractor())
    try:
        adapter.transcribe(_chunk())
        pytest.fail("expected SpeechRecognitionError")
    except Exception as exc:
        assert isinstance(exc, SpeechRecognitionError)
        assert not isinstance(exc, RuntimeError)


# --- S. existing ApplicationPipeline can accept the adapter interface -----------------------


def test_application_pipeline_accepts_whisper_runtime_adapter(model_paths):
    adapter = _build_adapter(model_paths)
    pipeline = ApplicationPipeline(
        speech_to_text=adapter,
        text_classifier=MockTextClassifier(),
        evidence_provider=RuleBasedEvidenceProvider(),
        evidence_fusion=EvidenceFusion(),
        risk_engine=DeterministicRiskEngine(),
    )
    session = Session("whisper-adapter-e2e")
    session.start()
    assessment = pipeline.process_audio_chunk(session, _chunk())
    assert assessment is not None
    assert session.buffer.size() == 1
