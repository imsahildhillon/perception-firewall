"""Proves the abstract interfaces are real ABCs (cannot be instantiated
directly) and that the error hierarchy behaves as documented.
"""

import pytest

from perception_firewall.interfaces.audio import AudioChunk, AudioSource
from perception_firewall.interfaces.classifier import TextClassifier
from perception_firewall.interfaces.errors import (
    AudioSourceError,
    ClassificationError,
    EvidenceExtractionError,
    EvidenceFusionError,
    PerceptionFirewallError,
    RiskEngineError,
    SpeechRecognitionError,
)
from perception_firewall.interfaces.evidence_provider import EvidenceProvider
from perception_firewall.interfaces.risk_engine import RiskEngine
from perception_firewall.interfaces.speech_to_text import SpeechToTextEngine


@pytest.mark.parametrize(
    "interface",
    [AudioSource, SpeechToTextEngine, TextClassifier, EvidenceProvider, RiskEngine],
)
def test_interfaces_cannot_be_instantiated_directly(interface):
    with pytest.raises(TypeError):
        interface()


@pytest.mark.parametrize(
    "error_cls",
    [
        AudioSourceError,
        SpeechRecognitionError,
        ClassificationError,
        EvidenceExtractionError,
        EvidenceFusionError,
        RiskEngineError,
    ],
)
def test_application_errors_are_perception_firewall_errors(error_cls):
    assert issubclass(error_cls, PerceptionFirewallError)
    assert issubclass(error_cls, Exception)


def test_application_error_can_be_raised_and_caught():
    with pytest.raises(PerceptionFirewallError):
        raise SpeechRecognitionError("boom")


def test_audio_chunk_carries_generic_metadata_only():
    chunk = AudioChunk(
        data=b"\x00\x01", sample_rate_hz=16000, channels=1, fixture_id="demo_normal"
    )
    assert chunk.sample_rate_hz == 16000
    assert chunk.channels == 1
    assert chunk.fixture_id == "demo_normal"


def test_speech_to_text_engine_transcribe_stream_default_delegates_to_transcribe():
    from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource

    class _Echo(SpeechToTextEngine):
        def transcribe(self, audio):
            return (
                TranscriptSegment(
                    segment_id=f"seg-{audio.sequence_number}",
                    text="echo",
                    start_time=0.0,
                    end_time=1.0,
                    source=TranscriptSource.LIVE_AUDIO,
                ),
            )

    engine = _Echo()
    chunks = [
        AudioChunk(data=b"", sample_rate_hz=16000, channels=1, sequence_number=i)
        for i in range(3)
    ]
    segments = list(engine.transcribe_stream(chunks))
    assert [s.segment_id for s in segments] == ["seg-0", "seg-1", "seg-2"]
