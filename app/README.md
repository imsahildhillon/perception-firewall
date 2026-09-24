# Perception Firewall

## Purpose

A privacy-first, local social-engineering/scam detection assistant designed for
Windows on Snapdragon PCs. It listens to audio (microphone or recordings),
transcribes it locally, and classifies the ongoing conversation for
social-engineering/scam risk — surfacing warnings with evidence quotes,
entirely on-device.

## Current development hardware

Apple Silicon Mac M2.

**Important limitation:** the Mac does not provide Qualcomm Hexagon NPU
execution. Application logic in this repository is being developed and
unit-tested on the Mac against mockable inference interfaces; real on-device
NPU inference can only be exercised on actual Snapdragon hardware.

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
interfaces, not concrete model runtimes, so they can be built and tested on
the Mac and later wired to real on-device inference on Windows/Snapdragon
without rewriting application logic.

See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) and
[`docs/ADR-001-runtime-separation.md`](../docs/ADR-001-runtime-separation.md)
for details.

## Status

Scaffolding only. No application logic, dependencies, or UI have been
implemented yet.
