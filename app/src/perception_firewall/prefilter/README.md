# Prefilter

## 1. Purpose

The prefilter is a deterministic, rule-based `EvidenceProvider`. It scans
transcript segments for a fixed set of behavioral-indicator phrases and
produces `Evidence` — it does not decide whether a conversation is a scam.
That judgment belongs to risk fusion (a later, not-yet-built stage), which
weighs evidence from multiple sources (this prefilter, the future Qwen3
classifier adapter, and potentially others).

**The prefilter provides deterministic behavioral indicators. It does not
establish that a conversation is fraudulent.**

## 2. Evidence categories

Uses the existing domain `EvidenceCategory` enum unchanged: `AUTHORITY`,
`URGENCY`, `THREAT`, `PAYMENT`, `CREDENTIAL_REQUEST`, `REMOTE_ACCESS`,
`SECRECY`, `IDENTITY_PRESSURE`.

## 3. Pattern configuration

All phrases live in `patterns.py`, as an immutable
`Mapping[EvidenceCategory, tuple[str, ...]]` (`PATTERNS`), plus a matching
`EXPLANATION_TEMPLATES` mapping used to render each category's
human-readable explanation. No string literals are scattered through the
matching or provider code — adding a new phrase means adding one string to
one tuple in `patterns.py`; no other file changes.

