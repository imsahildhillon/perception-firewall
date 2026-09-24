"""Speech-to-text interface.

Defines what the application needs from a speech-to-text engine, not how
any particular engine works. Nothing here mentions Whisper, ONNX, QNN, or
any other runtime/model-specific concept — those belong only in a concrete
adapter (e.g. a future Qualcomm Whisper adapter), never in this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Sequence

from perception_firewall.domain.transcript import TranscriptSegment
from perception_firewall.interfaces.audio import AudioChunk


class SpeechToTextEngine(ABC):
    """Transcribes audio into transcript segments.

    Implementations must raise ``SpeechRecognitionError`` (see
    ``perception_firewall.interfaces.errors``) on failure — never a raw
    ONNX Runtime, QNN, or other runtime-specific exception.
    """

    @abstractmethod
    def transcribe(self, audio: AudioChunk) -> Sequence[TranscriptSegment]:
        """Transcribe one complete unit of audio into transcript segments."""
        raise NotImplementedError

    def transcribe_stream(
        self, chunks: Iterable[AudioChunk]
    ) -> Iterator[TranscriptSegment]:
        """Optionally transcribe a stream of audio chunks incrementally.

        The default implementation simply calls :meth:`transcribe` on each
        chunk in turn. Implementations that support true streaming
        recognition (e.g. maintaining state across chunks) may override
        this method.
        """
        for chunk in chunks:
            yield from self.transcribe(chunk)
