# Transcript Buffer

## Responsibility

`TranscriptBuffer` holds one session's `TranscriptSegment` objects in
chronological order. That is its entire job.

It is explicitly **not** responsible for, and must never be extended to
perform: speech recognition, evidence extraction, classification, risk
scoring, UI, or model inference of any kind. Those are the responsibility
of `SpeechToTextEngine`, `EvidenceProvider`, `TextClassifier`,
`RiskEngine`, and the future UI layer, respectively — `TranscriptBuffer`
only manages state between them.

## Behavior

- `append(segment)` — accepts a `TranscriptSegment`, preserves the exact
  object given (no copying, no mutation), and requires non-decreasing
  `start_time` ordering.
- `segments()` — returns the buffered segments as a `tuple` (an immutable
  snapshot), never the internal list, so a caller cannot mutate buffer
  state through the returned value.
- `text()` — joins segment texts with a deterministic separator (a single
  space by default), in chronological order, verbatim — nothing is
  rewritten, paraphrased, truncated, or reordered.
- `clear()` — removes all buffered segments.
- `size()` — returns the current segment count.

## Out-of-order policy

If `append()` receives a segment whose `start_time` precedes the most
recently buffered segment's `start_time`, it is **rejected** — raising
`TranscriptBufferError` — rather than silently reordered.

This is the simplest policy consistent with the existing domain model
(`TranscriptSegment.start_time` is already a validated, non-negative,
session-relative float offset — see `domain/transcript.py`), and it keeps
chronological ordering an invariant the buffer can actually guarantee: a
buffer that silently reorders input can never prove to a caller that
"segments()` is in order" without re-sorting on every read, and it would
also mask a genuine upstream bug (e.g. a misbehaving speech-to-text
engine emitting segments out of sequence) instead of surfacing it.

## No bounded-buffer behavior

An optional bounded/rolling buffer (dropping the oldest segments past
some limit) was considered and deliberately **not** implemented. Nothing
in the current architecture needs it yet, and adding it now would be
complexity without a concrete requirement driving it — a future step can
add bounding if a real memory constraint appears.
