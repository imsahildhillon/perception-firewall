"""Transcript domain model.

Represents recognized speech as an application concept, independent of
whichever speech-to-text engine produced it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TranscriptSource(Enum):
    """Where a transcript segment's audio originated.

    Intentionally generic (not "whisper_base" or any other engine name) so
    the domain layer never depends on a specific speech-to-text runtime.
    """

    LIVE_AUDIO = "live_audio"
    RECORDED_AUDIO = "recorded_audio"
    MANUAL_TEXT = "manual_text"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TranscriptSegment:
    """One recognized piece of speech.

    Timestamps are session-relative offsets in seconds (not wall-clock
    times), so they remain consistent regardless of when a session started.
    """

    segment_id: str
    text: str
    start_time: float
    end_time: float
    source: TranscriptSource

    def __post_init__(self) -> None:
        normalized = " ".join(self.text.split())
        if not normalized or not any(ch.isalnum() for ch in normalized):
            raise ValueError(
                "TranscriptSegment.text must contain meaningful content "
                "after normalization"
            )
        object.__setattr__(self, "text", normalized)

        if self.start_time < 0:
            raise ValueError("TranscriptSegment.start_time must not be negative")

        if self.end_time < self.start_time:
            raise ValueError(
                "TranscriptSegment.end_time must not precede start_time"
            )

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
