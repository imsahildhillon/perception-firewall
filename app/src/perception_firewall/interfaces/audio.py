"""Audio abstractions.

``AudioChunk`` is a runtime-independent envelope for a piece of audio.
It deliberately carries only generic fields (raw bytes plus format
metadata) — nothing here names a codec, a capture device, or a specific
speech-to-text engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass(frozen=True)
class AudioChunk:
    """A single piece of audio handed to the pipeline.

    ``fixture_id`` is optional metadata used by development/test audio
    sources (see the mock speech-to-text engine) to identify a known
    fixture scenario. Real audio sources are not required to set it.
    """

    data: bytes
    sample_rate_hz: int
    channels: int
    sequence_number: int = 0
    fixture_id: Optional[str] = None


class AudioSource(ABC):
    """Provides a sequence of audio chunks to the pipeline.

    This is an interface only. Concrete implementations — prerecorded-file
    playback, live microphone capture — are intentionally not implemented
    yet.
    """

    @abstractmethod
    def stream(self) -> Iterator[AudioChunk]:
        """Yield audio chunks until the source is exhausted or stopped.

        Implementations must raise ``AudioSourceError`` (see
        ``perception_firewall.interfaces.errors``) on failure, not a raw
        runtime-specific exception.
        """
        raise NotImplementedError
