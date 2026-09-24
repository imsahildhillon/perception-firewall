from datetime import datetime, timezone

import pytest

from perception_firewall.domain.evidence import Evidence, EvidenceCategory, EvidenceSource
from perception_firewall.domain.risk import RiskLevel
from perception_firewall.domain.transcript import TranscriptSegment, TranscriptSource
from perception_firewall.interfaces.errors import RiskEngineError
from perception_firewall.prefilter import RuleBasedEvidenceProvider
from perception_firewall.risk.engine import DeterministicRiskEngine, _level_for_raw_score


def _evidence(
    category: EvidenceCategory,
    evidence_id: str = "ev-1",
    segment_id: str = "seg-1",
    source: EvidenceSource = EvidenceSource.RULE,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        category=category,
        source=source,
        evidence_text="observed text",
        explanation="an interpretation",
        timestamp=datetime.now(timezone.utc),
        segment_id=segment_id,
    )


@pytest.fixture
def engine():
    return DeterministicRiskEngine()


FORBIDDEN_VERDICT_TERMS = ("scam", "scammer", "fraud", "fraudulent", "criminal")


def _assert_no_verdict_language(text: str) -> None:
    lowered = text.lower()
    for term in FORBIDDEN_VERDICT_TERMS:
        assert term not in lowered


# --- 1. no evidence -> SAFE -------------------------------------------------


def test_no_evidence_is_safe(engine):
    assessment = engine.assess([], session_id="s1")
    assert assessment.risk_level is RiskLevel.SAFE
    assert assessment.score == 0.0
    assert assessment.contributions == ()
    assert assessment.evidence == ()


# --- 2-9. each category individually ----------------------------------------


@pytest.mark.parametrize(
    "category,expected_level",
    [
        (EvidenceCategory.AUTHORITY, RiskLevel.LOW),
        (EvidenceCategory.URGENCY, RiskLevel.LOW),
        (EvidenceCategory.THREAT, RiskLevel.MEDIUM),
        (EvidenceCategory.PAYMENT, RiskLevel.MEDIUM),
        (EvidenceCategory.CREDENTIAL_REQUEST, RiskLevel.MEDIUM),
        (EvidenceCategory.REMOTE_ACCESS, RiskLevel.MEDIUM),
        (EvidenceCategory.SECRECY, RiskLevel.MEDIUM),
        (EvidenceCategory.IDENTITY_PRESSURE, RiskLevel.LOW),
    ],
)
def test_single_category(engine, category, expected_level):
    assessment = engine.assess([_evidence(category)], session_id=f"s-{category.value}")
    assert assessment.risk_level is expected_level
    assert len(assessment.contributions) == 1
    assert assessment.contributions[0].category is category
    assert assessment.contributions[0].interaction_points == 0


# --- 10-14. each interaction pair -------------------------------------------


@pytest.mark.parametrize(
    "cat_a,cat_b,expected_level",
    [
        (EvidenceCategory.AUTHORITY, EvidenceCategory.PAYMENT, RiskLevel.HIGH),
        (EvidenceCategory.THREAT, EvidenceCategory.PAYMENT, RiskLevel.CRITICAL),
        (EvidenceCategory.URGENCY, EvidenceCategory.CREDENTIAL_REQUEST, RiskLevel.CRITICAL),
        (EvidenceCategory.REMOTE_ACCESS, EvidenceCategory.CREDENTIAL_REQUEST, RiskLevel.CRITICAL),
        (EvidenceCategory.SECRECY, EvidenceCategory.PAYMENT, RiskLevel.CRITICAL),
    ],
)
def test_interaction_pair(engine, cat_a, cat_b, expected_level):
    session_id = f"s-{cat_a.value}-{cat_b.value}"
    assessment = engine.assess(
        [_evidence(cat_a, "ev-a"), _evidence(cat_b, "ev-b")], session_id=session_id
    )
    assert assessment.risk_level is expected_level
    interaction_contributions = [
        c for c in assessment.contributions if c.category is None
    ]
    assert len(interaction_contributions) == 1
    assert interaction_contributions[0].interaction_points > 0


# --- 15. multiple categories -------------------------------------------------


