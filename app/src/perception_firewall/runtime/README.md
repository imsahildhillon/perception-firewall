# Whisper Snapdragon Runtime Adapter

## Why runtime integration is isolated

`WhisperRuntimeAdapter` implements the existing `SpeechToTextEngine`
interface using the runtime path the STEP 9 investigation found and
verified by direct inspection of the installed Qualcomm SDK: **ONNX
Runtime + the Qualcomm QNN Execution Provider**, running a precompiled
encoder/decoder ONNX-wrapped-QNN-context-binary pair.

That investigation also found real, concrete risks worth designing
around from day one: `onnxruntime-qnn` is a specific, platform-locked ORT
build (only one `onnxruntime` variant can be installed at a time — the
SDK's own code enforces this), and the eventual Qwen3/GenieX runtime may
have its own, currently-unverified dependency footprint. Keeping this
whole package's optional dependencies (`onnxruntime`, `transformers`)
strictly out of the core application (`app/pyproject.toml` remains
`dependencies = []`) means:

- The domain model, interfaces, prefilter, risk engine, evidence fusion,
  transcript buffer, and pipeline orchestration continue to run and test
  anywhere, with zero ML dependencies, exactly as before.
- This package can be *imported* safely in any environment — nothing in
  it imports `onnxruntime` or `transformers` at module load time.
- *Constructing* a real, working `WhisperRuntimeAdapter` requires those
  optional dependencies to be installed and requires real
  Windows-on-Snapdragon hardware — and fails with a clear
  `SpeechRecognitionError` explaining exactly what's missing if they
  aren't, rather than silently falling back to something fake.

## Snapdragon runtime requirements

Confirmed by STEP 9's direct inspection of
`qai_hub_models/utils/onnx/torch_wrapper.py`:

```python
if os.name != "nt" or "Qualcomm" not in platform.processor():
    install_instructions = (
        "NPU execution is supported only on Windows on Snapdragon devices."
    )
```

`platform_guard.py` reimplements this same check (`os.name == "nt"` and
`"qualcomm" in platform.processor().lower()`), with the platform
information injectable via `PlatformInfo`, so it is deterministically
unit-testable without needing to run on Windows-on-Snapdragon hardware.
**Passing this check does not prove NPU execution will succeed or has
ever been exercised** — it only means the host appears compatible with
the documented runtime path. Real validation requires running actual
inference on real hardware.

## ONNX Runtime + QNN architecture

```
AudioChunk
    |
    v
WhisperFeatureExtractor  (transformers-backed; abstract boundary)
    |
    v
input_features [1,80,3000] float16
    |
    v
WhisperEncoderSession.run()  --(onnxruntime.InferenceSession, QNNExecutionProvider)-->  EncoderOutput (12 cross-attention KV tensors)
    |
    v
decoder_loop.run_decoder_loop()  (pure Python, no tensor library)
    |  each iteration calls:
    v
WhisperDecoderSession.run()  --(onnxruntime.InferenceSession, QNNExecutionProvider)-->  DecoderStepOutput (logits + updated self-attention KV)
    |
    v
WhisperTokenizer.decode()  (transformers-backed; abstract boundary)
    |
    v
TranscriptSegment
```

## Encoder/decoder separation

`sessions.py` defines `WhisperEncoderSession` and `WhisperDecoderSession`
as abstract contracts using only opaque (`object`-typed) tensors — no
numpy, no onnxruntime, nothing tensor-library-specific. This is what lets
`decoder_loop.py` (the autoregressive loop itself) be pure Python,
independently unit-tested with a deterministic fake session, and
completely decoupled from the concrete backend.

`onnx_sessions.py` provides the real implementation
(`WhisperOnnxEncoderSession`, `WhisperOnnxDecoderSession`), which:

- Imports `onnxruntime` (and the `numpy` it transitively requires)
  lazily, inside `__init__`, never at module import time.
- Loads the encoder/decoder `.onnx` files via
  `onnxruntime.InferenceSession(..., providers=["QNNExecutionProvider"])`
  — mirroring `qai_hub_models.utils.onnx.torch_wrapper.
  OnnxModelTorchWrapper.OnNPU`, which STEP 9 found and verified is the
  actual mechanism the Qualcomm SDK itself uses for this same artifact
  type.
- **Introspects the loaded ONNX graph's own input/output tensor names and
  shapes** to discover the self-attention KV cache layout (how many
  layers, what shape) rather than hard-coding whisper-base-specific
  architecture constants (layer count, head count, head dimension)
  anywhere in this code.
- Owns all backend-specific tensor construction — zero-initializing the
  self-attention KV cache on the decoder's first step, and building the
  sliding-window `attention_mask` per step — exactly matching the
  behavior STEP 9 found in the reference harness's own decode loop
  (`HfWhisperApp._transcribe_single_chunk`).

**This has not been exercised against real Windows-on-Snapdragon
hardware or a real `onnxruntime` + `onnxruntime-qnn` installation in this
step.**

## Tokenizer boundary

STEP 9 found the reference harness resolves the tokenizer, decoder-start
token ID, EOT token ID, and feature-extractor config via `transformers`
(`WhisperConfig.from_pretrained`, a Whisper tokenizer class). `tokenizer.py`
defines `WhisperTokenizer` as an abstract contract (`start_of_transcript_
token_id`, `eot_token_id`, `decode()`) and provides
`TransformersWhisperTokenizer`, a concrete implementation backed by
`transformers`, imported lazily. No token ID is ever hard-coded anywhere
in `decoder_loop.py` or `adapter.py` — every one comes from this
boundary. If `transformers` is not installed, construction fails clearly
with `SpeechRecognitionError` — there is no fallback tokenizer.

`feature_extraction.py` follows the identical pattern for audio
preprocessing (`WhisperFeatureExtractor` abstract boundary,
`TransformersWhisperFeatureExtractor` concrete implementation backed by
`transformers`' own `WhisperFeatureExtractor`) — deliberately not a
reimplementation of Whisper's mel-filterbank algorithm, since STEP 9
found no evidence justifying a different one and reinventing it without
that evidence would risk a numerical mismatch against the compiled
encoder graph.

## Optional dependency strategy

| Dependency | Where it's needed | Import style |
|---|---|---|
| `onnxruntime` (+ `onnxruntime-qnn` on the real target) | `onnx_sessions.py` | Lazy, inside `__init__` |
| `numpy` | `onnx_sessions.py` (transitively required by `onnxruntime`) | Lazy, alongside `onnxruntime` |
| `transformers` | `tokenizer.py`, `feature_extraction.py` | Lazy, inside `__init__` |

None of these appear in `app/pyproject.toml`, which remains
`dependencies = []`. Every module in this package can be imported in any
environment (verified: importing `perception_firewall.runtime` pulls in
no forbidden module — see the STEP 10 report). Only *constructing* a
`TransformersWhisperTokenizer`, `TransformersWhisperFeatureExtractor`,
`WhisperOnnxEncoderSession`, or `WhisperOnnxDecoderSession` requires its
respective optional package, and each fails with a clear
`SpeechRecognitionError` (never a raw `ImportError`, `onnxruntime`
exception, or `transformers` exception) if that package is missing.

## Device validation

See "Snapdragon runtime requirements" above. `check_snapdragon_windows_
host()` is a pure function over an injectable `PlatformInfo`, called by
`WhisperRuntimeAdapter.__init__` before constructing any session — a host
that fails this check never gets as far as attempting to load a model.

## What is implemented

- `WhisperRuntimeConfig` / `WhisperModelPaths` / `WhisperTokenizerConfig`
  / `WhisperDecodeConfig` — immutable configuration, no hard-coded paths
  or device names anywhere.
- `check_snapdragon_windows_host()` — deterministic, injectable device
  guard.
- `WhisperEncoderSession` / `WhisperDecoderSession` — backend-agnostic
  session abstraction.
- `run_encoder()` / `run_decoder_loop()` — the pure, fully-tested
  autoregressive decode loop, modeling the exact behavior STEP 9 found
  in the reference harness.
- `WhisperTokenizer` / `WhisperFeatureExtractor` — abstract boundaries,
  each with a real `transformers`-backed concrete implementation.
- `WhisperOnnxEncoderSession` / `WhisperOnnxDecoderSession` — the real
  ONNX Runtime + QNN Execution Provider implementation.
- `WhisperRuntimeAdapter` — the `SpeechToTextEngine` implementation
  wiring all of the above together, with model-path validation, the
  device guard, and error translation (every failure becomes
  `SpeechRecognitionError`, never a raw runtime exception).

## What remains hardware-dependent

- Whether `onnxruntime-qnn` and its QNN Execution Provider actually load
  and execute correctly on real Windows-on-Snapdragon hardware, using the
  real compiled `encoder.onnx`/`decoder.onnx` artifacts.
- Whether the introspected self-attention KV cache tensor names/shapes in
  `onnx_sessions.py` match the real artifact exactly (this was designed
  against the tensor names/shapes recorded in
  `experiments/whisper_base_x_elite_npu/.../metadata.json`, but has not
  been run against the real `.onnx` files).
- Whether `transformers`' `WhisperConfig`/tokenizer/feature-extractor for
  `openai/whisper-base` produce token IDs and mel features that are
  numerically compatible with this specific compiled artifact.
- End-to-end transcription accuracy and latency — nothing here measures
  either.
- Whether the device-guard's Windows+Qualcomm-processor check is
  sufficient in practice, or whether x64 emulation on real Snapdragon
  hardware passes it while still failing at actual QNN EP execution (an
  open question STEP 9 flagged and did not resolve).

**No claim is made anywhere in this codebase that Whisper runtime
inference has been executed or validated on real hardware.** This step
implements the adapter architecture and its testable boundary only.

## How actual Snapdragon validation will later be performed

1. On real Windows-on-Snapdragon hardware, in an isolated environment,
   install `onnxruntime` (the QNN-EP-enabled build) and `transformers`.
2. Construct a real `WhisperRuntimeAdapter` (no injected fakes) pointed
   at the real, locally-present `encoder.onnx`/`decoder.onnx` files.
3. Feed it a known `AudioChunk` and compare the transcribed text against
   a known-correct reference transcription.
4. Only once that has actually happened does any claim of "Whisper
   Snapdragon runtime execution validated" become honest — nothing in
   this repository makes that claim yet.
