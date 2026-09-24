# Risk Engine

## 1. Purpose

`DeterministicRiskEngine` implements `RiskEngine`. It aggregates a
session's `Evidence` into a single, explainable `RiskAssessment`.

**The RiskEngine aggregates observed indicators; it does not establish
that a conversation is fraudulent.** It never determines "this person is
a scammer" — it determines "given the indicators currently observed, the
current risk state is X," with the full basis for X preserved on the
returned `RiskAssessment` (`evidence`, `triggered_categories`,
`contributions`).

## 2. Score model

For each `assess(evidence, session_id)` call:

1. Collect the **distinct** `EvidenceCategory` values present across
   `evidence` (a set — occurrence count is discarded at this stage).
2. **Base score** = sum of `CATEGORY_WEIGHTS[category]` for each distinct
   category present (§3).
3. **Interaction score** = sum of `INTERACTION_BONUSES[pair]` for each
   configured category pair where *both* categories are present (§4).
4. **Raw score** = base score + interaction score (an unbounded-looking
   but in practice capped integer — see §5 and §11 for the actual bound).
5. Raw score is mapped to an instantaneous `RiskLevel` via
   `RISK_LEVEL_THRESHOLDS` (§5), then passed through the session's
   hysteresis state (§7) to get the *displayed* `RiskLevel`.
6. `RiskAssessment.score` (the domain-required `[0.0, 1.0]` float) is the
   raw score normalized as `min(1.0, raw_score / SCORE_NORMALIZATION_CAP)`
   (default cap: 12). **The raw integer point total is the authoritative,
   fully-explainable score** — recover it at any time by summing
   `contribution.base_points + contribution.interaction_points` across
   `RiskAssessment.contributions`. The normalized float exists only to
   satisfy the existing domain contract; treat it as a coarse, saturating
   summary, not the primary number.

## 3. Category weights

Configured in `config.py::CATEGORY_WEIGHTS`, exactly as specified for
this step:

| Category | Weight |
|---|---:|
| AUTHORITY | 1 |
| URGENCY | 2 |
| THREAT | 3 |
| PAYMENT | 3 |
| CREDENTIAL_REQUEST | 4 |
| REMOTE_ACCESS | 4 |
| SECRECY | 3 |
| IDENTITY_PRESSURE | 2 |

**These are engineering heuristics. They are NOT scientifically
validated.**

## 4. Interaction bonuses

Configured in `config.py::INTERACTION_BONUSES`, keyed by an unordered
`frozenset` of exactly two categories:

| Pair | Bonus |
|---|---:|
| URGENCY + CREDENTIAL_REQUEST | +3 |
| THREAT + PAYMENT | +4 |
| AUTHORITY + PAYMENT | +3 |
| REMOTE_ACCESS + CREDENTIAL_REQUEST | +4 |
| SECRECY + PAYMENT | +3 |

**Prototype values, not empirically optimized.** A bonus is applied at
most once per pair per `assess()` call, based on whether both categories
are *present* — never multiplied by how many times either category
occurred (see §6).

## 5. Thresholds

Configured in `config.py::RISK_LEVEL_THRESHOLDS`, applied to the **raw**
integer point total (not the normalized `[0.0, 1.0]` score):

| Raw score | Risk level |
|---|---|
| 0 | SAFE |
| 1–2 | LOW |
| 3–5 | MEDIUM |
| 6–8 | HIGH |
| 9+ | CRITICAL |

This is exactly the example mapping given for this step. Sanity-checked
against the three specified example scenarios: BANK_OTP (AUTHORITY +
THREAT + CREDENTIAL_REQUEST + URGENCY, one interaction bonus) totals 13
raw points → CRITICAL; AUTHORITY_PAYMENT (AUTHORITY + PAYMENT + URGENCY +
THREAT, two interaction bonuses) totals 16 → CRITICAL; the
REMOTE_ACCESS + IDENTITY_PRESSURE scenario (no configured interaction
pair between those two) totals 6 → HIGH. These land in the range a human
reviewer would expect, but **the thresholds are engineering choices, not
validated against real data.**

## 6. Repeated-evidence behavior

Score contribution is computed from the **set of distinct categories
present**, not from the list of `Evidence` objects — so:

- The same category repeated any number of times (in one segment, or
  across many segments/many separate `Evidence` objects) contributes its
  weight exactly once to the base score.
- An interaction bonus is likewise applied at most once per pair per
  `assess()` call, regardless of how many times either category occurred.
- This gives the score a hard ceiling: the sum of all 8 category weights
  (22) plus all 5 interaction bonuses (17) is 39 raw points, no matter how
  much evidence is supplied — "give me the OTP" repeated 20 times cannot
  push the score past what a single OTP request already contributes.

