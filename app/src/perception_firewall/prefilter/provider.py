"""RuleBasedEvidenceProvider — the deterministic lexical/rule prefilter.

CRITICAL PRINCIPLE: this component identifies behavioral INDICATORS. It
never concludes that a conversation is fraudulent, and it never outputs a
verdict such as "this caller is a scammer." Every ``Evidence`` object it
produces pairs the original transcript text with a plain description of
which category of indicator was observed — see
``perception_firewall.prefilter.patterns.EXPLANATION_TEMPLATES``.

See app/src/perception_firewall/prefilter/README.md for the full design
rationale, pattern set, and documented limitations.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional, Sequence

from perception_firewall.domain.evidence import Evidence, EvidenceSource
from perception_firewall.domain.transcript import TranscriptSegment
from perception_firewall.interfaces.errors import EvidenceExtractionError
from perception_firewall.interfaces.evidence_provider import EvidenceProvider
from perception_firewall.prefilter.matcher import (
    CompiledPattern,
    compile_patterns,
    find_matches,
)
from perception_firewall.prefilter.patterns import EXPLANATION_TEMPLATES, PATTERNS

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str) -> str:
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    return slug or "pattern"


class RuleBasedEvidenceProvider(EvidenceProvider):
    """Deterministic, stateless ``EvidenceProvider`` backed by ``patterns.py``.

    This implementation needs per-segment structure (a stable
    ``segment_id`` and each segment's own original text) to attribute
    evidence correctly, so it does its matching against ``segments``, not
    the plain ``transcript_text`` string. ``transcript_text`` is still
    validated (it is part of the ``EvidenceProvider`` contract) but is not
    itself scanned for patterns by this implementation.

    Provenance is always ``EvidenceSource.RULE`` — this class never claims
    to be an AI classifier.
    """

    def __init__(self) -> None:
        # Compiled once at construction; matching never mutates state, so
        # a single instance is safe to reuse or share across calls.
        self._compiled_patterns: tuple[CompiledPattern, ...] = compile_patterns(
            PATTERNS
        )

    def analyze(
        self,
        transcript_text: str,
        segments: Optional[Sequence[TranscriptSegment]] = None,
    ) -> Sequence[Evidence]:
        if transcript_text is None or not isinstance(transcript_text, str):
            raise EvidenceExtractionError(
                "RuleBasedEvidenceProvider.analyze() requires transcript_text "
                "to be a string"
            )

        if segments is None:
            # No structured segments to attribute evidence to. This is a
            # legitimate, clean "nothing to analyze yet" state, not an
            # error — e.g. at the very start of a session.
            return ()

        if not isinstance(segments, (list, tuple)):
            raise EvidenceExtractionError(
                "RuleBasedEvidenceProvider.analyze() requires segments to be "
                f"a list or tuple of TranscriptSegment, got "
                f"{type(segments).__name__!r}"
            )

        evidence: list[Evidence] = []
        for segment in segments:
            if not isinstance(segment, TranscriptSegment):
                raise EvidenceExtractionError(
                    "RuleBasedEvidenceProvider.analyze() requires every "
                    "element of segments to be a TranscriptSegment, got "
                    f"{type(segment).__name__!r}"
                )
            evidence.extend(self._analyze_segment(segment))

        return tuple(evidence)

    def _analyze_segment(self, segment: TranscriptSegment) -> list[Evidence]:
        seen: set[tuple[str, str]] = set()
        results: list[Evidence] = []

        for match in find_matches(segment.text, self._compiled_patterns):
            # Defensive dedup: find_matches() already yields at most one
            # PatternMatch per configured phrase, so this should never
            # actually trigger — kept as an explicit, documented guard
            # rather than relying solely on that implementation detail.
            key = (match.category.value, match.pattern)
            if key in seen:
                continue
            seen.add(key)

            explanation_template = EXPLANATION_TEMPLATES[match.category]
            results.append(
                Evidence(
                    evidence_id=(
                        f"rule-{segment.segment_id}-{match.category.value}-"
                        f"{_slugify(match.pattern)}"
                    ),
                    category=match.category,
                    source=EvidenceSource.RULE,
                    evidence_text=segment.text,
                    explanation=explanation_template.format(pattern=match.pattern),
                    # A rule match means "the transcript contains this
                    # indicator," not a calibrated probability of
                    # malicious intent. There is no defensible way to turn
                    # a boolean keyword match into a confidence score, so
                    # confidence is deliberately left unset.
                    confidence=None,
                    timestamp=datetime.now(timezone.utc),
                    segment_id=segment.segment_id,
                )
            )

        return results
