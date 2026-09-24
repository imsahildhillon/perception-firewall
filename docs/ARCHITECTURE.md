# Architecture: Two-Layer Separation

Perception Firewall is developed and shipped as two distinct layers that do
not share a Python dependency stack or an execution environment.

## Layer 1 — Model export/build tooling (local development only)

- `snapdragon-ai` conda environment (Whisper-Base export/profiling)
- `qwen3-npu` conda environment (Qwen3-1.7B export/profiling)
- Qualcomm AI Hub Workbench (cloud compile/profile jobs against real
  Snapdragon devices)
- Model export/profile job scripts and their output artifacts
  (`experiments/`)

This layer exists solely to produce compiled model artifacts (ONNX + QNN
context binaries for Whisper, Genie/QAIRT context binaries for Qwen3) and to
validate them against real Snapdragon hardware via AI Hub Workbench. It runs
only in the local development environment and is never packaged or shipped.

## Layer 2 — Application runtime (Windows ARM64 / Snapdragon target)

- Windows on Snapdragon (ARM64)
- Compiled Whisper runtime (ONNX Runtime QNN Execution Provider)
- Compiled Qwen3 runtime (Genie SDK)
- The Perception Firewall application pipeline (`app/src/perception_firewall`)
- The user-facing warning UI

This is the layer that actually ships. It consumes the *compiled artifacts*
produced by Layer 1 — it does not depend on `transformers`, `torch`, or
either conda environment. Application pipeline code is written against
interfaces (see `app/src/perception_firewall/interfaces/`) so it can be
developed and unit-tested locally with mocked/stub inference, then wired
to the real compiled runtimes only when running on Snapdragon hardware.

## Explicit statement

`snapdragon-ai` and `qwen3-npu` are **development/export environments only**.
They are **not** application runtime environments, are not shipped, and the
application must never import from or depend on packages installed in them.