**The initial pattern set is an engineering prototype and has not been
empirically validated as a fraud-detection model.** It was seeded from the
literal phrase list specified for this step, with two documented
additions (also called out in `patterns.py`'s module docstring):

- `"authority"` / `"authorities"` were added to `AUTHORITY` because none
  of the originally listed ten AUTHORITY phrases
  (police/officer/government/bank/tax department/tax
  authority/court/legal department/compliance/customs) match the word
  "authorities" itself, yet the specified AUTHORITY_PAYMENT test scenario
  ("I am calling from the authorities...") requires an AUTHORITY match.
- `"verify your account"` was added to `IDENTITY_PRESSURE` because none of
  the originally listed seven IDENTITY_PRESSURE phrases match it, yet the
  specified REMOTE_ACCESS test scenario ("...so I can verify your
  account.") requires an IDENTITY_PRESSURE match.

## 4. Matching behavior

Implemented in `matcher.py`, standard library only (`re`):

- **Case-insensitive** — `re.IGNORECASE`.
- **Unicode-safe** — Python 3 `str` regexes are Unicode-aware by default;
  `\b`/`\w` recognize Unicode letters, not just ASCII, so a pattern
  embedded in non-Latin-script surrounding text still matches correctly.
- **Whitespace-normalized** — multi-word phrases join their tokens with
  `\s+` rather than a literal space, so double spaces, tabs, or line
  breaks between words don't block a match.
- **Punctuation-tolerant without stripping punctuation** — nothing rewrites
  the input; `\b` word-boundary assertions already treat punctuation as
  non-word characters, so `"blocked."` still matches the pattern
  `"blocked"`.
- **Word-boundary protected** — every compiled phrase is wrapped in
  `\b...\b`, so `"pin"` does not match inside `"spinach"`, and no pattern
  matches as a sub-word fragment of an unrelated word.
- **Original text preserved** — matching reads `segment.text` as-is;
  `Evidence.evidence_text` is always the untouched original segment text,
  never a normalized or truncated copy.

**Known limitation:** apostrophe style is not normalized. A pattern using
a straight apostrophe (`don't`) will not match text using a curly
apostrophe (`don't`, U+2019). Given the instruction to avoid NLP
dependencies and keep this simple, this was left undone; if it matters in
practice, normalizing apostrophe variants before matching would be a small,
self-contained follow-up.

## 5. Duplicate handling

`find_matches()` is presence-only: each configured phrase is checked once
per segment with `regex.search()`, not counted, so a phrase repeated
multiple times within one segment (e.g. "urgent... urgent...") yields
exactly one match and therefore exactly one `Evidence` object for that
(segment, category, phrase) combination — no unbounded duplication.

`RuleBasedEvidenceProvider._analyze_segment()` additionally keeps an
explicit `seen` set as a documented, defensive second layer, even though
`find_matches()`'s presence-only design should already make it a no-op.

Two **different** phrases of the same category matching within the same
segment (e.g. both `"transfer"` and `"payment"` present) each produce
their own `Evidence` object — this is intentional, not a duplicate: they
are different observed phrases and each is independently explainable.

Evidence from **different** segments is never deduplicated against each
other, even for an identical phrase — repeated behavior across segments
(i.e. over time within a session) is itself meaningful and is preserved.

## 6. Evidence provenance

Every `Evidence` object produced here has `source = EvidenceSource.RULE`.
This component never claims AI provenance.

`confidence` is always `None`. A rule match means "the transcript contains
this indicator" — it is a boolean fact, not a calibrated probability of
malicious intent, and there is no defensible way to turn a keyword match
into a confidence score. Setting `confidence=1.0` because a rule matched
would misrepresent what was actually established.

`timestamp` is the wall-clock UTC time the prefilter evaluated the
segment (`datetime.now(timezone.utc)` at evidence-creation time) — **not**
the segment's audio-relative offset. `TranscriptSegment.start_time` /
`end_time` (float seconds, session-relative — see the domain layer) remain
the source of truth for where in the audio a segment falls; `segment_id`
is carried onto every `Evidence` object so it can always be traced back to
its originating segment and that segment's own timing.

## 7. Limitations

- Purely lexical: no semantics, no context across the whole conversation,
  no negation handling (`"do NOT give the OTP to anyone"` still matches
  `CREDENTIAL_REQUEST`, because the phrase "OTP" is present regardless of
  the surrounding negation).
- No cross-segment reasoning: each segment is evaluated independently; the
  prefilter itself does not track patterns building up across a session
  (that is risk fusion's job, using the evidence this component emits).
- Apostrophe-variant blind spot (see §4).
- The pattern list is short and manually curated; it was not derived from
  any labeled dataset.

## 8. False-positive risks

Some configured phrases are broad, common words that will legitimately
appear in entirely benign conversation:

- `"bank"` (AUTHORITY) matches any mention of a bank, including
  "the bank branch near my house is crowded" — nothing to do with a
  caller claiming institutional authority.
- `"today"` (URGENCY) matches almost any sentence that mentions the
  current day, e.g. "crowded today," with no urgency-pressure meaning at
  all.

Both are part of the literally specified initial pattern list and were
kept as specified rather than silently dropped. Their false-positive
behavior is captured in a regression test
(`test_benign_conversation_documents_known_false_positives` in
`app/tests/unit/test_prefilter.py`) so it is visible and intentional
rather than a silent surprise. If real-world use shows these patterns fire
too often, the fix is to remove or narrow them in `patterns.py` — no
matching-logic change would be required.

## 9. Why this is not a fraud classifier

The prefilter has no concept of "fraud," "scam," or intent. It cannot
weigh evidence, cannot use context beyond a single segment's text, and
produces no verdict of any kind — only a set of `Evidence` objects
describing which configured phrases were observed and why each category
they belong to is worth flagging. Turning a set of observed indicators
into an actual risk judgment is explicitly the job of a separate,
not-yet-built risk engine, which is expected to combine this prefilter's
output with output from other evidence sources.

## 10. Future relationship with Qwen3

`RuleBasedEvidenceProvider` and the future `QualcommQwenClassifier` (via
`TextClassifier`, not `EvidenceProvider`) are expected to run as
independent, complementary evidence sources over the same transcript:
this component catches known literal phrases deterministically and
cheaply; Qwen3 is expected to catch paraphrased, contextual, or novel
phrasing this rule set cannot. Risk fusion is expected to combine both.
Neither component depends on the other, and this prefilter has no
dependency on Qwen3, Whisper, or any Qualcomm runtime — see
`docs/ARCHITECTURE.md`.
