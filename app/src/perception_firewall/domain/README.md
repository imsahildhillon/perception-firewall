# Domain Layer

This package defines Perception Firewall's core concepts as plain,
strongly-typed Python — `TranscriptSegment`, `Evidence`, `ClassificationResult`,
`RiskAssessment`, `SessionState`, and their supporting enums.

## Principles

1. **The domain layer is model-independent.** Nothing here knows about
   Whisper, Qwen, transformers, PyTorch, ONNX, ONNX Runtime, QNN, Genie, or
   Qualcomm AI Hub. It describes what the application reasons about, not
   which models or runtimes produce that reasoning.

2. **Evidence does not prove fraud.** `Evidence` and `ClassificationResult`
   represent observed indicators and their interpretation — they are
   signals to be weighed, never a verdict on a person.

3. **Risk is an engineering assessment.** `RiskAssessment` is the
   application's own fused judgment, built from the evidence available to
   it. It is not a claim of objective truth about what is happening in a
   conversation.

4. **AI output remains distinguishable from observed evidence.** Every
   model here keeps raw/observed material (e.g. `Evidence.evidence_text`,
   a transcript quote) separate from interpretation (e.g.
   `Evidence.explanation`, `ClassificationResult.overall_assessment`).
   Consumers of these models can always tell which is which.

5. **The domain layer must be usable without Qualcomm dependencies.** It
   depends only on the Python standard library, so it can be developed,
   imported, and unit-tested in any environment, with no `qai_hub`,
   `transformers`, `torch`, or `onnxruntime` installed.

6. **The same domain layer will be reused on Windows/Snapdragon.** These
   models are the stable contract between every other layer of the
   application (prefilter, classifier, risk fusion, UI) and are not
   expected to change when the underlying inference runtimes do.
