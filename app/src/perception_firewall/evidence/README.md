# Evidence Fusion

## 1. Purpose

`EvidenceFusion` combines two independent evidence-producing paths —
deterministic rule evidence (`RuleBasedEvidenceProvider`) and structured
AI classification output (`ClassificationResult`, in practice from a
future Qwen3 classifier adapter) — into a single `Evidence` collection for
`DeterministicRiskEngine`, without ever letting AI output masquerade as an
observed fact.

## 2. Provenance model

There are three distinct concepts, and fusion is built specifically to
keep them from collapsing into one:

- **Observed/extracted evidence** (`EvidenceSource.RULE`,
  `EvidenceSource.SYSTEM`): a concrete observation tied to a transcript
  segment or system state. `RuleBasedEvidenceProvider` produces this
  today; a future OCR/screen-state source would also produce
  `SYSTEM`-sourced evidence this way.
- **AI interpretation** (`ClassificationResult`): what a classifier
  *believes* the transcript means. It is not an observation — it is an
  inference — and it stays that way through fusion.
- **Fused evidence**: the combined `Evidence` collection handed to the
  risk engine. Every item retains its original provenance
  (`Evidence.source`); nothing produced by fusion is ambiguous about
  where it came from.

## 3. RULE vs. AI evidence

RULE evidence passed into `fuse()` is returned **completely unchanged** —
same object identity, same `category`/`source`/`evidence_text`/
`explanation`/`timestamp`/`segment_id`/`confidence` — and always appears
first, in its given order. Fusion never edits, re-scores, or reclassifies
RULE evidence.

AI evidence is newly constructed, one item per meaningful
`ClassificationResult` field (see §4), and is unambiguously marked:

- `source = EvidenceSource.AI` — never `RULE`.
- `evidence_text` is always prefixed `"AI interpretation: ..."`, followed
  by the classifier's own free-text finding for that field (whitespace-
  normalized). This is a deliberate improvement on a purely generic
  template: it preserves the classifier's actual finding content while
  making it structurally impossible to mistake for a verbatim transcript
  quote — nothing in fusion ever copies transcript text into an
  AI-sourced `Evidence.evidence_text`.
- `explanation` is a **stable, category-level** template (see
  `evidence/config.py::AI_EXPLANATION_TEMPLATES`), not built from the
  classifier's own wording — this mirrors the same convention
  `prefilter/patterns.py::EXPLANATION_TEMPLATES` already uses for RULE
  evidence, so both provenances explain themselves consistently.
- `confidence` is always `None`. `ClassificationResult.uncertainty` is
  *self-reported uncertainty*, not a calibrated confidence value, and is
  explicitly documented (both on the domain model and here) as metadata
  that stays on `ClassificationResult` — it is never copied, inverted, or
  otherwise turned into `Evidence.confidence`. There is no field on the
  current `ClassificationResult` contract that constitutes a defensible
  confidence value, so none is used, per this step's explicit instruction.
- `timestamp` / `segment_id` are propagated **only if the classifier
  itself supplied them** on `ClassificationResult` — never invented. If
  `transcript_segments` is also given to `fuse()` and the classifier's
  `segment_id` doesn't match any real segment in it, that `segment_id` is
  treated as a dangling reference and dropped back to `None` rather than
  propagated — this is a defensive integrity check, not a fabrication.

## 4. Why AI interpretation is not equivalent to observed evidence

An AI classifier's job is to *interpret* — to say "this looks like a
payment request" — not to reproduce a transcript quote. Treating that
interpretation as if it were an observation (e.g. giving it
`source=RULE`, or writing it into `evidence_text` without the
`"AI interpretation:"` prefix) would erase the distinction between "the
transcript says X" and "a model believes the transcript means X" — exactly
the failure mode this whole layer exists to prevent. Fusion enforces the
distinction structurally: there is no code path by which an AI-derived
item can end up with `source=EvidenceSource.RULE`, and no code path by
which `evidence_text` is copied from the transcript for an AI item.

## 5. Field-to-category mapping

Exactly seven `ClassificationResult` fields are mapped, each to the
`EvidenceCategory` it represents (`evidence/config.py::FIELD_CATEGORY_MAP`):

| Field | Category |
|---|---|
| `authority_claim` | AUTHORITY |
| `urgency_description` | URGENCY |
| `payment_request` | PAYMENT |
| `credential_request` | CREDENTIAL_REQUEST |
| `remote_access_request` | REMOTE_ACCESS |
| `secrecy_request` | SECRECY |
| `identity_pressure` | IDENTITY_PRESSURE |

A field only produces `Evidence` when it is **meaningful**: not `None`,
and not empty/whitespace-only after stripping. `ClassificationResult`'s
mapped fields are all `Optional[str]` under the current domain contract —
there is no boolean "false" value to additionally guard against.

### Fields intentionally not mapped

- **`requested_action`** — a general summary field that overlaps with the
  more specific per-category fields above; mapping it too would risk
  double-counting the same finding under a vague, uncategorizable
  "requested action" label. No `EvidenceCategory` exists for it, and
  inventing one would violate the "don't turn every free-form field into
  a category" principle.
