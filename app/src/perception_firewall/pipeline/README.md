# Pipeline: Session Lifecycle and Orchestration

## Purpose

This package proves the application architecture works end-to-end —
`SpeechToTextEngine -> TranscriptBuffer -> EvidenceProvider + TextClassifier
-> EvidenceFusion -> RiskEngine -> RiskAssessment` — using the existing
interfaces, deterministic mocks, rule prefilter, evidence fusion, and risk
engine, entirely without a real model or Qualcomm runtime. It contains two
things: `Session` (lifecycle + transcript state for one monitoring
session) and `ApplicationPipeline` (stateless orchestration connecting the
injected components).

## Session lifecycle

`Session` wraps a `session_id`, the existing domain `SessionState` enum
(no duplicate state enum was introduced), and a per-session
`TranscriptBuffer`.

```
IDLE --start()--> ACTIVE --pause()--> PAUSED --resume()--> ACTIVE
                     |                    |
                     +---- end() --------+---> ENDED (terminal)
                     |                    |
                     +-- mark_error() ---+---> ERROR (terminal)

reset() : any state (including ENDED, ERROR) -> IDLE, unconditionally
```

- Every transition other than `reset()` requires a specific source state
  (`start()` only from IDLE, `pause()` only from ACTIVE, `resume()` only
  from PAUSED, `end()` from ACTIVE or PAUSED); an invalid one raises
  `SessionError` naming the attempted operation, the session's actual
  state, and its `session_id`. `resume()` and `start()` both land on
  ACTIVE but are deliberately not interchangeable — `resume()` is
  rejected from IDLE, since nothing was paused to resume from.
- `mark_error()` is how `ApplicationPipeline` reports a component failure
  onto a session (see "Error boundaries" below) — allowed from any state
  except `ENDED`, since an already-ended session cannot subsequently fail.
- `reset()` is the one operation not gated by the transition table: it
  works from any state, including the two terminal ones, and returns the
  session to `IDLE` with an empty buffer. `session_id` is unchanged by
  `reset()` — a reset session is the same identity starting over, not a
  new one.

## Pipeline responsibility

`ApplicationPipeline.process_segments(session, segments)`:

1. Validates `session` is an active `Session`.
2. Appends `segments` (which may be `None`/empty — re-assessing whatever
   is already buffered is a valid call, not an error) to
   `session.buffer`.
3. Reads `session.buffer.text()` and `session.buffer.segments()`.
4. Calls the injected `EvidenceProvider.analyze(...)` for RULE evidence.
5. Calls the injected `TextClassifier.classify(...)` for a
   `ClassificationResult`.
6. Calls `EvidenceFusion.fuse(...)` to combine both into one
   provenance-preserving evidence collection.
7. Calls the injected `RiskEngine.assess(...)` and returns its
   `RiskAssessment`.

`process_audio_chunk(session, audio)` is a thin wrapper: it calls the
injected `SpeechToTextEngine.transcribe(audio)` to get segments, then
delegates to `process_segments`. Real audio input is out of scope for
this step (see "Why real model/runtime integration is deferred") — this
method exists so the architecture is provably ready for it.

**Risk scoring happens nowhere in this package.** Every score, level, and
contribution comes from the injected `RiskEngine`; the orchestrator only
moves data between components.

## Dependency injection

`ApplicationPipeline.__init__` takes five dependencies, every one an
interface (`SpeechToTextEngine`, `TextClassifier`, `EvidenceProvider`,
`RiskEngine`) or, for `EvidenceFusion`, the one concrete
provenance-preserving implementation from evidence fusion (it has no
competing implementation, so no interface was introduced for it — see
`evidence/README.md`). Nothing in this package imports or hard-codes a
concrete Qualcomm/Whisper/Qwen implementation; only the existing mocks
(`MockSpeechToTextEngine`, `MockTextClassifier`) and deterministic
components (`RuleBasedEvidenceProvider`, `EvidenceFusion`,
`DeterministicRiskEngine`) are used in this step's tests.

## Error boundaries

Every component the orchestrator calls raises one of the existing
application-level errors (`SpeechRecognitionError`, `ClassificationError`,
`EvidenceExtractionError`, `EvidenceFusionError`, `RiskEngineError`) or, at
the pipeline/session boundary itself, the two added in this step
(`TranscriptBufferError`, `SessionError`) — all subclasses of
`PerceptionFirewallError`.

`process_audio_chunk` and `process_segments` both catch
`PerceptionFirewallError` around their component calls, call
`session.mark_error()`, and **re-raise the original exception unchanged**
— never swallowed, never replaced with a generic error, never allowed to
produce a partial/successful `RiskAssessment`. The caller always knows
exactly which component failed and why, and the session's state honestly
reflects that a failure occurred.

## Session isolation

Two `Session` objects with different `session_id` values never share
state:

- Each owns its own `TranscriptBuffer` instance — no shared mutable state.
- `DeterministicRiskEngine`'s hysteresis (see `risk/state.py`) is keyed
  strictly by `session_id` string, so a different `session_id` starts with
  no risk history regardless of what any other session has done.
- `ApplicationPipeline` itself holds no per-session state at all — it is
  a stateless orchestrator over whatever `Session` object is passed to
  each call, so there is no pipeline-level registry that could leak state
  between sessions.

`ApplicationPipeline.reset_session(session)` clears both layers together:
`session.reset()` (buffer + lifecycle state) and, if the injected
`RiskEngine` exposes a `reset_session(session_id)` method (an addition
specific to `DeterministicRiskEngine`, not part of the `RiskEngine`
interface — see `risk/engine.py`), that too. This method degrades
gracefully with any `RiskEngine` implementation that doesn't expose it.

## Why real model/runtime integration is deferred

This step proves the architecture — every stage, every interface boundary,
every error path — works correctly using deterministic components only:
the existing mocks (`MockSpeechToTextEngine`, `MockTextClassifier`), the
rule prefilter, evidence fusion, and the deterministic risk engine. No
microphone capture, no real Whisper/Qwen inference, no Qualcomm runtime
(QNN/ONNX Runtime/Genie), no live UI, and no threading/async streaming are
implemented here — those require actual Snapdragon hardware to validate
meaningfully and are separate, later steps. Because every pipeline stage
already depends only on interfaces, wiring in a real
`QualcommWhisperAdapter` / `QualcommQwenClassifier` later requires no
change to `ApplicationPipeline`, `Session`, or `TranscriptBuffer`.

## Deterministic test strategy

Every end-to-end test in this step uses only deterministic components —
the existing mocks and the rule/risk/fusion layers — so a given input
always produces the same `RiskAssessment` (aside from `assessment_id` and
`timestamp`, which are documented as non-deterministic identity/time
fields on the domain model itself). No test in this step depends on
network access, real model weights, or Snapdragon hardware.
