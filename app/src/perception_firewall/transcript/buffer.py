"""TranscriptBuffer — ordered, session-scoped transcript state.

Manages ``TranscriptSegment`` objects for an active session. This class
does exactly one thing: it holds transcript state in chronological order.

It is NOT responsible for, and must never be extended to perform:
speech recognition, evidence extraction, classification, risk scoring,
UI, or model inference of any kind. See transcript/README.md.
"""

from __future__ import annotations

from typing import List, Sequence

from perception_firewall.domain.transcript import TranscriptSegment
from perception_firewall.interfaces.errors import TranscriptBufferError

#: Deterministic separator used to join segment texts into one transcript
#: string. A single space, matching how TranscriptSegment.text itself is
#: already whitespace-normalized by the domain layer.
DEFAULT_SEPARATOR = " "


class TranscriptBuffer:
    """Ordered store of ``TranscriptSegment`` objects for one session.

    Segments must be appended in non-decreasing ``start_time`` order.
    Out-of-order segments are rejected (raising ``TranscriptBufferError``)
    rather than silently reordered — this is the simplest policy that
    keeps chronological ordering an invariant the buffer can guarantee,
    and surfaces an upstream bug (e.g. a misbehaving speech-to-text
    engine) instead of hiding it.
    """

    def __init__(self) -> None:
        self._segments: List[TranscriptSegment] = []

    def append(self, segment: TranscriptSegment) -> None:
        """Append one segment, preserving the original object unchanged.

        Raises ``TranscriptBufferError`` if ``segment`` is not a
        ``TranscriptSegment``, or if its ``start_time`` precedes the most
        recently buffered segment's ``start_time``.
        """
        if not isinstance(segment, TranscriptSegment):
            raise TranscriptBufferError(
                "TranscriptBuffer.append() requires a TranscriptSegment, "
                f"got {type(segment).__name__!r}"
            )

        if self._segments and segment.start_time < self._segments[-1].start_time:
            raise TranscriptBufferError(
                "TranscriptBuffer.append() received an out-of-order "
                f"segment: start_time={segment.start_time} precedes the "
                "last buffered segment's start_time="
                f"{self._segments[-1].start_time}"
            )

        # Segment objects are frozen dataclasses — appending the same
        # object reference is safe; nothing here copies or mutates it.
        self._segments.append(segment)

    def segments(self) -> Sequence[TranscriptSegment]:
        """Return the currently buffered segments, in chronological order.

        Returns a tuple (immutable snapshot), never the internal list, so
        callers cannot mutate buffer state through the returned value.
        """
        return tuple(self._segments)

    def text(self, separator: str = DEFAULT_SEPARATOR) -> str:
        """Return the transcript text in chronological order.

        Segment texts are joined verbatim with ``separator`` — nothing is
        rewritten, paraphrased, or reordered.
        """
        return separator.join(segment.text for segment in self._segments)

    def clear(self) -> None:
        """Remove all buffered segments."""
        self._segments.clear()

    def size(self) -> int:
        """Return the number of currently buffered segments."""
        return len(self._segments)
