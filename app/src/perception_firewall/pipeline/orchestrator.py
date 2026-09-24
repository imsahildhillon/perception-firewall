"""ApplicationPipeline — connects the existing components end-to-end.

    SpeechToTextEngine
            |
            v
    TranscriptBuffer (owned by Session)
            |
            v
    EvidenceProvider (e.g. RuleBasedEvidenceProvider)
            +
    TextClassifier
            |
            v
    EvidenceFusion
            |
            v
    RiskEngine
            |
            v
    RiskAssessment

The orchestrator depends only on interfaces (``SpeechToTextEngine``,
``TextClassifier``, ``EvidenceProvider``, ``RiskEngine``) plus the two
concrete, model-independent services from earlier steps (``EvidenceFusion``,
which has no interface of its own — see evidence/fusion.py). It never
imports or hard-codes a concrete Qualcomm/Whisper/Qwen implementation; see
pipeline/README.md for the full dependency-injection rationale.

Risk scoring happens nowhere in this file — every score is produced by the
injected ``RiskEngine`` and nothing here inspects or recomputes it.
"""

from __future__ import annotations

from typing import Optional, Sequence

from perception_firewall.domain.classification import ClassificationResult
from perception_firewall.domain.evidence import Evidence
from perception_firewall.domain.risk import RiskAssessment
from perception_firewall.domain.session import SessionState
from perception_firewall.domain.transcript import TranscriptSegment
from perception_firewall.evidence.fusion import EvidenceFusion
from perception_firewall.interfaces.audio import AudioChunk
from perception_firewall.interfaces.classifier import TextClassifier
from perception_firewall.interfaces.errors import (
    PerceptionFirewallError,
    SessionError,
    TranscriptBufferError,
)
from perception_firewall.interfaces.evidence_provider import EvidenceProvider
from perception_firewall.interfaces.risk_engine import RiskEngine
from perception_firewall.interfaces.speech_to_text import SpeechToTextEngine
from perception_firewall.pipeline.session import Session


class ApplicationPipeline:
    """Deterministic orchestration of the existing pipeline components.

    Every dependency is injected as an interface (or, for
    ``EvidenceFusion``, the one concrete provenance-preserving
    implementation from STEP 6 — there is no competing implementation to
    make an interface for). Swapping any of these for a real Qualcomm
    adapter later requires no change to this class.
    """

    def __init__(
        self,
        speech_to_text: SpeechToTextEngine,
        text_classifier: TextClassifier,
        evidence_provider: EvidenceProvider,
        evidence_fusion: EvidenceFusion,
        risk_engine: RiskEngine,
    ) -> None:
        self._speech_to_text = speech_to_text
        self._text_classifier = text_classifier
        self._evidence_provider = evidence_provider
        self._evidence_fusion = evidence_fusion
        self._risk_engine = risk_engine

    def process_audio_chunk(self, session: Session, audio: AudioChunk) -> RiskAssessment:
        """Transcribe ``audio`` via the injected ``SpeechToTextEngine``,
        then delegate to :meth:`process_segments` for everything else.
        """
        self._require_active_session(session)

        try:
            new_segments = self._speech_to_text.transcribe(audio)
        except PerceptionFirewallError:
            session.mark_error()
            raise

        return self.process_segments(session, new_segments)

    def process_segments(
        self,
        session: Session,
        segments: Optional[Sequence[TranscriptSegment]] = None,
    ) -> RiskAssessment:
        """Append ``segments`` to ``session``'s buffer, then run the full
        evidence/classification/fusion/risk pipeline over the session's
        entire buffered transcript so far, and return the resulting
        ``RiskAssessment``.

        ``segments`` may be ``None`` or empty — the pipeline still runs
        (re-assessing whatever is already buffered) rather than treating
        "nothing new" as an error. Risk scoring happens only inside the
        injected ``RiskEngine``; nothing here computes or adjusts a score.

        On any component failure, the session is marked ``ERROR`` and the
        original ``PerceptionFirewallError`` subclass is re-raised
        unchanged — never swallowed, and never allowed to produce a
        partial/successful ``RiskAssessment``.
        """
        self._require_active_session(session)

        if segments is not None and not isinstance(segments, (list, tuple)):
            error = TranscriptBufferError(
                "ApplicationPipeline.process_segments() requires segments "
                f"to be None, a list, or a tuple, got "
                f"{type(segments).__name__!r}"
            )
            session.mark_error()
            raise error

        try:
            for segment in segments or ():
                session.buffer.append(segment)

            transcript_text = session.buffer.text()
            current_segments = session.buffer.segments()

            rule_evidence: Sequence[Evidence] = self._evidence_provider.analyze(
                transcript_text, segments=current_segments
            )
            classification_result: ClassificationResult = self._text_classifier.classify(
                transcript_text, segments=current_segments
            )
            fused_evidence: Sequence[Evidence] = self._evidence_fusion.fuse(
                rule_evidence,
                classification_result,
                transcript_segments=current_segments,
            )
            return self._risk_engine.assess(fused_evidence, session_id=session.session_id)
        except PerceptionFirewallError:
            session.mark_error()
            raise

    def reset_session(self, session: Session) -> None:
        """Reset ``session`` (buffer + lifecycle state) AND, if the
        injected ``RiskEngine`` supports it, its hysteresis state for
        ``session.session_id``.

        ``RiskEngine.reset_session()`` is not part of the ``RiskEngine``
        interface (see ``risk/engine.py``) — it is an addition specific
        to ``DeterministicRiskEngine``'s stateful implementation. This
        method calls it only if present, so ``ApplicationPipeline``
        continues to work with any ``RiskEngine`` implementation, stateful
        or not.
        """
        session.reset()
        reset_engine_session = getattr(self._risk_engine, "reset_session", None)
        if callable(reset_engine_session):
            reset_engine_session(session.session_id)

    @staticmethod
    def _require_active_session(session: Session) -> None:
        if session is None or not isinstance(session, Session):
            raise SessionError(
                "ApplicationPipeline requires a Session instance, got "
                f"{type(session).__name__!r}"
            )
        if session.state is not SessionState.ACTIVE:
            raise SessionError(
                "Cannot process transcript input while session is "
                f"{session.state.value}; call start() or resume() first "
                f"(session_id={session.session_id!r})"
            )