def test_multiple_categories(engine):
    evidence = [
        _evidence(EvidenceCategory.AUTHORITY, "ev-1"),
        _evidence(EvidenceCategory.THREAT, "ev-2"),
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-3"),
        _evidence(EvidenceCategory.URGENCY, "ev-4"),
    ]
    assessment = engine.assess(evidence, session_id="s-multi")
    assert assessment.risk_level is RiskLevel.CRITICAL
    categories = {c.category for c in assessment.contributions if c.category is not None}
    assert categories == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.THREAT,
        EvidenceCategory.CREDENTIAL_REQUEST,
        EvidenceCategory.URGENCY,
    }
    raw_total = sum(c.base_points + c.interaction_points for c in assessment.contributions)
    assert raw_total == 13  # 1+3+4+2 base + 3 (URGENCY+CREDENTIAL_REQUEST)


# --- 16. repeated same category ----------------------------------------------


def test_repeated_same_category_counts_once(engine):
    evidence = [
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, f"ev-{i}", f"seg-{i}")
        for i in range(5)
    ]
    assessment = engine.assess(evidence, session_id="s-repeat-category")
    category_contributions = [
        c for c in assessment.contributions if c.category is EvidenceCategory.CREDENTIAL_REQUEST
    ]
    assert len(category_contributions) == 1
    assert category_contributions[0].base_points == 4
    assert assessment.risk_level is RiskLevel.MEDIUM
    assert len(assessment.evidence) == 5  # all preserved


# --- 17. repeated same evidence ----------------------------------------------


def test_repeated_identical_evidence_counts_once_for_score(engine):
    single = _evidence(EvidenceCategory.URGENCY, "ev-dup", "seg-1")
    assessment = engine.assess([single, single, single], session_id="s-dup")
    urgency_contributions = [
        c for c in assessment.contributions if c.category is EvidenceCategory.URGENCY
    ]
    assert len(urgency_contributions) == 1
    assert len(assessment.evidence) == 3  # preserved as given


# --- 18. repeated evidence across different segments -------------------------


def test_repeated_evidence_across_segments_counts_once_for_score(engine):
    evidence = [
        _evidence(EvidenceCategory.SECRECY, "ev-1", "seg-1"),
        _evidence(EvidenceCategory.SECRECY, "ev-2", "seg-2"),
        _evidence(EvidenceCategory.SECRECY, "ev-3", "seg-3"),
    ]
    assessment = engine.assess(evidence, session_id="s-cross-segment")
    secrecy_contributions = [
        c for c in assessment.contributions if c.category is EvidenceCategory.SECRECY
    ]
    assert len(secrecy_contributions) == 1
    assert len(assessment.evidence) == 3
    assert {e.segment_id for e in assessment.evidence} == {"seg-1", "seg-2", "seg-3"}


# --- 19. score does not grow unbounded ---------------------------------------


def test_score_does_not_grow_unbounded_with_all_categories_repeated(engine):
    evidence = []
    for category in EvidenceCategory:
        for i in range(10):
            evidence.append(_evidence(category, f"ev-{category.value}-{i}", f"seg-{i}"))

    assessment = engine.assess(evidence, session_id="s-max")
    raw_total = sum(c.base_points + c.interaction_points for c in assessment.contributions)
    # Sum of all 8 weights (1+2+3+3+4+4+3+2=22) + all 5 interaction bonuses
    # (3+4+3+4+3=17) = 39, regardless of the 80 Evidence objects supplied.
    assert raw_total == 39
    assert assessment.risk_level is RiskLevel.CRITICAL
    assert assessment.score == 1.0  # normalized and clamped
    assert len(assessment.evidence) == 80  # fully preserved


# --- 20. interaction bonus applied once --------------------------------------


def test_interaction_bonus_applied_once_regardless_of_occurrence_count(engine):
    evidence = [
        _evidence(EvidenceCategory.AUTHORITY, f"ev-a{i}", f"seg-a{i}") for i in range(5)
    ] + [_evidence(EvidenceCategory.PAYMENT, f"ev-p{i}", f"seg-p{i}") for i in range(5)]
    assessment = engine.assess(evidence, session_id="s-bonus-once")
    interaction_contributions = [c for c in assessment.contributions if c.category is None]
    assert len(interaction_contributions) == 1
    assert interaction_contributions[0].interaction_points == 3
    raw_total = sum(c.base_points + c.interaction_points for c in assessment.contributions)
    assert raw_total == 7  # 1 + 3 + 3, not multiplied by 5x5


