# Perception Firewall

## Purpose

A privacy-first, local social-engineering/scam detection assistant designed for
Windows on Snapdragon PCs. It listens to audio (microphone or recordings),
transcribes it locally, and classifies the ongoing conversation for
social-engineering/scam risk — surfacing warnings with evidence quotes,
entirely on-device.

## Development approach

Application logic is developed and unit-tested against mockable inference
interfaces, independent of any specific inference runtime. Qualcomm Hexagon
NPU execution is only available on real Snapdragon hardware, so on-device
NPU inference is validated separately, via Qualcomm AI Hub Workbench against
real Snapdragon devices (see "Validated Qualcomm evidence" below) — not as
part of local application unit testing.

## Validated Qualcomm evidence

Real Qualcomm AI Hub Workbench measurements already exist for:

- **Whisper-Base** on Snapdragon X Elite CRD (ONNX / precompiled QNN,
  100% of reported operators on NPU)
- **Qwen3-1.7B** (W4A16, geniex_qairt, context length 512) on Snapdragon
  X Elite CRD (100% of reported operators on NPU, all four collection
  parts compiled/linked/profiled)

These are **isolated AI Hub Workbench compile/profile results**. They are
**not** evidence that the complete Perception Firewall application has been
tested end-to-end on an HP retail Snapdragon PC. That claim must never be
made until such a test has actually been performed.

## Architecture principle

Application logic must remain independent of Qualcomm-specific inference
runtimes. The pipeline stages (audio capture, transcript buffering,
deterministic prefilter, classifier, risk fusion, UI) are designed against
interfaces, not concrete model runtimes, so they can be built and tested
locally and later wired to real on-device inference on Windows/Snapdragon
without rewriting application logic.

See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) and
[`docs/ADR-001-runtime-separation.md`](../docs/ADR-001-runtime-separation.md)
for details.

## Status

Implemented so far:

- **Domain model** — model-independent core types (transcript segments,
  evidence, classification results, risk assessments).
- **Interfaces and deterministic mocks** — abstract contracts for audio,
  speech-to-text, classification, evidence, and risk, plus dependency-free
  mock implementations for local development and testing.
- **Deterministic transcript evidence prefilter** — rule-based extraction
  of behavioral indicators from transcript text.
- **Deterministic risk engine** — configurable, explainable aggregation of
  evidence into a risk assessment, with hysteresis to avoid risk-level
  flicker.
- **Provenance-preserving evidence fusion** — combines rule-based and
  AI-classifier evidence into one collection without letting AI
  interpretation be mistaken for observed fact.
- **Comprehensive automated tests** — 231 tests passing.
- **Snapdragon model compilation/profile validation** — Whisper-Base and
  Qwen3-1.7B (W4A16) compiled and profiled via Qualcomm AI Hub Workbench on
  Snapdragon X Elite CRD hardware (see "Validated Qualcomm evidence" above).

Not yet implemented: live microphone capture, on-device Qualcomm runtime
integration (Whisper/Qwen3 inference wired into the application), the UI,
and end-to-end application deployment on Snapdragon hardware. Full
application latency and product readiness have not been measured or
claimed — those are future stages.