**Evidence preservation is separate from score contribution.**
`RiskAssessment.evidence` always contains every `Evidence` object passed
in, unmodified and undeduplicated — 20 repeated OTP observations remain
visible as 20 objects, in full, for explainability and for any future
consumer that cares about frequency (e.g. a future fusion layer) — while
`RiskAssessment.contributions` and `.score` reflect only the deduplicated,
per-category-present computation described above.

## 7. State / hysteresis behavior

Implemented in `state.py::RiskStateTracker`, keyed per `session_id`
(`DeterministicRiskEngine` holds one tracker instance internally). Reuses
the existing `RiskLevel` enum as the state value — no separate
NORMAL/SUSPICIOUS/HIGH_RISK/CRITICAL enum was introduced.

- **Escalation is immediate**: if this call's instantaneous level is
  higher than the session's current displayed level, the displayed level
  jumps to it right away.
- **De-escalation requires a streak**: if this call's instantaneous level
  is lower than the displayed level, a per-session counter increments;
  only once that counter reaches `DE_ESCALATION_STREAK_REQUIRED`
  (default: 2 consecutive lower evaluations) does the displayed level
  drop — directly to the current instantaneous level, not one step at a
  time. An evaluation *equal* to the displayed level resets the counter
  without changing the level.
- **Explicit reset**: `DeterministicRiskEngine.reset_session(session_id)`
  clears a session's state entirely (not part of the `RiskEngine`
  interface — an addition specific to this stateful implementation, since
  the shared abstract interface was not changed). The next `assess()`
  call for that `session_id` then starts fresh at SAFE.
- **Session isolation**: state is keyed strictly by `session_id`; a new
  `session_id` always starts at SAFE with no history, and different
  `session_id`s never share or leak state.

This is a small, deterministic state machine, not a statistical model, as
instructed.

## 8. Limitations

- No true NLP/semantic reasoning — the risk engine only sees the
  `EvidenceCategory` values attached to whatever `Evidence` it is handed;
  it has no way to judge whether the *underlying* evidence was itself a
  false positive.
- Thresholds and weights are a flat, hand-picked scale, not derived from
  any labeled outcome data.
- Hysteresis is a simple counter-based streak, not a time-decay or
  statistical smoothing model — "several evaluations" is a call count,
  not a wall-clock duration.
- `RiskAssessment.score`'s normalization (`raw / 12`, clamped) means
  scores at or above 12 raw points are indistinguishable at `score == 1.0`
  — use `contributions` for the real magnitude beyond that point.

## 9. Engineering-heuristic disclaimer

**The scoring and thresholds are engineering heuristics for this
prototype and have not been empirically validated.** Category weights,
interaction bonuses, risk-level thresholds, the score-normalization cap,
and the de-escalation streak length are all centralized in `config.py`
specifically so they can be revised without touching `engine.py`,
`state.py`, or `explanations.py`.

## 10. Architectural separation: no contextual suppression here

The rule prefilter's own known false positives (`"bank"` → AUTHORITY,
`"today"` → URGENCY — see `prefilter/README.md`) are **not** suppressed,
filtered, or specially handled by this engine. Given the benign sentence
"Hi, how are you? The bank branch near my house is crowded today.", the
prefilter emits AUTHORITY + URGENCY evidence, and this engine faithfully
aggregates it (raw score 3 → MEDIUM instantaneous level) exactly as it
would for any other AUTHORITY + URGENCY evidence — because as far as the
`RiskEngine` interface is concerned, it received two `Evidence` objects
with those categories and no basis to distinguish them from a real
occurrence. **Suppressing this kind of contextual false positive is
explicitly out of scope for this engine and is deferred to a future
AI/fusion layer** — a component with actual semantic understanding of the
transcript, not just category presence/absence. This separation is
deliberate: the rule prefilter and this risk engine are both
intentionally "dumb but explainable" layers; intelligence belongs above
them.

## 11. Future relationship with Qwen3 / evidence fusion

`DeterministicRiskEngine` consumes `Evidence` regardless of which
`EvidenceProvider` produced it — the rule prefilter today, and a future
Qwen3-backed classifier adapter's evidence (once one exists) tomorrow,
through the same `assess(evidence, session_id)` call. This engine has no
dependency on Qwen3, Whisper, or any Qualcomm runtime (see
`docs/ARCHITECTURE.md`) and does not need to change when a new evidence
source is added — it only needs `Evidence` objects with a category it has
a configured weight for. Combining rule-based and AI-based evidence more
intelligently than "treat every category as equally trustworthy
regardless of source" (e.g. weighting `EvidenceSource.AI` differently
from `EvidenceSource.RULE`) is a natural extension of `config.py` in a
later step, not a change to this engine's architecture.