- **`overall_assessment`** — remains an assessment, not a category. It is
  the classifier's own summary and stays on `ClassificationResult`.
- **`uncertainty`** — remains uncertainty metadata (see §3); it is never
  turned into `Evidence.confidence` or any other Evidence field.
- **`ClassificationResult.indicators`** — the domain model's own
  structured `tuple[EvidenceCategory, ...]` field is deliberately **not**
  used as an independent second signal alongside the seven free-text
  fields above. Using both would either be redundant (a consistent
  classifier populates `indicators` as a superset marker of what its
  free-text fields already say) or risk producing a category with no
  explainable free-text content behind it. The free-text fields are fused
  because they are the actual evidentiary content; `indicators` is left
  for a future classifier adapter or fusion strategy to use directly if a
  concrete need for it arises.
- **THREAT** — no `ClassificationResult` field corresponds to it, so AI
  evidence for THREAT is never produced by this fusion layer; only RULE
  evidence can currently surface THREAT. This is a gap in field coverage,
  not a bug in the mapping logic.

## 6. Deduplication policy

- Each `fuse()` call derives **at most one** AI `Evidence` item per
  category, because each of the seven mapped fields corresponds to a
  distinct category and a `ClassificationResult` can only hold one value
  per field — duplicate AI evidence for the same category within one call
  is structurally impossible, reinforced by an explicit (normally
  unreachable) `seen_categories` guard, mirroring
  `RuleBasedEvidenceProvider`'s own defensive-dedup convention.
- RULE and AI evidence for the **same category** are never merged or
  deduplicated against each other — they have different provenance and
  both remain in the fused output. `EvidenceProvider`-sourced RULE
  evidence continues to follow the existing prefilter's own duplicate
  handling (see `prefilter/README.md` §5) unchanged.
- `fuse()` is a pure, stateless function of its inputs: the same
  `rule_evidence` + `classification_result` + `transcript_segments`
  always produces the same output, and repeated calls do not accumulate
  or suppress anything across calls — there is no fusion-level history.

## 7. What fusion does NOT do

- **No risk scoring.** `EvidenceFusion` never computes a score, risk
  level, or interaction bonus — that remains entirely
  `DeterministicRiskEngine`'s job (see `risk/README.md`).
- **No contextual suppression.** Fusion does not judge whether a RULE or
  AI finding is a false positive; it passes both through faithfully, the
  same architectural stance `DeterministicRiskEngine` already takes (see
  `risk/README.md` §10).
- **No transcript-quote fabrication.** AI evidence never claims to be
  verbatim transcript text.
- **No invented attribution.** AI evidence never fabricates a timestamp
  or segment_id the classifier did not itself provide.
- **No provenance rewriting.** Fusion never changes a RULE item's
  `source` to `AI` (or vice versa), and never merges two items from
  different sources into one.

## 8. Relationship to RiskEngine

The intended pipeline is:

```
Transcript
    -> RuleBasedEvidenceProvider -> RULE Evidence
                                          \
AI Classifier -> ClassificationResult -> EvidenceFusion -> Fused Evidence
                                          /
                                   (RULE Evidence passed through)
                                                |
                                                v
                                    DeterministicRiskEngine
                                                |
                                                v
                                          RiskAssessment
```

`DeterministicRiskEngine.assess()` takes a plain `Sequence[Evidence]` and
already treats every item by its `category` for scoring purposes,
regardless of `source` — it does not currently weight `RULE` differently
from `AI`. That is a real, documented limitation (see `risk/README.md`
§8/§11): today, one AI-derived AUTHORITY item and one RULE-derived
AUTHORITY item each contribute their category's weight once (deduplicated
by category, not by source), the same as if both were RULE. Making the
risk engine source-aware (e.g. trusting `RULE` more than `AI`) is a
natural future extension of `risk/config.py`, not a change required by
this step.

## 9. Limitations

- No cross-field reasoning: each of the seven fields is treated
  independently; fusion does not check whether, say,
  `credential_request` and `urgency_description` are actually about the
  same underlying request in the transcript, or contradict each other.
- No deduplication *across* separate `fuse()` calls: if the same
  `ClassificationResult` is (incorrectly) passed to `fuse()` multiple
  times, each call independently regenerates the same AI evidence items
  (with the same deterministic `evidence_id`s) — deterministic, but not
  deduplicated across calls, since fusion is intentionally stateless.
- `evidence_id` for AI items is derived from
  `classification_result.classification_id` + category; if a caller
  reuses the same `classification_id` for two logically different
  classification results, their AI `Evidence` objects would collide on
  `evidence_id`. Fusion does not currently guard against this — it trusts
  `classification_id` to be unique per genuine classification pass, the
  same way `RuleBasedEvidenceProvider` trusts `segment_id` to be unique
  per real transcript segment.
- `transcript_segments` is currently used only for the dangling-`segment_id`
  defensive check described in §3 — it does not otherwise enrich or alter
  AI evidence content.

**The evidence fusion layer aggregates RULE and AI findings; it does not
itself establish that a conversation is fraudulent, and neither does
anything it produces for the risk engine to consume.**
