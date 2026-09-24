# Interface Layer

Application interfaces are intentionally independent from model/runtime
implementations.

This package defines what the Perception Firewall pipeline needs from
audio, speech recognition, classification, evidence extraction, and risk
fusion — as abstract contracts (`AudioSource`, `SpeechToTextEngine`,
`TextClassifier`, `EvidenceProvider`, `RiskEngine`) plus a clean
application-level error model (`errors.py`). None of these contracts
mention Whisper, Qwen, transformers, torch, ONNX, ONNX Runtime, QNN,
Genie, or Qualcomm AI Hub by import — only in comments/docstrings that
explain what a future concrete implementation will be.

## Development vs. target implementations

**Development** (this repository, today, in a local development
environment):

```
Local development environment
 -> MockSpeechToTextEngine / MockTextClassifier   (interfaces/mocks/)
 -> application pipeline
```

`MockSpeechToTextEngine` and `MockTextClassifier` are deterministic test
doubles. They perform no real speech recognition and no real
classification — they return fixed, known outputs for a small set of
fixture scenarios so the rest of the application can be built and tested
without any ML dependency and without a Snapdragon device. They must never
be presented as, or mistaken for, real model output.

**Target** (future work, not implemented in this step):

```
Windows ARM64 Snapdragon
 -> QualcommWhisperAdapter / QualcommQwenClassifier
 -> application pipeline
```

`QualcommWhisperAdapter` and `QualcommQwenClassifier` will implement the
same `SpeechToTextEngine` / `TextClassifier` interfaces, backed by the
compiled Whisper-Base and Qwen3-1.7B artifacts already validated via
Qualcomm AI Hub Workbench (see `experiments/` and `docs/ARCHITECTURE.md`).
**They are intentionally not implemented in this step.**

## What the Workbench results do and do not establish

The AI Hub Workbench measurements already on record — Whisper-Base
(encoder/decoder, 100% NPU) and Qwen3-1.7B (W4A16, all four collection
parts, 100% NPU) on a Snapdragon X Elite CRD — establish **model-level
feasibility on real Snapdragon hardware**. They do not establish that this
application has been integrated with those runtimes and run end-to-end.
That is a separate, later hardware-integration step, and requires actual
Windows-on-Snapdragon hardware to attempt at all: **the local development
environment cannot execute Qualcomm Hexagon NPU inference**, so no adapter
targeting the NPU can be built or tested there.

## Why this boundary exists

Keeping the pipeline's dependency on models behind these interfaces means:

- Pipeline code (prefilter, risk fusion, UI) can be written and tested
  fully in the local development environment, today, using the mocks.
- Swapping a mock for a real Qualcomm adapter later requires no change to
  any code that depends only on the interfaces.
- The two model-export environments (`snapdragon-ai`, `qwen3-npu`) and
  their conflicting dependencies (see `docs/ADR-001-runtime-separation.md`)
  never need to be installed alongside the application; a real adapter
  loads only its compiled artifact, not a Python ML stack.
