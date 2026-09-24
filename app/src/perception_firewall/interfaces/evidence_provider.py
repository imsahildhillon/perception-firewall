"""Evidence provider interface.

Represents any component that can analyze transcript content and produce
``Evidence``. This will later be implemented by (at least) a deterministic
lexical/rule prefilter, an AI classifier adapter, and potentially a future
OCR/screen-state evidence source — kept model-independent so the risk
engine can consume evidence uniformly regardless of where it came from.

Naming note: this class is named ``EvidenceProvider`` (a component that
*produces* evidence) specifically to avoid colliding with
``perception_firewall.domain.evidence.EvidenceSource`` (the
``RULE``/``AI``/``SYSTEM`` provenance enum stamped onto a piece of
``Evidence``). The two are unrelated concepts that both happened to want
the name "EvidenceSource"; this module keeps it for the enum only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from perception_firewall.domain.evidence import Evidence
from perception_firewall.domain.transcript import TranscriptSegment


class EvidenceProvider(ABC):
    """Analyzes transcript content and produces evidence.

    Implementations must raise ``EvidenceExtractionError`` (see
    ``perception_firewall.interfaces.errors``) on failure.
    """

    @abstractmethod
    def analyze(
        self,
        transcript_text: str,
        segments: Optional[Sequence[TranscriptSegment]] = None,
    ) -> Sequence[Evidence]:
        """Return zero or more pieces of evidence found in the transcript."""
        raise NotImplementedError