# --- 21. session reset --------------------------------------------------------


def test_session_reset_clears_hysteresis(engine):
    high_evidence = [
        _evidence(EvidenceCategory.REMOTE_ACCESS, "ev-1"),
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-2"),
    ]
    first = engine.assess(high_evidence, session_id="s-reset")
    assert first.risk_level is RiskLevel.CRITICAL

    engine.reset_session("s-reset")

    after_reset = engine.assess([], session_id="s-reset")
    assert after_reset.risk_level is RiskLevel.SAFE


# --- 22. session isolation -----------------------------------------------------


def test_sessions_are_isolated(engine):
    high_evidence = [
        _evidence(EvidenceCategory.REMOTE_ACCESS, "ev-1"),
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-2"),
    ]
    engine.assess(high_evidence, session_id="s-a")
    other_session_result = engine.assess([], session_id="s-b")
    assert other_session_result.risk_level is RiskLevel.SAFE


# --- 23. escalation ------------------------------------------------------------


def test_escalation_is_immediate(engine):
    first = engine.assess([], session_id="s-escalate")
    assert first.risk_level is RiskLevel.SAFE

    high_evidence = [
        _evidence(EvidenceCategory.REMOTE_ACCESS, "ev-1"),
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-2"),
    ]
    second = engine.assess(high_evidence, session_id="s-escalate")
    assert second.risk_level is RiskLevel.CRITICAL


# --- 24. de-escalation ----------------------------------------------------------


def test_deescalation_requires_a_streak(engine):
    high_evidence = [
        _evidence(EvidenceCategory.REMOTE_ACCESS, "ev-1"),
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-2"),
    ]
    first = engine.assess(high_evidence, session_id="s-deescalate")
    assert first.risk_level is RiskLevel.CRITICAL

    # One benign evaluation must NOT instantly clear the elevated level.
    second = engine.assess([], session_id="s-deescalate")
    assert second.risk_level is RiskLevel.CRITICAL

    # A second consecutive benign evaluation reaches the configured
    # streak (DE_ESCALATION_STREAK_REQUIRED == 2) and the level drops.
    third = engine.assess([], session_id="s-deescalate")
    assert third.risk_level is RiskLevel.SAFE


def test_deescalation_streak_resets_on_non_lower_evaluation(engine):
    high_evidence = [
        _evidence(EvidenceCategory.REMOTE_ACCESS, "ev-1"),
        _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-2"),
    ]
    engine.assess(high_evidence, session_id="s-streak-reset")
    engine.assess([], session_id="s-streak-reset")  # streak = 1
    # A CRITICAL-again evaluation should reset the streak, not add to it.
    engine.assess(high_evidence, session_id="s-streak-reset")
    still_critical = engine.assess([], session_id="s-streak-reset")  # streak = 1 again
    assert still_critical.risk_level is RiskLevel.CRITICAL


# --- 25. empty evidence ---------------------------------------------------------


def test_empty_evidence_list_is_safe_and_clean(engine):
    assessment = engine.assess([], session_id="s-empty")
    assert assessment.risk_level is RiskLevel.SAFE
    assert assessment.contributions == ()
    assert assessment.evidence == ()
    assert assessment.explanation == "No configured behavioral indicators were detected."


# --- 26. benign evidence ---------------------------------------------------------


def test_benign_single_authority_evidence_is_low_not_alarming(engine):
    assessment = engine.assess(
        [_evidence(EvidenceCategory.AUTHORITY)], session_id="s-benign"
    )
    assert assessment.risk_level is RiskLevel.LOW
    _assert_no_verdict_language(assessment.explanation)


# --- 27. human-readable explanation -----------------------------------------------


def test_explanation_is_human_readable_string(engine):
    assessment = engine.assess(
        [_evidence(EvidenceCategory.CREDENTIAL_REQUEST)], session_id="s-explain"
    )
    assert isinstance(assessment.explanation, str)
    assert len(assessment.explanation) > 10
    assert "credential" in assessment.explanation.lower()


# --- 28. no verdict language -------------------------------------------------------


