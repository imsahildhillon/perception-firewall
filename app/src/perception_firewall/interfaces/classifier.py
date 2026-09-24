"""Text classifier interface.

Represents what the application needs from a classifier — a
``ClassificationResult`` for a piece of transcript — not how any
particular model works. Nothing here mentions Qwen, transformers, torch,
Genie, Qualcomm, or any model file format; those belong only in a concrete
adapter (e.g. a future Qualcomm Qwen3 classifier adapter).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.transcript import TranscriptSegment


class TextClassifier(ABC):
    """Classifies transcript content for social-engineering/scam indicators.

    Implementations must raise ``ClassificationError`` (see
    ``perception_firewall.interfaces.errors``) on failure — never a raw
    model/runtime-specific exception.
    """

    @abstractmethod
    def classify(
        self,
        transcript_text: str,
        segments: Optional[Sequence[TranscriptSegment]] = None,
    ) -> ClassificationResult:
        """Classify rolling transcript text.

        ``segments`` may optionally be supplied so an implementation can
        use structured timing/source information in addition to the plain
        text.
        """
        raise NotImplementedError
