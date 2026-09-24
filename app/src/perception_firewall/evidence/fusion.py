"""EvidenceFusion — combines RULE evidence and AI classification output
into one provenance-preserving Evidence collection for the RiskEngine.

ARCHITECTURAL PRINCIPLE (see evidence/README.md for the full discussion):

  A. Observed/extracted evidence (RULE, SYSTEM) is a concrete observation
     tied to a transcript segment or system state.
  B. AI interpretation (a ClassificationResult) describes what a model
     believes the transcript means — it is never treated as, or converted
     into, an observation.
  C. Fused evidence combines both, but every item retains its original
     provenance; AI-derived items are always clearly marked as such.

This component does NOT score risk. Its only job is to produce a clean,
explainable Evidence collection; DeterministicRiskEngine remains solely
responsible for turning evidence into a RiskAssessment.
"""

from __future__ import annotations

from typing import Optional, Sequence

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import Evidence, EvidenceSource
from perception_firewall.domain.transcript import TranscriptSegment
from perception_firewall.evidence.config import (
    AI_EXPLANATION_TEMPLATES,
    FIELD_CATEGORY_MAP,
)
from perception_firewall.interfaces.errors import EvidenceFusionError


def _is_meaningful(value: Optional[str]) -> bool:
    """True if ``value`` is a non-empty string after whitespace stripping.

    ClassificationResult's mapped fields are all ``Optional[str]`` (free
    text) — there is no boolean "false" representation to distinguish
    from a meaningful finding under the current domain contract, so this
    reduces to: not None, and not empty/whitespace-only.
    """
    return value is not None and bool(value.strip())


def _normalize(value: str) -> str:
    return " ".join(value.split())


class EvidenceFusion:
    """Deterministic, stateless combiner of RULE evidence and AI
    interpretation into one Evidence collection.

    Not part of the pluggable ``interfaces/`` ABC layer (no existing
    interface for this concept was defined in STEP 3, and none was
    requested for this step) — a concrete, standalone service class.
    """

    def fuse(
        self,
        rule_evidence: Sequence[Evidence],
        classification_result: Optional[ClassificationResult] = None,
        transcript_segments: Optional[Sequence[TranscriptSegment]] = None,
    ) -> Sequence[Evidence]:
        """Combine ``rule_evidence`` with AI evidence derived from
        ``classification_result`` (if any) into one Evidence sequence.

        ``rule_evidence`` items are passed through completely unchanged —
        same object identity, same source/category/evidence_text/
        explanation/timestamp/segment_id/confidence — and always appear
        first in the result, in their given order.

        ``classification_result`` may be ``None`` (no AI classification
        available yet); in that case no AI evidence is added.

        ``transcript_segments``, if given, is used only defensively: if
        ``classification_result.segment_id`` does not correspond to any
        segment in ``transcript_segments``, it is treated as an
        unreliable/dangling reference and dropped (the derived Evidence's
        ``segment_id`` is left ``None``) rather than propagated. It is
        never used to invent a segment_id the classifier did not itself
        supply.
        """
        if rule_evidence is None:
            raise EvidenceFusionError(
                "EvidenceFusion.fuse() requires rule_evidence to be a "
                "sequence, not None"
            )
        if not isinstance(rule_evidence, (list, tuple)):
            raise EvidenceFusionError(
                "EvidenceFusion.fuse() requires rule_evidence to be a list "
                f"or tuple, got {type(rule_evidence).__name__!r}"
            )
        for item in rule_evidence:
            if not isinstance(item, Evidence):
                raise EvidenceFusionError(
                    "EvidenceFusion.fuse() requires every element of "
                    f"rule_evidence to be an Evidence, got "
                    f"{type(item).__name__!r}"
                )

        if classification_result is not None and not isinstance(
            classification_result, ClassificationResult
        ):
            raise EvidenceFusionError(
                "EvidenceFusion.fuse() requires classification_result to be "
                "None or a ClassificationResult, got "
                f"{type(classification_result).__name__!r}"
            )

        valid_segment_ids: Optional[set[str]] = None
        if transcript_segments is not None:
            if not isinstance(transcript_segments, (list, tuple)):
                raise EvidenceFusionError(
                    "EvidenceFusion.fuse() requires transcript_segments to "
                    "be None, a list, or a tuple, got "
                    f"{type(transcript_segments).__name__!r}"
                )
            for segment in transcript_segments:
                if not isinstance(segment, TranscriptSegment):
                    raise EvidenceFusionError(
                        "EvidenceFusion.fuse() requires every element of "
                        "transcript_segments to be a TranscriptSegment, got "
                        f"{type(segment).__name__!r}"
                    )
            valid_segment_ids = {segment.segment_id for segment in transcript_segments}

        ai_evidence = self._derive_ai_evidence(classification_result, valid_segment_ids)

        # RULE evidence is never duplicated, reordered, or modified — it
        # is returned exactly as given, with AI evidence appended.
        return tuple(rule_evidence) + ai_evidence

    def _derive_ai_evidence(
        self,
        classification_result: Optional[ClassificationResult],
        valid_segment_ids: Optional[set[str]],
    ) -> tuple[Evidence, ...]:
        if classification_result is None:
            return ()

        segment_id = classification_result.segment_id
        if (
            segment_id is not None
            and valid_segment_ids is not None
            and segment_id not in valid_segment_ids
        ):
            segment_id = None  # dangling reference — never propagated

        # classification_result.timestamp is the classifier's own
        # attribution (when it ran that pass), not an invented value, so
        # it is honestly propagated if present; never fabricated if absent.
        timestamp = classification_result.timestamp

        results: list[Evidence] = []
        seen_categories: set = set()  # defensive; each field maps to a
        # distinct category 1:1, so this should never actually trigger —
        # kept as an explicit guard, mirroring RuleBasedEvidenceProvider's
        # own defensive-dedup convention.

        for field_name, category in FIELD_CATEGORY_MAP.items():
            value = getattr(classification_result, field_name)
            if not _is_meaningful(value):
                continue
            if category in seen_categories:
                continue
            seen_categories.add(category)

            normalized_value = _normalize(value)
            results.append(
                Evidence(
                    evidence_id=(
                        f"ai-{classification_result.classification_id}-"
                        f"{category.value}"
                    ),
                    category=category,
                    source=EvidenceSource.AI,
                    evidence_text=f"AI interpretation: {normalized_value}",
                    explanation=AI_EXPLANATION_TEMPLATES[category],
                    # ClassificationResult.uncertainty is self-reported
                    # uncertainty, not a calibrated confidence value, and
                    # is explicitly documented as metadata that stays on
                    # ClassificationResult rather than becoming part of
                    # any derived Evidence — see evidence/README.md. No
                    # defensible confidence value exists here, so it is
                    # left unset, exactly as RULE evidence does.
                    confidence=None,
                    timestamp=timestamp,
                    segment_id=segment_id,
                )
            )

        return tuple(results)