@pytest.mark.parametrize(
    "evidence",
    [
        [],
        [_evidence(EvidenceCategory.AUTHORITY)],
        [_evidence(EvidenceCategory.THREAT), _evidence(EvidenceCategory.PAYMENT, "ev-2")],
        [
            _evidence(EvidenceCategory.REMOTE_ACCESS),
            _evidence(EvidenceCategory.CREDENTIAL_REQUEST, "ev-2"),
        ],
    ],
)
def test_no_verdict_language_across_levels(evidence):
    engine_ = DeterministicRiskEngine()
    assessment = engine_.assess(evidence, session_id="s-verdict-check")
    _assert_no_verdict_language(assessment.explanation)
    for contribution in assessment.contributions:
        _assert_no_verdict_language(contribution.reason)


# --- 29. deterministic output -------------------------------------------------------


def test_deterministic_output_for_identical_evidence():
    evidence = [
        _evidence(EvidenceCategory.AUTHORITY, "ev-1"),
        _evidence(EvidenceCategory.THREAT, "ev-2"),
        _evidence(EvidenceCategory.PAYMENT, "ev-3"),
    ]
    first = DeterministicRiskEngine().assess(evidence, session_id="s-det-1")
    second = DeterministicRiskEngine().assess(evidence, session_id="s-det-2")

    assert first.risk_level is second.risk_level
    assert first.score == second.score
    assert first.explanation == second.explanation
    assert first.triggered_categories == second.triggered_categories
    assert [
        (c.category, c.base_points, c.interaction_points, c.reason)
        for c in first.contributions
    ] == [
        (c.category, c.base_points, c.interaction_points, c.reason)
        for c in second.contributions
    ]


# --- boundary threshold tests -------------------------------------------------------


@pytest.mark.parametrize(
    "raw_score,expected_level",
    [
        (0, RiskLevel.SAFE),
        (1, RiskLevel.LOW),
        (2, RiskLevel.LOW),
        (3, RiskLevel.MEDIUM),
        (5, RiskLevel.MEDIUM),
        (6, RiskLevel.HIGH),
        (8, RiskLevel.HIGH),
        (9, RiskLevel.CRITICAL),
        (100, RiskLevel.CRITICAL),
    ],
)
def test_threshold_boundaries(raw_score, expected_level):
    assert _level_for_raw_score(raw_score) is expected_level


# --- false-positive scenario (architectural separation) -----------------------------


def test_prefilter_false_positive_is_faithfully_aggregated_not_suppressed():
    """The RiskEngine does not add contextual intelligence to suppress
    the prefilter's own documented false positives ('bank' -> AUTHORITY,
    'today' -> URGENCY). See risk/README.md section 10 and
    prefilter/README.md section 8. Contextual suppression is explicitly
    deferred to a future AI/fusion layer, not this engine.
    """
    segment = TranscriptSegment(
        segment_id="benign-1",
        text="Hi, how are you? The bank branch near my house is crowded today.",
        start_time=0.0,
        end_time=4.0,
        source=TranscriptSource.RECORDED_AUDIO,
    )
    evidence = RuleBasedEvidenceProvider().analyze("", segments=[segment])
    assert {e.category for e in evidence} == {
        EvidenceCategory.AUTHORITY,
        EvidenceCategory.URGENCY,
    }

    assessment = DeterministicRiskEngine().assess(evidence, session_id="s-false-positive")
    assert assessment.risk_level is RiskLevel.MEDIUM  # 1 (AUTHORITY) + 2 (URGENCY), no bonus
    assert len(assessment.evidence) == 2
    _assert_no_verdict_language(assessment.explanation)


# --- malformed input / error handling ------------------------------------------------


def test_none_evidence_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.assess(None, session_id="s1")


def test_non_sequence_evidence_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.assess("not a sequence", session_id="s1")


def test_evidence_containing_non_evidence_item_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.assess([_evidence(EvidenceCategory.AUTHORITY), "not evidence"], session_id="s1")


def test_none_session_id_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.assess([], session_id=None)


def test_empty_session_id_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.assess([], session_id="   ")


def test_non_string_session_id_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.assess([], session_id=12345)


def test_reset_session_with_invalid_session_id_raises(engine):
    with pytest.raises(RiskEngineError):
        engine.reset_session("")


# --- interface contract sanity -------------------------------------------------------


def test_assess_returns_risk_assessment_with_timestamp(engine):
    assessment = engine.assess([_evidence(EvidenceCategory.URGENCY)], session_id="s-contract")
    assert assessment.session_id == "s-contract"
    assert assessment.timestamp is not None
