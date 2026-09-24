# Perception Firewall

Privacy-first, on-device social-engineering detection optimized for
Snapdragon-powered Windows PCs.

## Overview

Perception Firewall is designed to identify conversational
social-engineering signals as a call or conversation happens — entirely
on-device, with no audio or transcript leaving the machine. It watches for
behavioral indicators such as:

- authority impersonation
- urgency
- threats
- payment requests
- credential/OTP requests
- remote-access requests
- secrecy pressure
- identity pressure

The system combines **deterministic evidence extraction** (a rule-based
prefilter over the live transcript) with **structured AI interpretation**
(a classifier producing a structured, model-independent result), fuses
both into one provenance-preserving evidence collection, and feeds that
into a **deterministic risk engine** that produces an explainable,
auditable risk assessment.

**Perception Firewall is advisory.** It does not automatically transfer
money, does not automatically contact authorities, and does not
automatically block calls. Every assessment it produces is a signal for
the user to act on — the user remains in control of every action.

## Architecture

```text
Audio / Input
      │
      ▼
Speech-to-Text
      │
      ▼
Transcript Buffer
      │
      ├──────────────────┐
      ▼                  ▼
Deterministic Rules   Structured AI
      │                  │
      └────────┬─────────┘
               ▼
        Evidence Fusion
               │
               ▼
    Deterministic Risk Engine
               │
               ▼
        Risk Assessment
               │
               ▼
          User Interface
```

Every stage above the Speech-to-Text/AI boundary is built against
interfaces, not concrete model implementations, so the same architecture
runs today against deterministic mocks and later against real on-device
Snapdragon inference without being rewritten. See
[`app/README.md`](app/README.md) and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design and
current implementation status.

## Snapdragon validation

Real Qualcomm AI Hub Workbench measurements exist for the two models this
architecture targets, both compiled and profiled on Snapdragon X Elite CRD
hardware:

- **Whisper-Base** (speech-to-text) — ONNX / precompiled QNN, 100% of
  reported operators on NPU.
- **Qwen3-1.7B** (W4A16, GenieX QAIRT, context length 512) — 100% of
  reported operators on NPU, all four model-collection parts compiled,
  linked, and profiled.

These are isolated AI Hub Workbench compile/profile results. They
establish model-level feasibility on real Snapdragon hardware — they are
**not** evidence that the complete application has been run end-to-end on
a retail Snapdragon PC. That claim is not made anywhere in this
repository until such a test has actually been performed.

## Project structure

```
.
├── app/                  Application source (domain, interfaces, prefilter,
│                         evidence fusion, risk engine, transcript buffer,
│                         pipeline orchestration) and its test suite
├── docs/                 Architecture documentation and decision records
├── experiments/          Qualcomm AI Hub Workbench compile/profile records
├── FEASIBILITY.md        Technical feasibility study
└── RESEARCH.md           Competition and platform research
```

See [`app/README.md`](app/README.md) for current implementation status and
test count, and the per-package READMEs under `app/src/perception_firewall/`
for the design of each layer (domain model, interfaces, prefilter,
evidence fusion, risk engine, transcript buffer, pipeline).

## Status

Under active development. The application architecture — domain model,
interfaces, deterministic mocks, rule-based prefilter, evidence fusion,
deterministic risk engine, transcript buffer, and session/pipeline
orchestration — is implemented and covered by an automated test suite.
Real on-device Qualcomm runtime integration (wiring the compiled
Whisper-Base and Qwen3-1.7B models into the running application) and the
user interface are future work. See [`app/README.md`](app/README.md) for
the detailed breakdown.
