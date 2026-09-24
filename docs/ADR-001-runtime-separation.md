# ADR-001: Keep Qualcomm Model Export Tooling Separate from Application Runtime

## Status

Accepted (current engineering decision — not asserted as the only possible
architecture).

## Context

- Whisper-Base's export/profiling pipeline requires `transformers==4.56.2`.
- Qwen3-1.7B's export/profiling pipeline requires `transformers==5.7.0`.
- These two versions pin mutually exclusive `huggingface-hub` ranges
  (`<1.0,>=0.34.0` vs. `<2.0,>=1.5.0`), confirmed via PyPI metadata — they
  cannot be installed in the same Python environment.
- The local development environment cannot execute Qualcomm Hexagon NPU
  inference. All NPU validation to date has happened remotely via Qualcomm
  AI Hub Workbench against real Snapdragon X Elite hardware, not locally.
- The application's actual deployment target is Windows on Snapdragon
  (ARM64), a different OS and architecture from the local development
  environment used to build and test it.

## Decision

Model export/build tooling (the `snapdragon-ai` and `qwen3-npu` conda
environments, and all AI Hub Workbench export/profile scripts and outputs)
is kept entirely separate from the Perception Firewall application runtime.
The application depends only on the *compiled* model artifacts these
environments produce (ONNX/QNN context binaries, Genie/QAIRT context
binaries) and on stable interfaces, never on the export environments'
Python packages directly.

## Reason

1. Whisper and Qwen3 require incompatible Python dependency stacks
   (`transformers` 4.x vs. 5.x), so a single shared environment cannot
   export/run both models.
2. Qualcomm NPU execution is not available in the local development
   environment, so application logic must be structured to be developed
   and tested independently of any specific inference runtime, then
   integrated with real on-device runtimes only on actual Snapdragon
   hardware.
3. Separating the two layers means a dependency change needed for one
   model's export tooling can never break the other model's export tooling,
   and neither can break the application runtime, which doesn't depend on
   either.

## Consequences

- Application code must be written against interfaces/abstractions for
  speech-to-text and classification, not against `transformers`/`torch`
  APIs directly.
- Any future model swap or re-export only touches Layer 1
  (`docs/ARCHITECTURE.md`) and does not require changes to application code,
  provided the interface contract is preserved.
- End-to-end validation of the full application can only happen on real
  Windows-on-Snapdragon hardware; local development necessarily relies on
  mocked/stubbed inference until that point.

## Alternatives considered (not chosen)

- A single shared Python environment for both models — ruled out as
  impossible due to the `transformers`/`huggingface-hub` version conflict.
- Downgrading Qwen3-1.7B's tooling to `transformers==4.56.2` — not
  attempted; the checkpoint's tokenizer schema was confirmed incompatible
  with 4.x during feasibility testing.

This decision may be revisited if Qualcomm's tooling converges on a single
compatible dependency stack, or if the application architecture changes.
