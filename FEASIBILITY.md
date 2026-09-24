# Stage 2 — Adversarial Technical Feasibility Study
## S1 Perception Firewall · S2 Paath · S3 Airlock

**Prepared:** 22 September 2026 · **Deadline:** 30 September 2026, 23:59 IST · **Solo developer · One immutable submission**

**Conventions:** `FACT` = verified against a cited primary source. `ANALYSIS` = my inference. `UNVERIFIED` = I could not confirm it. `UNKNOWN` = no number exists that I can obtain without hardware or a running experiment. I have not substituted models silently; where a proposed model could not be verified it is marked and left in place.

---

# A. Executive Technical Assessment

## A.1 The finding that reorders Stage 1

`FACT` Your development machine is an **Apple M2 MacBook Air, macOS 27.0, arm64**, Python 3.12 via Anaconda, with **no virtualization software installed** (checked: no Parallels, VMware, UTM, Docker).

`FACT` `onnxruntime-qnn` 2.6.0 publishes wheels for `win_arm64`, `win_amd64`, and Linux aarch64/x86_64 — **there is no macOS wheel** (checked directly against the PyPI JSON API).

`FACT` Qualcomm's own Whisper Windows sample states that native ARM64 Python is required and that **"running x64 Python under emulation breaks NPU access via ONNX Runtime QNN."** ([whisper_windows_py README](https://raw.githubusercontent.com/qualcomm/ai-hub-apps/main/apps/whisper_windows_py/README.md))

`ANALYSIS` Therefore, with certainty: **you cannot execute a single inference on a Hexagon NPU on your own hardware, at any point in the next eight days.** Not in a VM (Apple Silicon has no Hexagon NPU to pass through), not under emulation, not with any toolchain. This is not a risk to mitigate; it is a fixed boundary condition.

Two things follow, and they should drive every subsequent decision:

1. **100% of your NPU evidence must come from AI Hub Workbench cloud devices.** `FACT` `qai-hub` 0.55.0 is a pure-Python wheel (`py3-none-any`) classified for macOS, requiring Python ≥3.10 — so it runs on your M2 today. `FACT` AI Hub provides "thousands of real devices hosted through multiple device farms" and you can "programmatically download the optimized model." This path is open and free.
2. **The concept you choose should have a platform-neutral core.** Anything whose essential mechanism is a Windows-only OS hook (WASAPI loopback, Win32 screen capture, clipboard chaining) is something you will write blind and never run.

`ANALYSIS` This substantially weakens the Stage-1 assumption that all three concepts were equally buildable, and it changes the ranking. It also means the honest submission posture is fixed: *"architected for Windows on Snapdragon; models measured on real Snapdragon X Elite / X2 Elite silicon via AI Hub Workbench; application logic developed and validated cross-platform on CPU."* That is defensible and matches the rule's "designed, developed, **or intended to be** optimised" language. Any stronger claim would be false.

## A.2 Correction to Stage 1

Stage 1 recorded that "only AMD64 Python is supported on Windows for Snapdragon X users." That was an over-generalisation of a real but narrower constraint. The verified position is:

| Stage | Required Python | Source |
|---|---|---|
| Model **export / quantisation** (`qai_hub_models`, ORT quantisation utils) | x86-64 recommended; ARM64 problematic | `FACT` [ai-hub-models#258](https://github.com/qualcomm/ai-hub-models/issues/258) |
| **Runtime NPU inference** on device (ORT QNN EP) | **Native ARM64 required**; x64-under-emulation breaks NPU access | `FACT` whisper_windows_py README |

`ANALYSIS` These are not in conflict — they apply to different machines at different stages. It matters because it means the deployment target must ship ARM64-native Python (or C++), which the official sample handles with an `install_runtime.ps1` that installs ARM64 Python for you.

## A.3 Second-order finding: pipeline coverage on AI Hub is the real discriminator

`ANALYSIS` Because all your evidence comes from Workbench, the decisive question is not "is the idea good" but **"what fraction of my pipeline is already a first-party AI Hub model with published Snapdragon benchmarks, versus a bring-your-own model I must convert myself under QNN's static-shape and operator constraints?"**

| Concept | Pipeline stages on AI Hub with published Snapdragon numbers | Stages requiring BYO conversion | Coverage |
|---|---|---|---|
| **S1** | Whisper-Base (ASR) ✓, Qwen3-1.7B (classifier) ✓, EasyOCR (screen text) ✓ | none essential | **High** |
| **S2** | EasyOCR detector+recognizer ✓ (Latin), layout seg ✓ | **Indic recognizer, Indic TTS** | **Medium-Low** |
| **S3** | Qwen3-1.7B ✓, EasyOCR ✓ | **GLiNER-PII (the differentiating model)** | **Medium** |

`ANALYSIS` This inverts my Stage-1 read. I previously said S3 had the lowest execution risk. Under the constraint that you cannot test on device, S3's *differentiating* component — the NER model — is precisely the one not on AI Hub, and it carries QNN's two hardest constraints (dynamic sequence length, transformer op coverage). Meanwhile S1's entire critical path is first-party Qualcomm models with Qualcomm-published Snapdragon X Elite / X2 Elite latency numbers **that already exist before you run a single job**.

## A.4 Third finding: S1 is not a sub-100 ms system, and Stage 1 implied it was

`ANALYSIS` Working the real numbers (§4) gives a detection latency of roughly **2–8 seconds**, not 110 ms. For a scam call lasting minutes this is entirely adequate — but the Stage-1 framing of "a perception loop with a sub-100 ms budget" was wrong and must not appear in the submission. The correct claim is about **duty cycle and energy**, not per-event latency.

## A.5 Bottom line

| | Verdict |
|---|---|
| **S1 Perception Firewall** | **Strongest candidate.** Highest AI Hub coverage, published Snapdragon numbers for every critical model, an official Qualcomm sample that already does live-mic streaming ASR on NPU, best demo. Main risks are honesty/positioning and the absence of a labelled evaluation set. |
| **S3 Airlock** | **Viable, with a forced trade-off.** Either keep GLiNER-PII and accept an unverified QNN conversion, or replace it with Qwen3-1.7B and accept a weaker NPU story plus unmeasured recall. Cleanest platform portability. |
| **S2 Paath** | **Weakest under these constraints.** Two BYO stages, both Indic-specific, both unverified on QNN; Indic TTS is the single least-supported component in the whole study. Overlap with EchoSight is real but narrower than assumed. |

---

# B. PART 1 — Concrete end-to-end architectures

## B.1 S1 — Perception Firewall

```
[A] Audio source
    ├─ Live microphone  (cross-platform: sounddevice/PortAudio)
    └─ System loopback  (Windows-only: WASAPI loopback)      ← optional, Windows-only
         │
         ▼
[B] Ring buffer, 30 s window, 16 kHz mono, hop = 5 s
         │  (log-Mel 80×3000 feature extraction — CPU, numpy/torch)
         ▼
[C] Whisper-Base encoder      → 80×3000 fixed input        [NPU]
         ▼
[D] Whisper-Base decoder      → ≤200 tokens, autoregressive [NPU]
         ▼
[E] Rolling transcript buffer (last ~90 s), CPU
         │
         ├────────────────────────────────┐
         ▼                                 ▼
[F] Lexical/rule prefilter          [G] Qwen3-1.7B structured classifier   [NPU]
    (keyword + regex over                 prompt: transcript window
     8 manipulation primitives)           output: JSON, 8 booleans + spans
    CPU, <1 ms                            ~40 output tokens
         │                                 │
         └──────────────┬──────────────────┘
                        ▼
[H] Screen-state channel (optional, sampled every 3–5 s)
    screenshot → EasyOCR detector+recognizer [NPU] → keyword match
    + process-list check (remote-desktop tools) — CPU, OS-specific
                        ▼
[I] Evidence fusion — weighted rule engine over
    {authority, legal-threat, urgency, isolation, secrecy,
     remote-access, payment-redirect, verification-refusal}
    + screen evidence. Deterministic, auditable. CPU.
                        ▼
[J] Risk state machine (hysteresis; N-of-M over consecutive windows
    to suppress single-window false positives)
                        ▼
[K] UI — evidence panel listing each matched primitive with
    timestamp + verbatim quote; escalating banner; no auto-actions
                        ▼
[L] User action — user decides. System never blocks, never calls anyone,
    never contacts a bank. Advisory only.
```

`ANALYSIS` The rule prefilter at [F] is not redundancy theatre — it exists so that the demo degrades gracefully if the LLM stage is slow or unavailable, and so that every alert has a deterministic, quotable explanation rather than an LLM assertion.

## B.2 S2 — Paath

```
[A] Input: scanned PDF page / image (file drop)
         ▼
[B] Pre-processing — deskew, denoise, contrast normalise (OpenCV, CPU)
    optional: QuickSRNet / Real-ESRGAN upscale for low-DPI scans   [NPU]
         ▼
[C] Layout segmentation — regions: text-block / heading / table / figure
    candidate: DDRNet or Mask2Former (AI Hub)                      [NPU]
    ⚠ these are semantic-segmentation models, NOT document-layout models — see §C.2
         ▼
[D] Text detection — EasyOCR detector (CRAFT), 608×800 input        [NPU]
         ▼
[E] Text recognition — EasyOCR recognizer
    Latin: AI Hub build ✓ [NPU]
    Devanagari/Bengali/Tamil: separate ~210 MB models, BYO          [UNVERIFIED on NPU]
         ▼
[F] Reading-order reconstruction — geometric column/flow heuristics, CPU
         ▼
[G] Figure & table understanding — Qwen3-VL-4B via GenieX           [NPU]
         ▼
[H] Structured document emit — headings, blocks, alt-text, tables (JSON/EPUB)
         ▼
[I] TTS — Indic voice                                    [UNVERIFIED — see §C.2]
         ▼
[J] UI — navigable reader: jump by heading, skip table, replay figure description
```

## B.3 S3 — Airlock

```
[A] Ingress (three surfaces)
    ├─ HTTP proxy exposing an OpenAI-compatible /v1/chat/completions  ← platform-neutral
    ├─ Clipboard watcher                                              ← semi-portable
    └─ File/screenshot drop                                           ← portable
         ▼
[B] Deterministic floor — regex + checksum validators, CPU, <1 ms
    Aadhaar (Verhoeff), PAN, IFSC, phone, email, IP, credit card (Luhn),
    AWS/GitHub/Slack token patterns, private-key headers
         ▼
[C] Contextual detector — GLiNER-PII-edge, 60+ entity types          [UNVERIFIED on NPU]
    ALTERNATIVE: Qwen3-1.7B prompted extraction                       [NPU ✓ but generative]
         ▼
[D] Image path (if screenshot/document)
    EasyOCR detector+recognizer [NPU] → boxes+text → [B]+[C] over OCR text
    → SAM3 or plain rectangle masking → redacted image
         ▼
[E] Confidence gate  ── FAIL-CLOSED DECISION POINT ──
    high confidence sensitive → substitute
    low confidence / ambiguous → BLOCK and ask the user
    clean → pass
         ▼
[F] Surrogate generator — type-consistent, format-preserving,
    deterministic per-session (seeded), collision-checked
    "Priya Sharma" → "Anita Rao"; PAN → a syntactically valid fake PAN
         ▼
[G] Bidirectional mapping table — in-memory only, session-scoped, never persisted
         ▼
[H] Sanitised payload → cloud LLM  (or, in offline demo mode, to a local model)
         ▼
[I] Response → reverse substitution via [G] → user sees real values
         ▼
[J] Ledger UI — "this session: 14 spans substituted, 2 blocked, 0 leaked"
```

---

# C. PART 2 — Model availability audit

`ANALYSIS` Every row below was checked against a primary source (Qualcomm AI Hub model card on Hugging Face, the AI Hub site, PyPI JSON API, or the project's own repository). Where the Qualcomm card publishes a device benchmark I have quoted the device it was measured on.

| Model | Purpose | Size / params | Runtime | QNN/NPU | License | Evidence | Risk |
|---|---|---|---|---|---|---|---|
| **Whisper-Base** (encoder) | S1 ASR | 23.7 M / 90.7 MB float | ONNX, `PRECOMPILED_QNN_ONNX`, `QNN_CONTEXT_BINARY`, `VOICE_AI` | **NPU ✓** | Apache-2.0 | `FACT` [HF card](https://huggingface.co/qualcomm/Whisper-Base/blob/main/README.md): **X2 Elite 22.9 ms**; all devices report NPU as primary compute unit | **GREEN** |
| **Whisper-Base** (decoder) | S1 ASR | 48.9 M / 187 MB float | same | **NPU ✓** | Apache-2.0 | `FACT` same card: **Snapdragon X Elite 3.6–3.9 ms**, peak memory 20–126 MB | **GREEN** |
| **Whisper-Small** | S1 ASR (higher accuracy option) | enc 102 M / 391 MB; dec 139 M / 533 MB | ONNX/QNN | NPU (IoT chipsets listed) | Apache-2.0 | `FACT` [AI Hub card](https://aihub.qualcomm.com/iot/models/whisper_small) — **no compute-tier benchmark published** | **YELLOW** — larger, no X Elite number published |
| **Qwen3-1.7B** | S1 classifier / S3 contextual detector | 1.7 B, w4a16 or q4_0 | `GENIE`, `GENIEX_QAIRT`, `GENIEX_LLAMACPP` | **NPU ✓** | Apache-2.0 | `FACT` [HF card](https://huggingface.co/qualcomm/Qwen3-1.7B): X Elite + X2 Elite supported; **TTFT 0.05–1.7 s**, **22–68 tok/s**, context 512–4096 | **GREEN** (latency GREEN only at short context) |
| **EasyOCR detector** (CRAFT) | S1 screen text / S2 / S3 images | 20.8 M / 79.2 MB, input 608×800 | ONNX | **NPU ✓** | Apache-2.0 (orig. EasyOCR licence) | `FACT` [HF card](https://huggingface.co/qualcomm/EasyOCR/blob/main/README.md): **X2 Elite 20.0 ms / 9 MB**, **X Elite 38.1 ms / 36 MB**, float precision, NPU | **GREEN** |
| **EasyOCR recognizer** (Latin) | same | 3.84 M / 14.7 MB | ONNX | **NPU ✓** | Apache-2.0 | `FACT` same card: **X2 Elite 12.9 ms / 1 MB**, **X Elite 20.1 ms / 11 MB**, NPU | **GREEN** |
| **EasyOCR Devanagari / Bengali / Tamil recognizers** | S2 core | ~210 MB each (`devanagari_g2`, `bengali_g2`, `tamil_g1`) | PyTorch → ONNX (BYO) | **UNVERIFIED** | EasyOCR licence | `FACT` separate per-script models exist upstream; **not present in the AI Hub EasyOCR build**, which ships detector + one recognizer | **RED for S2** |
| **Qwen3-VL-4B-Instruct** | S2 figure description / S3 image reasoning | 4 B | GenieX | NPU (compute tier listed) | check card | `FACT` listed in AI Hub compute catalogue | **YELLOW** — no published X Elite latency retrieved |
| **GLiNER-PII-edge v1.0** | S3 core detector | ONNX **FP16 330 MB / UINT8 197 MB** | ONNX (CPU-proven) | **UNVERIFIED** | Apache-2.0 | `FACT` [HF card](https://huggingface.co/knowledgator/gliner-pii-edge-v1.0): 60+ PII types, **P 78.96 / R 72.34 / F1 75.50** on synthetic-multi-pii-ner-v1; English (multilingual tag) | **RED→YELLOW for S3** |
| **GLiNER2-PII** | S3 alternative | — | ONNX-quantised, CPU | **UNVERIFIED** | — | `FACT` [arXiv:2605.09973](https://arxiv.org/pdf/2605.09973) — multilingual, near-zero-shot, "ONNX-quantized variants that run on CPU" | **YELLOW** — CPU is the stated target |
| **SAM3** | S3 visual redaction masks | — | ONNX | NPU (official Windows sample exists) | — | `FACT` `sam3_segmentation_windows_py` in ai-hub-apps | **YELLOW** — likely overkill; rectangles suffice |
| **Indic TTS** — Indic Parler-TTS | S2 output | large autoregressive | PyTorch | **no ONNX/QNN found** | check card | `FACT` [AI4Bharat](https://huggingface.co/ai4bharat/indic-parler-tts-pretrained): 21 languages incl. Hindi | **RED** — autoregressive, heavy, no edge path found |
| **Indic TTS** — AI4Bharat Indic-TTS (FastPitch+HiFiGAN) | S2 output | — | PyTorch → ONNX (BYO) | **UNVERIFIED** | check repo | `FACT` [AI4Bharat/Indic-TTS](https://github.com/AI4Bharat/Indic-TTS), 13 languages | **YELLOW** |
| **Piper TTS (Hindi)** | S2 output | — | ONNX | CPU | MIT | `FACT` "The Piper community has not produced viable voices for Hindi as of earlier 2026"; Hindi arrived July 2026 via a different engine (Supertonic HD) | **RED — do not assume a Piper Hindi voice exists** |
| **MeloTTS** | S2 output | small | ONNX (sherpa-onnx) | CPU | MIT | listed in AI Hub TTS category | **YELLOW — Hindi support UNVERIFIED** |
| **vani-tts** | S2 output | target <200 MB INT8 | ONNX | CPU | check repo | `FACT` [GitHub](https://github.com/vivek-541/vani-tts) — Hindi, ONNX export, "target" wording implies WIP | **YELLOW/UNVERIFIED** |
| **IndicConformer** (AI4Bharat) | S1/S4 Indic ASR | 30 M | ONNX INT8 (8 languages, community conversion) | **UNVERIFIED** | check card | `FACT` [AI4Bharat](https://ai4bharat.iitm.ac.in/areas/asr); `FACT` [community ONNX](https://huggingface.co/meetsync/indic-conformer-onnx-sherpa) | **YELLOW** |
| **DDRNet / Mask2Former** | S2 layout | — | ONNX | NPU ✓ (AI Hub) | — | `FACT` in AI Hub catalogue | **RED for the stated purpose** — these are *scene* semantic-segmentation models; using them for document layout is a misuse, see §C.2 |

## C.1 Tooling availability — verified directly against PyPI

| Package | Version | Python | Platforms | Note |
|---|---|---|---|---|
| `qai-hub` | 0.55.0 | ≥3.10 | **macOS ✓**, Windows, Linux (`py3-none-any`) | `FACT` Runs on your M2 today |
| `qai-hub-models` | 0.62.2 | ≥3.10,<3.14 | `py3-none-any` | `FACT` Runs on your M2 |
| `qai-hub-apps` | — | — | — | `FACT` referenced by official sample: `pip install qai-hub-apps` |
| `onnxruntime-qnn` | 2.6.0 | ≥3.11 | `win_arm64`, `win_amd64`, linux aarch64/x86_64 — **no macOS wheel** | `FACT` The hard boundary in §A.1 |
| `geniex` | 0.7.0 | unspecified | sdist only | `FACT` on PyPI; Windows installer also published via GitHub releases |
| `gliner` | 0.2.29 | ≥3.10 | wheel + sdist | `FACT` available |

## C.2 Two model claims from Stage 1 that do not survive audit

`ANALYSIS` **(a) "DDRNet / Mask2Former for document layout."** These are semantic-segmentation models trained on scene-parsing datasets (Cityscapes/ADE20K class). Applying them to document layout analysis would require retraining on a document corpus — which is explicitly out of scope in 8 days. There is **no document-layout model on AI Hub that I could verify.** S2 must therefore either (i) do reading order geometrically from EasyOCR boxes alone, which is weaker but honest, or (ii) use Qwen3-VL to infer layout, which is slow and non-deterministic. This is a real downgrade to S2's architecture and I am flagging it rather than quietly substituting.

`ANALYSIS` **(b) "MeloTTS/PiperTTS for Indic output."** Verified that Piper had no viable Hindi voice as of early 2026. MeloTTS's documented language set does not evidence Hindi. S2's final stage — the one the user actually experiences — rests on a component I could not verify. That is the single most serious unverified dependency across all three concepts, because it is not a back-end optimisation the judge never sees; it *is* the product.

---

# D. PART 3 — NPU execution path, per model

## D.1 The two legitimate paths

```
PATH 1 — classical models
  Application (ARM64 Python or C++)
    └─ ONNX Runtime  (onnxruntime-qnn, win_arm64, Python ≥3.11 native ARM64)
         └─ QNN Execution Provider, backend = HTP
              └─ Qualcomm AI Runtime (QAIRT)
                   └─ Hexagon NPU

PATH 2 — generative models
  Application
    └─ GenieX  (Windows ARM64 installer / pip install geniex)
         ├─ backend geniex_qairt   → QAIRT → Hexagon NPU   (pre-compiled AI Hub bundles ONLY)
         └─ backend geniex_llamacpp → GGUF; Q4_0 recommended for best Hexagon support
```

`FACT` GenieX explicitly lists **Windows ARM64 (Snapdragon X/X Elite) — CLI, Python, local server**, is in Developer Preview, BSD-3-Clause, 8.4k stars / 2,324 commits, and recommends **"Q4_0 precision… it has the best Hexagon NPU support"** for the llama.cpp backend. NPU via `qairt` accepts **pre-compiled Qualcomm AI Hub bundles only**. ([qualcomm/GenieX](https://github.com/qualcomm/GenieX))

## D.2 Per-model placement

| Model | Path | Placement | Confidence | Basis |
|---|---|---|---|---|
| Whisper-Base encoder | 1 | **NPU** | High | `FACT` Qualcomm card reports NPU as primary compute unit on X Elite / X2 Elite |
| Whisper-Base decoder | 1 | **NPU** | High | same |
| Log-Mel feature extraction | — | **CPU** | Certain | `ANALYSIS` numpy/torch pre-processing, not part of the exported graph |
| Whisper tokenizer / BPE decode | — | **CPU** | Certain | `ANALYSIS` HF `transformers` tokenizer is pure Python |
| Qwen3-1.7B | 2 | **NPU** (`geniex_qairt`, w4a16) | High | `FACT` card lists GENIEX_QAIRT + X Elite/X2 Elite |
| Qwen3-1.7B tokenizer + sampling | — | **CPU** | Certain | `ANALYSIS` |
| EasyOCR detector | 1 | **NPU** | High | `FACT` card reports NPU, float precision |
| EasyOCR recognizer (Latin) | 1 | **NPU** | High | `FACT` same |
| EasyOCR Indic recognizer | 1 | **UNKNOWN** | — | Not on AI Hub; conversion unattempted |
| GLiNER-PII-edge | 1 | **UNKNOWN** | — | See §D.4 |
| Qwen3-VL-4B | 2 | **NPU** presumed; vision encoder placement **UNKNOWN** | Low | `ANALYSIS` VLM preprocessing/projection layers often fall back |
| Indic TTS (any) | 1 | **UNKNOWN** | — | No verified ONNX→QNN path |
| Rule engine / fusion / regex | — | **CPU** | Certain | by design |
| Screen capture, audio capture, UI | — | **CPU** | Certain | OS APIs |

## D.3 How to *prove* NPU execution rather than claim it

`ANALYSIS` Two independent, citable proofs are available, and using both is what separates this submission from the field:

1. `FACT` **ORT session-level proof.** The QNN EP supports `"session.disable_cpu_ep_fallback": "1"`. With that set, session creation **fails** if any node cannot be placed on the NPU. A successful session under that flag is a binary, screenshot-able proof that the whole graph is on the Hexagon NPU — not an assertion. ([ORT QNN EP docs](https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html))
2. `FACT` **Workbench Runtime Layer Analysis.** Profile jobs expose a per-layer **placement column** (NPU/GPU/CPU), and for ONNX Runtime targets, optrace and QHAS summary data under the NPU placement. Compute units can also be constrained per job. This is the artefact to screenshot for the submission.

`ANALYSIS` Proof #1 requires a Snapdragon device, which you do not have. **Proof #2 does not** — it runs in Qualcomm's cloud. So your evidence package uses #2, and you describe #1 as the on-device verification step in the deployment plan. Stating that distinction explicitly is itself a credibility signal.

## D.4 Constraint checklist — the things that actually break conversions

| Constraint | Verified statement | Which concept it threatens |
|---|---|---|
| **Static shapes mandatory** | `FACT` "QNN EP does not support models with dynamic shapes… Dynamic shapes must be fixed to a specific value." | **S3 critical** — NER over variable-length text. Mitigation: fix `max_seq_len` (e.g. 512) and chunk/pad. Padding waste is real but acceptable. |
| **HTP requires quantisation (per ORT docs)** vs **FP16 accepted (per Qualcomm apps README)** | `FACT` ORT: "The QNN HTP backend only supports quantized models… uint8/uint16." `FACT` Qualcomm ai-hub-apps: NPU acceleration accepts **FP16 on Hexagon v69+**, or INT8/INT16. | **Contradiction — flag, do not resolve by assumption.** `ANALYSIS` Most likely both true for different compile paths (AI Hub QNN context binaries vs raw ORT QDQ). The EasyOCR card showing **float precision running on NPU** supports the FP16 route. Verify empirically in Experiment 2. |
| **~70-operator whitelist** | `FACT` QNN EP maintains a whitelist; unsupported ops (Loop, If) can error or fall back | **S3** — GLiNER's span-scoring head and DeBERTa-style attention are the risk. **S2** — Qwen3-VL preprocessing. |
| **Quantisation tooling is x86_64-only** | `FACT` ORT quantisation utils unavailable on ARM64 | `ANALYSIS` Irrelevant to you — AI Hub does quantisation server-side. |
| **Model size >2 GB may fail** | `FACT` AI Hub FAQ: models "large (i.e. > 2GB)" may fail | Affects Whisper-Small (924 MB total — safe) and Qwen3-VL-4B (**check**) |
| **LLMs may fail out of the box** | `FACT` AI Hub FAQ: "LLMs/GenAI models may fail out of the box," quantisation recommended | Use the **pre-exported** Qwen3-1.7B bundle rather than exporting your own |
| **Whisper fixed 30 s input** | `FACT` "Input resolution: 80x3000 (30 seconds audio)", max 200 decoded tokens | **S1** — dictates a chunked, not truly streaming, design. See §E. |
| **Model load / context-binary overhead** | `FACT` `ep.context_enable=1` serialises compiled graphs and "significantly reduces model loading time"; Workbench reports `first_load_time` vs `warm_load_time` separately | All — affects startup UX, must be reported separately from steady-state |
| **Tokenizer CPU overhead** | `ANALYSIS` UNKNOWN magnitude; measurable on Mac as a proxy | S1, S3 |

---

# E. PART 4 — Real-time budget

## E.1 What Workbench can and cannot give you

`FACT` A profile job returns `compile_time`, `first_load_time`, `warm_load_time`, `estimated_inference_time` (microseconds), and peak/increase **memory ranges** — and it reports **"the minimum observed time, which results in a more repeatable metric."** The documentation does **not** report median, P50, P95 or max.

`ANALYSIS` Therefore, stated plainly:

- **P50 / P95 on Snapdragon: UNOBTAINABLE** without owning the device. Do not put percentile numbers for Snapdragon in the submission. Report Workbench's minimum inference time and label it exactly that.
- **P50 / P95 for the full pipeline** can be measured on your Mac with ONNX Runtime CPU EP and reported as a *relative* distribution study, clearly labelled as macOS/CPU, used to characterise variance and orchestration overhead — not as a Snapdragon claim.
- This limitation is itself worth writing down in the submission. `ANALYSIS` A judge who sees "we report minimum inference time because that is what Workbench measures; percentile latency was measured on x86/ARM CPU only and is not a Snapdragon claim" will trust every other number on the page.

## E.2 S1 budget — built only from published numbers

All Snapdragon figures below are `FACT` from Qualcomm's own model cards; everything derived is marked.

| Stage | Component | Time | Source |
|---|---|---|---|
| Audio capture | ring buffer fill | hop = **5 000 ms** (design choice) | `ANALYSIS` |
| Feature extraction | log-Mel 80×3000, CPU | **UNKNOWN** — measurable on Mac | — |
| ASR encode | Whisper-Base encoder, X2 Elite | **22.9 ms** | `FACT` HF card |
| ASR decode | Whisper-Base decoder, X Elite | **3.6–3.9 ms per token** | `FACT` HF card |
| ASR decode total | ~100 tokens for 30 s of speech | **≈ 360–390 ms** | `ANALYSIS` derived; token count is an estimate |
| Tokenizer/BPE | CPU | **UNKNOWN** | — |
| Rule prefilter | regex over 8 primitives | **<1 ms** | `ANALYSIS` |
| LLM classify — TTFT | Qwen3-1.7B, short context | **50 ms … 1 700 ms** | `FACT` HF card (range covers 512–4096 ctx) |
| LLM classify — generate | ~40 JSON tokens @ 22–68 tok/s | **≈ 590 – 1 820 ms** | `ANALYSIS` derived |
| Screen OCR (optional) | EasyOCR det + rec, X2 Elite, ~15 lines | **20.0 + (12.9 × 15) ≈ 214 ms** | `ANALYSIS` derived from `FACT` per-call numbers |
| Fusion + state machine | CPU | **<1 ms** | `ANALYSIS` |

**Derived totals (compute only, excluding the 5 s hop):**

| | Optimistic | Pessimistic |
|---|---|---|
| ASR (encode + decode) | ~385 ms | ~415 ms |
| LLM classification | ~640 ms | ~3 520 ms |
| Screen OCR | 0 (skipped this cycle) | ~214 ms |
| **Compute subtotal** | **≈ 1.0 s** | **≈ 4.1 s** |
| **+ hop latency (0–5 s)** | **≈ 1.0 s** | **≈ 9.1 s** |

`ANALYSIS` **Conclusion: end-to-end detection latency is ~1–9 s, typical ~3–5 s.** For a scam call this is fine — the manipulation unfolds over minutes. But it destroys the "sub-100 ms perception loop" framing. The defensible Snapdragon claim is therefore:

> Per 5-second cycle the pipeline consumes roughly 1–4 s of NPU time, i.e. a **20–80% duty cycle of the NPU** but a near-zero share of CPU and battery relative to running the same models on CPU. The claim is *sustainability*, not *speed*.

`ANALYSIS` **Design correction this forces:** the LLM stage is the bottleneck (up to 3.5 s of a 5 s budget). Two mitigations, both worth stating: (i) run the LLM only when the cheap rule prefilter fires, cutting LLM invocations by an order of magnitude; (ii) cap context at 512 tokens to stay at the fast end of the published TTFT range. **This is exactly the "ingest a lot, emit a little" architecture Stage 1 argued for**, and it is forced by the numbers rather than asserted.

## E.3 S3 budget

| Stage | Time | Source |
|---|---|---|
| Regex/checksum floor | **<1 ms** | `ANALYSIS` |
| GLiNER-PII-edge, 512 tokens, on Snapdragon NPU | **UNKNOWN** | not on AI Hub; Experiment 3 would establish it |
| GLiNER-PII-edge on CPU (Mac, proxy measure) | **UNKNOWN** — measurable today | — |
| Qwen3-1.7B alternative: TTFT + ~60 tokens | **≈ 0.9 – 4.4 s** | `ANALYSIS` derived from `FACT` card |
| Screenshot path: EasyOCR det + rec × ~30 lines, X2 Elite | **≈ 20.0 + 387 = 407 ms** | `ANALYSIS` derived from `FACT` |
| Surrogate generation + mapping | **<1 ms** | `ANALYSIS` |

`ANALYSIS` The UX constraint is different from S1: a user pasting into a chat box will tolerate ~200–400 ms, not 3 s. So the Qwen3-1.7B fallback is **architecturally wrong for the paste path** and only acceptable as a second-pass check on blocked items. This makes GLiNER's latency the load-bearing unknown for S3 — and it is the one number you cannot get without a conversion experiment. That is S3's core risk, precisely located.

## E.4 Metrics to define and where each can be obtained

| Metric | S1 | S2 | S3 | Where obtainable |
|---|---|---|---|---|
| P50 latency (Snapdragon) | UNKNOWN | UNKNOWN | UNKNOWN | **Not obtainable — needs device** |
| P95 latency (Snapdragon) | UNKNOWN | UNKNOWN | UNKNOWN | **Not obtainable — needs device** |
| Minimum inference time (Snapdragon, per model) | available | available | partly | **Workbench** ✓ |
| Peak memory range (per model) | available | available | partly | **Workbench** ✓ |
| Layer placement NPU/GPU/CPU | available | available | partly | **Workbench Runtime Layer Analysis** ✓ |
| Cold-start / `first_load_time` | available | available | partly | **Workbench** ✓ |
| Warm load `warm_load_time` | available | available | partly | **Workbench** ✓ |
| Throughput (RTF for ASR) | derivable | n/a | n/a | derived from Workbench + audio length |
| Full-pipeline P50/P95 | measurable on CPU only | same | same | **your Mac**, labelled as CPU |
| Energy per query | UNKNOWN | UNKNOWN | UNKNOWN | **Not obtainable** — cite arXiv:2606.11257 as comparable published evidence, never as your own measurement |
| Accuracy | needs a labelled set | needs a labelled set | RedactionBench / GLiNER card | see §H |

---

# F. PART 5 — Snapdragon Workbench benchmark plans

## F.1 Protocol common to all concepts

```
Targets (submit each job against both):
  device = "Snapdragon X Elite CRD"          # FACT: named in official docs
  device = <Snapdragon X2 Elite compute device as listed in hub.get_devices()>
                                             # exact name UNVERIFIED — enumerate first

Runtimes:  target_runtime = onnx  |  precompiled_qnn_onnx  |  qnn_context_binary
Compute-unit variants per model:  [npu]  /  [gpu]  /  [cpu]
           (AI Hub default is NPU with fallback to GPU/CPU; force explicitly to
            produce a clean three-way comparison rather than relying on the default)

Iterations / warm-up: controlled by Workbench, not by you. It runs inference
           "several times in a tight loop" and reports the MINIMUM.
           => Do not claim you chose an iteration count. Report what it reports.

Recorded per job: compile_time, first_load_time, warm_load_time,
                  estimated_inference_time, peak/increase memory ranges,
                  per-layer placement (NPU/GPU/CPU) from Runtime Layer Analysis,
                  job URL (public, citable)
```

`ANALYSIS` The job URL matters: AI Hub profile jobs have public URLs (e.g. `aihub.qualcomm.com/jobs/<id>`). **Putting the job IDs in your README makes every number independently verifiable by a judge.** Very few submissions will be falsifiable in that way, and falsifiability is the strongest possible credibility signal.

## F.2 Benchmark set — S1

| ID | Model | Precision | Input | Runtime | Compute unit | Purpose |
|---|---|---|---|---|---|---|
| A1 | Whisper-Base encoder | float / w8a8 | 80×3000 | onnx | **cpu** | CPU baseline |
| A2 | Whisper-Base encoder | float | 80×3000 | precompiled_qnn_onnx | **npu** | headline NPU number |
| A3 | Whisper-Base encoder | float | 80×3000 | onnx | **gpu** | test the "iGPU is worst" hypothesis |
| A4 | Whisper-Base decoder | float | 1 token step | precompiled_qnn_onnx | npu | per-token decode |
| A5 | Whisper-Small encoder | float | 80×3000 | precompiled_qnn_onnx | npu | accuracy/latency trade point |
| A6 | Qwen3-1.7B (w4a16) | w4a16 | ctx 512 | geniex_qairt | npu | TTFT + tok/s at the context you will actually use |
| A7 | Qwen3-1.7B | w4a16 | ctx 4096 | geniex_qairt | npu | show the context→latency curve |
| A8 | EasyOCR detector | float | 608×800 | onnx | npu | screen-channel cost |
| A9 | EasyOCR recognizer | float | default | onnx | npu | per-line cost |

**What constitutes a meaningful Snapdragon advantage for S1:** A2 ≫ A1 on encoder latency (the prefill-class workload), and A3 ≤ A1 (confirming the Adreno is not the right target). `ANALYSIS` If A2/A1 is large and A3 is genuinely worse than A1, you have independently reproduced the arXiv:2606.11257 finding on different models — which is a far stronger claim than citing it.

## F.3 Benchmark set — S2

| ID | Model | Runtime | Compute | Purpose |
|---|---|---|---|---|
| B1 | EasyOCR detector | onnx | cpu / npu / gpu | baseline vs NPU |
| B2 | EasyOCR recognizer (Latin) | onnx | cpu / npu | baseline vs NPU |
| B3 | **EasyOCR Devanagari recognizer (BYO export)** | onnx | npu | **the gating experiment** |
| B4 | QuickSRNet / Real-ESRGAN | onnx | npu | pre-enhancement cost |
| B5 | Qwen3-VL-4B | geniex_qairt | npu | figure-description cost |
| B6 | **Indic TTS (BYO export)** | onnx | npu | **the second gating experiment** |
| B7 | Full-page batch: 300 pages × (B1+B2) | — | npu vs cpu | the "index a textbook on battery" claim |

`ANALYSIS` B3 and B6 are not benchmarks; they are **existence tests**. If either fails to convert, S2's differentiated claim (Indic, not generic OCR) collapses to "EasyOCR in English," which is EchoSight's document-reading feature.

## F.4 Benchmark set — S3

| ID | Model | Runtime | Compute | Purpose |
|---|---|---|---|---|
| C1 | **GLiNER-PII-edge UINT8, seq 512 fixed (BYO)** | onnx | **npu** | **the gating experiment** |
| C2 | GLiNER-PII-edge UINT8, seq 512 | onnx | cpu | baseline |
| C3 | GLiNER-PII-edge FP16, seq 512 | onnx | npu | tests the FP16-on-NPU contradiction in §D.4 |
| C4 | Qwen3-1.7B, ctx 512 | geniex_qairt | npu | fallback-path latency |
| C5 | EasyOCR det+rec | onnx | npu | screenshot path |
| C6 | Throughput sweep: 1 / 10 / 100 payloads | — | npu vs cpu | the "always-on, zero-tax" claim |

**Meaningful advantage for S3:** C1 must land in the low tens of milliseconds for the always-on premise to hold. `ANALYSIS` If C1 fails to convert *or* lands above ~200 ms, S3's core UX claim ("scans every paste with no perceptible tax") is unsupported and the concept needs rearchitecting.

## F.5 What must be measured in your application rather than Workbench

| Thing | Why Workbench can't | Where it goes |
|---|---|---|
| Feature extraction, tokenizer, BPE decode | not part of the exported graph | your Mac, CPU, labelled |
| Orchestration and IPC overhead | not a model | your Mac, labelled |
| P50/P95 distributions | Workbench reports minimum only | your Mac, labelled as CPU |
| End-to-end wall-clock detection latency | multi-model pipeline | your Mac, labelled; plus a *derived* Snapdragon estimate showing the arithmetic |
| Accuracy / false-positive rate | not a performance tool | §H evaluation plan |
| Battery / energy | no power rail access | **not measurable — cite published work, never claim your own** |

---

# G. PART 6 — Failure-mode analysis

Classification: 🟢 GREEN manageable · 🟡 YELLOW risky · 🔴 RED could kill the project.

## G.1 S1 Perception Firewall

| # | Failure mode | Class | Assessment |
|---|---|---|---|
| 1 | **No labelled scam-call dataset exists for you to evaluate against** | 🔴 RED | `ANALYSIS` You cannot report a credible accuracy number. Mitigation: build a small, transparent, hand-authored evaluation set from *publicly reported* scam transcripts + benign control calls (support calls, bank IVR, family conversation), publish it in the repo, and report results on it while explicitly stating n and that it is not a statistically meaningful benchmark. Honest smallness beats fake precision. |
| 2 | Qwen3-1.7B classification latency exceeds the 5 s cycle at long context | 🟡 YELLOW | Mitigated by design: rule prefilter gates LLM calls; cap context at 512. Published TTFT range makes this predictable. |
| 3 | Hinglish/Indian-accent ASR degradation | 🟡 YELLOW | `FACT` global models 14–16% WER on code-mixed telephony. Mitigation: demo in English or clear Hindi; report WER honestly if you measure it; do not claim Hinglish support you have not measured. |
| 4 | Whisper's 30 s fixed window makes "real-time" feel laggy | 🟢 GREEN | Sliding window with 5 s hop; the official sample already does mic streaming. |
| 5 | **False positives on legitimate bank/police/HR calls** | 🟡 YELLOW | Product-level, not technical. Mitigation: never output a verdict; output matched patterns with quotes. Require N-of-M windows. Frame as "patterns matched," never "this is a scam." |
| 6 | False negatives — a real scam not flagged | 🟡 YELLOW | Mitigation: explicit scope statement; the product is an advisory speed-bump, not protection. **Never make a financial or security guarantee.** |
| 7 | Windows-only system-audio loopback can't be built/tested on your Mac | 🟡 YELLOW | Mitigation: use **microphone capture** as the primary path (cross-platform via PortAudio) and demo with scam audio played aloud from a phone — which is also more realistic. Treat loopback as a documented Windows enhancement. |
| 8 | Screen channel (process list, remote-desktop detection) is OS-specific | 🟡 YELLOW | Make it an optional, clearly-scoped module; the audio channel alone carries the demo. |
| 9 | Ethics/optics: "always listening" reads badly | 🟡 YELLOW | Explicit per-session activation, visible indicator, airplane-mode demo, no persistence of audio. Address it on a slide before a judge asks. |
| 10 | Positioning collision with SnapShield (security analyst archetype) | 🟢 GREEN | `FACT` SnapShield is network-packet-level threat triage — a different layer entirely. Distinguish explicitly. |

## G.2 S2 Paath

| # | Failure mode | Class | Assessment |
|---|---|---|---|
| 1 | **Indic TTS has no verified ONNX/NPU path** | 🔴 RED | §C.2(b). This is the user-facing output stage. If it fails, the demo has no voice. |
| 2 | **EasyOCR Indic recognizers are not in the AI Hub build and conversion is unattempted** | 🔴 RED | §C. Without this, the product is English OCR. |
| 3 | **No document-layout model on AI Hub** | 🟡 YELLOW | §C.2(a). Fall back to geometric reading-order from OCR boxes — weaker but honest and demoable. |
| 4 | Indic OCR accuracy on real scans | 🟡 YELLOW | `FACT` EasyOCR multi-language carries a 20–30% accuracy penalty vs single-language pipelines, and "Indic ligatures and conjuncts cause wildly inaccurate confidence scores." |
| 5 | Equations and complex tables | 🟡 YELLOW | Scope them out explicitly. |
| 6 | Qwen3-VL-4B figure description may be slow / may exceed the 2 GB AI Hub limit | 🟡 YELLOW | Verify size before relying on it. |
| 7 | Overlap with EchoSight's document-reading feature | 🟡 YELLOW | Real but partial — see §K. |
| 8 | Overlap with Windows Narrator / built-in OCR | 🟡 YELLOW | Differentiate on reading order + Indic + figure description, not on "reads documents." |
| 9 | Demo requires a judge who can evaluate Hindi audio | 🟡 YELLOW | Mitigation: subtitle everything (the rules require English anyway). |
| 10 | Accessibility claims without a blind user testing it | 🟡 YELLOW | Do not claim validation you do not have. |

## G.3 S3 Airlock

| # | Failure mode | Class | Assessment |
|---|---|---|---|
| 1 | **GLiNER-PII fails QNN conversion (dynamic shapes / unsupported ops)** | 🔴 RED | §D.4. This is the differentiating model. |
| 2 | **Fail-closed is user-hostile in practice** | 🔴 RED | `ANALYSIS` See §J.3 — a genuinely fail-closed system blocks on every ambiguity, and with F1 ≈ 75.5% that is a lot of blocking. This is a design contradiction, not a bug. |
| 3 | Recall failure = product failure (one missed Aadhaar) | 🟡 YELLOW | `FACT` GLiNER-PII-edge recall 72.34% on its own card. You cannot honestly claim leak-proof. Mitigation: position as *defence in depth* with a deterministic checksum floor for the highest-stakes identifiers. |
| 4 | Latency tax on paste makes users disable it | 🟡 YELLOW | Gating experiment C1. |
| 5 | Surrogate substitution degrades cloud answer quality | 🟡 YELLOW | Measurable: same prompts with/without substitution, judged. Worth doing — it is a differentiator vs blunt masking. |
| 6 | Reverse substitution collides (surrogate appears naturally in the reply) | 🟡 YELLOW | Use rare, collision-checked surrogates; verify on restore. |
| 7 | TLS interception is fragile/invasive | 🟢 GREEN | Avoid entirely. Expose an explicit OpenAI-compatible endpoint the user points their client at. Platform-neutral and honest. |
| 8 | Demo requires live cloud API access — breaks the "offline" story | 🟡 YELLOW | `ANALYSIS` Genuine tension: S3's whole point is that data goes to the cloud. Mitigation: demo airplane-mode for the *detection* stage, then show the sanitised payload; optionally route to a local model to keep the whole demo offline. |
| 9 | Crowded prior art | 🟢 GREEN | Real but differentiable — §K. |
| 10 | Weakest "why a laptop NPU" story if detection is only on paste events | 🟡 YELLOW | `ANALYSIS` A paste happens a few times a minute — that is not a duty-cycle argument. The NPU case strengthens only if you also scan screenshots and documents in bulk. Design for that or the Snapdragon claim thins. |

---

# H. PART 7 — S1 deep audit

## H.1 Is the architecture realistic?

**Yes, with three corrections.**

`FACT` Qualcomm ships an official Windows Python sample, `whisper_windows_py`, described as running "OpenAI's Whisper speech-to-text on-device using ONNX Runtime QNN on Snapdragon X Elite," with `--stream-audio-device <n>` for live microphone streaming, `--list-audio-devices`, and `--audio-file`. Setup is `pip install qai-hub-apps` then `qai-hub-apps fetch whisper_windows_py --model whisper_base --chipset qualcomm-snapdragon-x-elite`.

`ANALYSIS` This is the single most de-risking fact in the entire study for any concept. The hardest engineering in S1 — live audio → NPU ASR on Windows ARM64 — is a solved, first-party, fetchable reference implementation. You are not building an ASR pipeline; you are building the **classifier, fusion and evidence layer on top of one**.

**Correction 1 — it is chunked, not streaming.** `FACT` fixed 80×3000 input = 30 s, max 200 decoded tokens. Design a 30 s sliding window with a 5 s hop. Say "chunked near-real-time," never "streaming."

**Correction 2 — latency is seconds, not milliseconds.** §E.2. Reframe the claim around duty cycle and energy.

**Correction 3 — screen state must be optional.** It is the least portable part and you cannot test it. Keep the audio channel self-sufficient.

## H.2 Can the eight signals be detected reliably?

`ANALYSIS` Honest answer: **the lexical signals, yes with decent precision; the pragmatic ones, unproven.**

| Signal | Detectability | Method |
|---|---|---|
| Authority impersonation | **High** — lexically explicit ("CBI", "Inspector", "TRAI", "Cyber Cell") | regex + LLM |
| Legal threat | **High** — "arrest", "FIR", "money laundering", "non-bailable" | regex + LLM |
| Urgency / time pressure | **Medium** — "within 30 minutes", "immediately" | LLM better than regex |
| Isolation instruction | **High and highly diagnostic** — "do not disconnect", "do not tell your family" | regex + LLM |
| Secrecy demand | **High** | regex + LLM |
| Remote-access request | **High** — named tools: AnyDesk, TeamViewer, QuickSupport | regex, plus process-list corroboration |
| Payment redirection | **Medium** — "transfer to this account for verification" | LLM |
| Verification refusal | **Low** — pragmatic, needs discourse understanding | **UNVERIFIED** — likely the weakest signal |

`ANALYSIS` The strongest design consequence: **the isolation instruction is the highest-value signal** because it is near-absent from legitimate institutional calls. No real bank tells you not to tell your family. Weighting it heavily improves precision more than any model change. That is a product insight the architecture should encode explicitly, and it is defensible in a pitch.

## H.3 Demo safety and honesty

- **Audio capture in a demo:** yes — play a scripted scam audio file through a phone speaker into the laptop mic. `ANALYSIS` More convincing than file input and avoids WASAPI entirely.
- **Provenance:** the demo audio must be **synthesised or acted from publicly reported scam patterns**, labelled on screen as a reconstruction. Never use a real victim's recording.
- **Privacy:** no recording persisted; airplane mode on camera; a visible "audio never leaves this device" indicator.
- **No guarantees:** the UI must say *"patterns matched"* and *"consider verifying independently — call 1930."* Never "this is a scam," never "you are protected." `ANALYSIS` This is both an ethical requirement and a scoring advantage: it demonstrates product judgement.
- **False positives:** N-of-M hysteresis; an always-visible "dismiss / this was legitimate" control; show the evidence, let the human decide.

## H.4 90-second demo

| Time | On screen |
|---|---|
| **0–10 s** | Laptop desktop. Presenter toggles **airplane mode**; Wi-Fi icon greys out. Corner badge: `Local · Hexagon NPU · 0 bytes sent`. |
| **10–30 s** | Phone plays: *"This is Inspector Sharma, CBI. Your Aadhaar is linked to a money-laundering case. Do not disconnect. Do not inform your family."* Evidence panel fills line by line — `Authority impersonation` ✓ `0:04` "Inspector Sharma, CBI" · `Legal threat` ✓ `0:09` · `Isolation instruction` ✓ `0:14` — each with a verbatim quote. Risk meter climbs. |
| **30–60 s** | Caller: *"Install AnyDesk so I can verify your account."* Second channel fires (`Remote-access request` + process detected). Meter → red. Calm full-screen card: *"5 of 8 digital-arrest patterns matched. Real police do not arrest over calls. Hang up and dial 1930."* |
| **60–90 s** | Benchmark panel with **live AI Hub job URLs**: Whisper-Base encoder on Snapdragon X2 Elite vs CPU; decoder ms/token; Qwen3-1.7B TTFT; the layer-placement screenshot showing NPU. Closing line: *"Network off the whole time. ~1–4 seconds of NPU work per 5-second window — which is why this can stay on for the entire call, on battery."* |

`ANALYSIS` Note what the closing line does **not** claim: no accuracy percentage, no money saved, no "prevents fraud." It claims exactly what the evidence supports.

---

# I. PART 8 — S2 deep audit

## I.1 Pipeline verdict

Two of nine stages are `RED` and one is `YELLOW-structural`:

| Stage | Status |
|---|---|
| Pre-processing (deskew/denoise/upscale) | 🟢 available, QuickSRNet/Real-ESRGAN on AI Hub |
| **Layout segmentation** | 🟡 **no document-layout model on AI Hub** — geometric fallback required |
| Text detection | 🟢 EasyOCR detector, NPU, X2 Elite 20.0 ms |
| **Text recognition (Indic)** | 🔴 **separate ~210 MB per-script models, not in AI Hub build, conversion unattempted** |
| Reading order | 🟢 heuristics, CPU |
| Figure/table understanding | 🟡 Qwen3-VL-4B, size and latency unverified |
| Structured emit | 🟢 |
| **Indic TTS** | 🔴 **no verified ONNX/NPU Indic voice** |
| UI | 🟢 |

## I.2 Script-by-script reality

| Script | EasyOCR model | AI Hub | Assessment |
|---|---|---|---|
| Latin/English | in AI Hub build | ✓ | works today, but this is the undifferentiated case |
| Devanagari (Hindi, Marathi) | `devanagari_g2` ~210 MB | ✗ | BYO conversion, **UNVERIFIED** |
| Bengali | `bengali_g2` ~210 MB | ✗ | BYO, **UNVERIFIED** |
| Tamil | `tamil_g1` ~210 MB | ✗ | BYO, **UNVERIFIED** |
| Punjabi (Gurmukhi) | **UNVERIFIED that EasyOCR covers it** | ✗ | do not assume |

`FACT` EasyOCR's multi-language mode carries a **20–30% accuracy penalty** versus single-language pipelines, and Indic ligatures/conjuncts produce unreliable confidence scores.

`ANALYSIS` Practical consequence: a demo on a *clean* Hindi scan is achievable; a demo on a *poor* scan — which is the actual problem statement — is where it will visibly fail, and that is the demo a judge will ask for.

## I.3 Can a convincing demo be produced without collecting or training a dataset?

**Partially.** Public scanned Hindi material exists (NCERT textbook PDFs, public-domain newspapers). You need no training data. But you also have **no ground truth**, so you cannot report CER/WER — only qualitative side-by-side against NVDA. `ANALYSIS` That is a weaker evidence package than S1's or S3's, and "Technical Implementation" is the top criterion.

## I.4 EchoSight overlap — evidence-based

`FACT` From the repository: EchoSight is an accessibility application for Snapdragon HP PCs combining real-time speech-to-text captioning, webcam scene description, and document/screen text extraction, running on the Hexagon NPU. It uses Whisper Base/Small, a lightweight VLM, an OCR model and a TTS model. The authors state: *"EchoSight does not reinvent model inference — it combines official Qualcomm AI Hub building blocks into a single accessibility pipeline."* Original work claimed: voice-command routing, overlay UI, pipeline orchestration, hotkey-triggered narration. Repository activity: **12 commits, 0 stars, 0 forks.**

| Dimension | EchoSight | S2 Paath | Overlap |
|---|---|---|---|
| Target user | general accessibility | specifically Indic-language blind/low-vision readers | **partial** |
| Document reading | yes — OCR + TTS | yes — but with layout, reading order, figure description | **substantial on the basic feature** |
| Indic language focus | **not evidenced** | core premise | **low** |
| Reading-order reconstruction | not evidenced | core differentiator | **low** |
| Live captioning, scene narration | yes | out of scope | none |
| Maturity | 12 commits, orchestration layer | — | — |

`ANALYSIS` **Verdict: overlap is real but narrower than Stage 1 assumed.** EchoSight is a broad accessibility copilot; S2 is a deep Indic document pipeline. They collide on "OCR a document and read it aloud." S2's differentiation is exactly the two stages that are 🔴 RED — Indic recognition and Indic TTS. **If those fail, S2 becomes EchoSight.** That is the crux: S2's differentiation and S2's technical risk are the same thing.

---

# J. PART 9 — S3 deep audit

## J.1 Detector coverage

| Category | Method | Confidence |
|---|---|---|
| Aadhaar | regex + **Verhoeff checksum** | 🟢 deterministic |
| PAN | regex `[A-Z]{5}[0-9]{4}[A-Z]` | 🟢 deterministic |
| Credit card | regex + **Luhn** | 🟢 deterministic |
| IFSC, phone, email, IP, URL | regex | 🟢 deterministic |
| AWS/GitHub/Slack tokens, private keys | regex (gitleaks-style ruleset) | 🟢 deterministic |
| Passwords in free text | contextual | 🟡 LLM/NER, no checksum possible |
| Person names, org names | GLiNER-PII | 🟡 `FACT` R 72.34% |
| Confidential project codenames | **no general method** | 🔴 requires user-supplied wordlist |
| Health conditions, financial context | GLiNER-PII (categories exist) | 🟡 |
| Source-code proprietary logic | **not a detectable entity class** | 🔴 out of scope — say so |

`ANALYSIS` The deterministic floor is genuinely strong and is where the India-specific value sits: Aadhaar's Verhoeff check and PAN's format give you **near-zero-false-positive detection of the two identifiers Indian users most need protected.** That is a concrete, defensible, India-relevant differentiator that does not depend on any ML model converting successfully — and therefore does not depend on the 🔴 risk. `ANALYSIS` **If you choose S3, build the submission's spine on the deterministic floor and treat the NER model as an enhancement, not the foundation.**

## J.2 Is the image path realistic?

Yes. `FACT` EasyOCR det+rec are on AI Hub with NPU placement and published X Elite/X2 numbers; ~30 lines ≈ 407 ms derived on X2 Elite. Masking can be plain rectangles over OCR boxes — SAM3 is unnecessary. `ANALYSIS` The screenshot-redaction demo is the most visually distinctive moment available to S3 and it rests entirely on 🟢 components.

## J.3 Can the system be genuinely fail-closed? — the critical question

`ANALYSIS` **Not in the strong form, and you should say so rather than claim it.**

A strictly fail-closed system blocks whenever it is uncertain. With a detector at `FACT` F1 ≈ 75.5% / recall 72.34%, "uncertain" covers a large fraction of ordinary text. A tool that interrupts one paste in four is abandoned within a day — and an abandoned tool protects nothing. This is a design contradiction, not an implementation bug.

**The defensible formulation is tiered:**

| Tier | Detection | Policy | Justification |
|---|---|---|---|
| 1 | Deterministic + checksum-validated (Aadhaar, PAN, card, tokens) | **Hard block / always substitute, no prompt** | near-zero FP rate makes automatic action safe |
| 2 | High-confidence NER above threshold | **Substitute, notify, allow undo** | good precision, low friction |
| 3 | Low-confidence / ambiguous | **Warn and require one click** | genuinely fail-closed, but bounded to the uncertain minority |
| 4 | Clean | pass | |

`ANALYSIS` This is honest, implementable, and — importantly — **a better answer than "yes, fail-closed"** when a judge probes it. State the recall number, state that leak-proofing is impossible with a probabilistic detector, and show the architecture that bounds the damage. Position as *defence in depth*, never as a guarantee.

## J.4 Differentiation against verified prior art

| Prior work | What it is (`FACT`) | Differentiation opportunity |
|---|---|---|
| **llm-redact-proxy** | Local proxy scrubbing PII/tokens before requests reach `api.anthropic.com`; gitleaks-style regex floor (~35 formats) + an **MLX** privacy-filter model | MLX is Apple-Silicon-only; no NPU path; text-only; no Indian identifiers |
| **PII Shield** (Microsoft) | FastAPI anonymise/deanonymise proxy | cloud-service shaped; no on-device/NPU story; text-only |
| **SurrogateShield** (arXiv:2606.29567) | Surrogates preserving semantic utility; no real PII crosses the API boundary | research prototype, not a deployable local app; no NPU |
| **LLM-Redactor** (arXiv:2604.12064) | MCP stdio server + HTTP proxy at `/v1/chat/completions` | same interception surface as S3 — **strongest overlap**; evaluation-focused |
| **Casper** (arXiv:2408.07004) | Prompt sanitisation for web LLMs | browser-extension scope |
| **RedactionBench** (arXiv:2606.18782) | A benchmark | **use it — do not compete with it** |

`ANALYSIS` **Differentiation opportunity** (stated as such, not as novelty): the combination of (a) a **screenshot/document path** alongside text, (b) **Indian identifier support with checksum validation**, and (c) execution on a **Hexagon NPU with measured Snapdragon latency**. I found no prior work combining all three. Each element individually exists.

`ANALYSIS` One caution: RedactionBench gives you something none of the other two concepts have — **an existing public benchmark you can report a real accuracy number on.** For the top-priority criterion, that is worth a great deal.

---

# K. PART 10 — Competition overlap audit

| Concept | Existing similarity | Overlap severity | Our differentiation |
|---|---|---|---|
| **S1** | **SnapShield** (challenge entry) — `FACT` "on-device network threat intelligence analyst… sub-5ms packet anomaly screening, local Llama 3.2 3B threat triage" | **Low** — network-packet layer, not conversational content | Different layer entirely: speech/semantic manipulation vs packet anomalies |
| **S1** | **Fraunhofer real-time deepfake detector** — `FACT` audio+video analysis warning of AI-generated participants in live video calls, **running locally on a laptop to avoid uploading footage** | **Medium** — same setting, same local rationale | Detects the **social-engineering script**, not synthetic-media artefacts. `FACT` Justified by the benchmark finding that "a detector trained on 2019 attacks does not generalize to 2026 attacks" |
| **S1** | Truecaller and caller-reputation apps | **Low** | Metadata/reputation vs in-call content |
| **S1** | Windows Live Captions / Studio Effects | **None** | different purpose |
| **S1** | Generic "AI security assistant" entries (expected at volume) | **Medium** | Specificity of the eight-primitive taxonomy + evidence-with-quotes UI |
| **S2** | **EchoSight** (challenge entry) — see §I.4 | **Medium-High on the document-reading feature; Low on Indic depth** | Indic recognition + reading-order + figure description; EchoSight is a broad copilot |
| **S2** | Windows Narrator, NVDA, JAWS | **Medium** | `FACT` documented Indic script weakness in all three |
| **S2** | Windows AI OCR API / Click to Do | **Medium** | first-party, English-centric, no reading-order reconstruction or Indic TTS |
| **S2** | Commercial Indian OCR APIs | **Low** | all cloud; S2 is offline |
| **S3** | **LLM-Redactor** (arXiv) | **High on the text proxy** | image path + Indian identifiers + NPU |
| **S3** | **llm-redact-proxy** (GitHub) | **High on concept, Low on platform** | MLX/Apple-only, no NPU, no images |
| **S3** | **PII Shield** (Microsoft) | **Medium** | cloud-shaped vs on-device |
| **S3** | Microsoft Presidio (established OSS) | **Medium** | `UNVERIFIED` whether an NPU path exists; Presidio is CPU/cloud-oriented |
| **S3** | Enterprise DLP products | **Low** | different buyer, no local-AI story |
| **All three** | **Hyperlink** (Qualcomm/Nexa) | **None** | different problem — this is the one trap all three correctly avoid |

`ANALYSIS` Prior art does not disqualify any of the three. The honest summary: **S1 has the least crowded positioning; S3 has the most crowded but also the clearest technical differentiation axis; S2 collides most directly with a submission already in this very competition.**
---

# L. PART 11 — Solo execution plans

`ANALYSIS` Calendar: today is **Mon 22 Sep (Day 0)**. Submission target is **Tue 29 Sep**, one full day before the 30 Sep 23:59 IST deadline, because the submission is immutable and the platform will be under load. That gives **Day 0 for experiments + Days 1–7 for execution.**

Common to all three plans, Day 0 (today, ~3 hours): run the experiments in §N. Everything below assumes they pass.

## L.1 S1 — Perception Firewall

| Day | Engineering | Research / Benchmark | Deliverable | Dependency | Contingency |
|---|---|---|---|---|---|
| **1** (23) | Scaffold repo; audio ring buffer + log-Mel on Mac; Whisper-Base via ORT **CPU EP** end-to-end | Submit Workbench jobs **A1–A4** | Mic → transcript working locally | Exp. 1+2 passed | If ORT CPU is slow on Mac, use `faster-whisper` for the dev loop and keep ORT for the deployment path |
| **2** (24) | The eight-primitive taxonomy: regex prefilter + Qwen3-1.7B prompt with constrained JSON output | Submit **A6–A7** (context sweep) | Transcript → structured evidence JSON | Day 1 | If constrained decoding is unreliable, fall back to a few-shot classifier prompt + strict parser |
| **3** (25) | Fusion rule engine + N-of-M hysteresis state machine; evidence store with timestamps and quotes | Build the **evaluation set**: ~15 reconstructed scam transcripts + ~15 benign controls, committed to the repo | Deterministic, explainable risk scoring | Day 2 | If the set is too small to be meaningful, report it as an illustrative set with explicit n |
| **4** (26) | UI: evidence panel, risk meter, interstitial card. Plain and legible, not styled | Run the evaluation set; record per-primitive precision | Demoable app | Day 3 | If UI time overruns, ship a terminal UI + a clean overlay for the one demo moment only |
| **5** (27) | Optional screen channel (screenshot → EasyOCR → keyword; process check) behind a feature flag | Submit **A8–A9**; assemble the benchmark table with job URLs | Multimodal fusion moment | Days 1–4 | **Cut entirely** — the audio channel alone carries the demo |
| **6** (28) | Windows ARM64 deployment writeup: `install_runtime.ps1` path, ARM64 Python requirement, `disable_cpu_ep_fallback` verification procedure. **Written, not run.** | Finish README: architecture diagram, model table, benchmark table, limitations | Complete evidence package | Day 5 | — |
| **7** (29) | Record demo twice; dry-run the Unstop submission form fully | — | **SUBMIT** | — | — |

**Critical path:** Day 1 → Day 2 → Day 3. Days 5 and the screen channel are expendable.

## L.2 S2 — Paath

| Day | Engineering | Research / Benchmark | Deliverable | Dependency | Contingency |
|---|---|---|---|---|---|
| **1** (23) | **Gating work:** export EasyOCR Devanagari recognizer to ONNX; attempt AI Hub compile | Submit **B1–B3** | Verdict on Indic OCR path | Exp. 4 | **If B3 fails, S2 is dead — switch concept on Day 1, not Day 4** |
| **2** (24) | **Second gate:** Indic TTS — evaluate AI4Bharat Indic-TTS / vani-tts ONNX export | Submit **B6** | Verdict on the voice stage | Day 1 | If no NPU path, ship CPU TTS and **explicitly exclude it from NPU claims** |
| **3** (25) | Pre-processing + detection + recognition pipeline; geometric reading-order | Submit **B4** | Scan → ordered text | Days 1–2 | — |
| **4** (26) | Structured document model; figure description via Qwen3-VL | Submit **B5**; verify model <2 GB | Scan → navigable document | Day 3 | Drop figure description if Qwen3-VL is slow or oversized |
| **5** (27) | TTS integration + navigable reader UI | Side-by-side vs NVDA capture | Demoable app | Day 2 | — |
| **6** (28) | Batch mode (300-page run) for the energy/throughput claim | **B7**; README | Evidence package | Day 5 | — |
| **7** (29) | Demo + submit | — | **SUBMIT** | — | — |

`ANALYSIS` S2 front-loads both 🔴 risks into Days 1–2, which is correct — but it means **two consecutive make-or-break days at the start of a seven-day build.** That is a materially worse risk profile than S1's.

## L.3 S3 — Airlock

| Day | Engineering | Research / Benchmark | Deliverable | Dependency | Contingency |
|---|---|---|---|---|---|
| **1** (23) | Deterministic floor: Aadhaar/Verhoeff, PAN, Luhn, IFSC, token rulesets + unit tests | **Gating:** fix GLiNER seq len to 512, export ONNX, submit **C1–C3** | Working floor + QNN verdict | Exp. 3 | **If C1 fails → pivot to Qwen3-1.7B detector and accept the weaker NPU story** |
| **2** (24) | OpenAI-compatible proxy; surrogate generator; bidirectional mapping | — | Text path end-to-end | Day 1 | — |
| **3** (25) | Tiered fail-closed policy engine (§J.3); response restoration | Evaluate on **RedactionBench** or the GLiNER card's dataset; record P/R/F1 | Real accuracy number | Day 2 | If benchmark integration is slow, evaluate on a hand-built India-specific set and say so |
| **4** (26) | Image path: EasyOCR → box masking → redacted image | Submit **C5** | Screenshot redaction demo | Day 1 | — |
| **5** (27) | Ledger UI; semantic-preservation study (answers with vs without substitution) | Submit **C6** throughput sweep | Differentiator evidence | Day 3 | Cut the semantic study if time-pressed |
| **6** (28) | Deployment writeup; README | Benchmark table with job URLs | Evidence package | — | — |
| **7** (29) | Demo + submit | — | **SUBMIT** | — | — |

---

# M. PART 12 — Demo stress test (judge sees it cold, no explanation)

## M.1 S1

| Window | What a judge sees with zero context |
|---|---|
| 0–10 s | Airplane mode toggled. A badge says local/NPU. **Reads as: this is offline AI.** |
| 10–30 s | A scam call plays; named manipulation tactics appear in real time with timestamps and quotes. **Reads as: the machine understands what is happening in the conversation.** |
| 30–60 s | Remote-access request triggers a second signal; a calm warning appears. **Reads as: multimodal fusion, and a product with judgement.** |
| 60–90 s | Benchmark table with clickable AI Hub job URLs. **Reads as: this person measured things.** |

**Would a Qualcomm engineer immediately understand why the NPU is necessary? — PARTIALLY.**

`ANALYSIS` They will immediately grasp *local execution* (airplane mode is unambiguous). They will **not** automatically grasp *NPU necessity*, because a Whisper-Base + 1.7B pipeline at a 5 s cadence is not obviously beyond a CPU. The necessity argument is **duty cycle and energy**, which is not visually self-evident and must be stated: "this runs for the whole call, every call, on battery." Mitigation: put a CPU-vs-NPU bar for the encoder on screen at 60–90 s, plus the sustained-operation framing. Without that explicit beat, the answer degrades to NO.

## M.2 S2

| Window | What a judge sees cold |
|---|---|
| 0–10 s | A bad scan is dropped in. Offline. |
| 10–30 s | Deskew, column detection, numbered reading-order arrows. **Reads as: real document understanding, not just OCR.** |
| 30–60 s | Correct Hindi audio in correct order, with a spoken figure description; NVDA side-by-side produces garbage. **Reads as: this solves something real.** |
| 60–90 s | 300-page batch with NPU-vs-CPU timing. |

**Would a Qualcomm engineer understand NPU necessity? — PARTIALLY, tending to NO for the single-page demo.**

`ANALYSIS` Reading one page is not an NPU-scale workload — a CPU does it in a second. The NPU case lives entirely in the 60–90 s batch segment (the 300-page/12.3× indexing-energy argument). If the batch segment is cut for time, the NPU justification evaporates. **The batch run is therefore not optional for S2; it is the Snapdragon argument.**

## M.3 S3

| Window | What a judge sees cold |
|---|---|
| 0–10 s | Text with an Aadhaar number and an API key is pasted into a cloud chat box. |
| 10–30 s | A diff overlay: real values struck through, surrogates substituted. "4 spans replaced · 0 left this device." |
| 30–60 s | The cloud reply comes back naming the surrogate; the overlay restores the real name. **Reads as: full answer quality, zero leakage.** |
| 60–90 s | A screenshot of a records table is pasted; black boxes appear over exactly the right cells before upload. Then latency numbers. |

**Would a Qualcomm engineer understand NPU necessity? — NO, unless the throughput segment is shown.**

`ANALYSIS` This is S3's sharpest weakness and it is a *demo* weakness rather than a technical one. A judge watching one paste being scanned sees a task a CPU handles trivially. The necessity argument requires the volume framing — every paste, every screenshot, every document, continuously — which is abstract. The screenshot-redaction moment is visually the best thing in this study, but it argues for *multimodal*, not for *NPU*. Mitigation: lead the 60–90 s segment with the C6 throughput sweep (1/10/100 payloads, NPU vs CPU) and a "scans per hour at X watts" figure.

`ANALYSIS` **Summary of this section — no concept scores a clean YES.** That is worth internalising: *on-device* is easy to demonstrate; *NPU-necessary* is not. Whichever concept is chosen, the 60–90 s segment must be engineered specifically to make NPU necessity visible, and it should be designed before the app is built, not after.

---

# N. PART 13 — Technical evidence plan

| # | Evidence item | S1 | S2 | S3 | Notes |
|---|---|---|---|---|---|
| 1 | Architecture diagram | EASY | EASY | EASY | |
| 2 | Model table with sizes/licences/sources | EASY | MEDIUM | MEDIUM | S2/S3 have BYO models to characterise |
| 3 | **Workbench per-layer NPU placement screenshot** | EASY | MEDIUM | MEDIUM | `FACT` Runtime Layer Analysis placement column |
| 4 | Snapdragon device profile (min inference, memory) | **EASY** | MEDIUM | MEDIUM | S1's models are all first-party |
| 5 | CPU vs NPU vs GPU comparison | EASY | MEDIUM | MEDIUM | force `compute_unit` per job |
| 6 | Memory footprint | EASY | EASY | EASY | Workbench reports ranges |
| 7 | **Energy** | **UNKNOWN** | **UNKNOWN** | **UNKNOWN** | Not measurable by you. Cite arXiv:2606.11257 as comparable published work only |
| 8 | Accuracy metric | **HARD** — no dataset exists | **HARD** — no ground truth | **MEDIUM** — RedactionBench / GLiNER card exist | **S3's clear advantage** |
| 9 | Offline demonstration | EASY | EASY | MEDIUM — cloud is inherent to the concept | |
| 10 | Demo video | EASY | MEDIUM — needs Hindi + subtitles | EASY | |
| 11 | Public, citable AI Hub job URLs | EASY | EASY | EASY | **highest-leverage, lowest-cost item in the whole package** |
| 12 | P50/P95 on Snapdragon | **UNKNOWN — unobtainable** | same | same | State the limitation explicitly |
| 13 | On-device end-to-end verification | **UNKNOWN — unobtainable** | same | same | Document the `disable_cpu_ep_fallback` procedure as the deployment verification step |

`ANALYSIS` Items 7, 12 and 13 are unobtainable for every concept. **Write them down as limitations rather than omitting them.** A "What we could not measure and why" section converts three weaknesses into one credibility asset, and it costs nothing.

---

# O. PART 14 — Decision matrix

| Dimension | S1 Perception Firewall | S2 Paath | S3 Airlock |
|---|---|---|---|
| User problem strength | **HIGH** | **HIGH** | MEDIUM |
| AI necessity | **HIGH** | **HIGH** | MEDIUM |
| Local AI necessity | **HIGH** | MEDIUM | **HIGH** |
| Snapdragon necessity | MEDIUM | MEDIUM | MEDIUM |
| NPU fit (duty cycle / prefill) | **HIGH** | MEDIUM (batch only) | MEDIUM |
| Technical feasibility (solo, 8 d) | **HIGH** | LOW | MEDIUM |
| Model availability | **HIGH** — all first-party AI Hub | LOW — 2 RED stages | MEDIUM — core model BYO |
| Workbench feasibility | **HIGH** | MEDIUM | MEDIUM |
| Real-time feasibility | **HIGH** (seconds is fine) | **HIGH** (offline batch) | MEDIUM (paste UX needs <400 ms) |
| Demo strength | **HIGH** | MEDIUM | **HIGH** |
| Differentiation | **HIGH** | MEDIUM | MEDIUM |
| Competition overlap | LOW (good) | **HIGH** (bad) | MEDIUM |
| Solo execution risk | MEDIUM | **HIGH** | MEDIUM |
| Deployment risk (no Windows machine) | MEDIUM | LOW | LOW |
| False-positive / false-negative risk | **HIGH** (mitigable by framing) | LOW | **HIGH** (structural) |
| Evidence quality potential | **HIGH** except accuracy | MEDIUM | **HIGH** including accuracy |
| Reference implementation exists | **YES** — `whisper_windows_py` | partial | no |

`ANALYSIS` Three observations the matrix makes visible:

1. **S2 is the weakest under these constraints.** Its two differentiating stages are its two highest-risk stages, and it collides with a submission already in the competition. Strong problem, wrong week.
2. **S1 and S3 trade cleanly.** S1 wins on model availability, feasibility, differentiation and overlap. S3 wins on accuracy evidence and platform portability. Since **Technical Implementation is the top-priority criterion and accuracy evidence feeds it**, this is a genuine trade rather than a dominance.
3. **Nothing scores HIGH on Snapdragon necessity.** That is the honest state of all three and the thing to engineer against, per §M.

---

# P. PART 15 — The Kill Test

## P.1 S1 Perception Firewall

1. **What single experiment could kill it?** Compile and profile **Whisper-Base encoder + Qwen3-1.7B (ctx 512)** on Snapdragon X Elite / X2 Elite via Workbench. If the combined minimum inference time exceeds roughly **4 s per cycle**, the always-on premise fails at a usable cadence.
2. **What would strongly validate it?** Encoder confirms ≈20–40 ms on NPU with per-layer placement showing NPU, and Qwen3-1.7B TTFT at the low end (≈50–300 ms) at 512 context.
3. **Completable today?** **Yes** — `qai-hub` runs on your Mac; both models are first-party with pre-exported assets.
4. **Abandon if:** the models will not compile for a compute-tier device, or layer analysis shows the bulk of the graph falling back to CPU.
5. **Proceed immediately if:** both profile cleanly on NPU and the arithmetic in §E.2 holds.

## P.2 S2 Paath

1. **What could kill it?** Exporting the **EasyOCR Devanagari recognizer** to ONNX and compiling it for Snapdragon. Failure means no Indic recognition, which means no differentiation from EchoSight.
2. **What would validate it?** Devanagari recognizer compiles, profiles on NPU, **and** a verified Indic TTS ONNX model exists that also compiles.
3. **Completable today?** **Partially.** The OCR export is a few hours. The TTS question is research, and I could not resolve it in this study — it may not be resolvable today at all.
4. **Abandon if:** either gate fails. `ANALYSIS` Note it is a **conjunctive** test — both must pass — which makes S2 strictly riskier than the other two.
5. **Proceed immediately if:** both pass and a clean Hindi scan produces legible text.

## P.3 S3 Airlock

1. **What could kill it?** Fixing **GLiNER-PII-edge** to a static 512 sequence length, exporting ONNX, and compiling for the Hexagon NPU. Failure, or a fallback-heavy layer placement, removes the NPU story from the component that defines the product.
2. **What would validate it?** Compiles with the bulk of layers on NPU and minimum inference **< ~100 ms** at seq 512.
3. **Completable today?** **Yes, roughly 2–3 hours** — `gliner` is on PyPI and the ONNX artefacts are published on the model card.
4. **Abandon the NPU framing (not the idea) if:** it falls back to CPU. `ANALYSIS` S3 then survives as a product but competes on the deterministic floor rather than on Snapdragon — which is a weak submission for a Snapdragon challenge.
5. **Proceed immediately if:** C1 lands under ~100 ms with NPU placement.

`ANALYSIS` The asymmetry is the decision. **S1's kill test uses two Qualcomm-published models with Qualcomm-published Snapdragon numbers — it is very likely to pass, and partly already has.** S2's is conjunctive and one half may be unresolvable. S3's is a genuine coin-flip on a model architecture with known QNN friction.

---

# Q. PART 16-N — NEXT ACTIONS — RUN THESE EXPERIMENTS BEFORE BUILDING

Five experiments. All start on your M2 MacBook Air today. Estimated total: **3–4 hours.** Run 1 and 2 first; they gate everything.

### Experiment 1 — Establish the Workbench channel (~30 min) · gates everything
Create a Qualcomm ID, get an API token, set up a Python 3.10/3.11 conda env, `pip install qai-hub qai-hub-models`, `qai-hub configure --api_token …`, then enumerate devices and record the **exact** compute-tier device strings (confirm `"Snapdragon X Elite CRD"`; find the X2 Elite equivalent — its exact name is currently **UNVERIFIED**).
**Kill condition:** no compute-tier Snapdragon device available for profiling → the entire evidence strategy changes and must be replanned before any building.

### Experiment 2 — S1 gate: Whisper-Base + Qwen3-1.7B on Snapdragon (~60 min)
Compile and profile Whisper-Base encoder and decoder (`precompiled_qnn_onnx`) and Qwen3-1.7B at ctx 512 against both compute devices, with `compute_unit` forced to NPU, then again to CPU for the baseline.
**Record:** minimum inference time, memory range, **per-layer placement**, and the **public job URLs**.
**Proceed if:** encoder lands near the published ≈22.9 ms on X2 Elite with NPU placement, and Qwen3-1.7B TTFT sits at the low end of its published range.

### Experiment 3 — S3 gate: GLiNER-PII-edge static-shape QNN conversion (~90 min)
Take `knowledgator/gliner-pii-edge-v1.0` (UINT8 ONNX, 197 MB), fix the sequence dimension to 512, submit a compile job for Snapdragon X Elite, then profile it.
**Proceed if:** it compiles, most layers show NPU placement, and minimum inference is under ~100 ms.
**Fall back if not:** re-scope S3 around Qwen3-1.7B as the detector and accept that the NPU claim weakens.

### Experiment 4 — S2 gate A: EasyOCR Devanagari export (~60 min)
Export the EasyOCR `devanagari_g2` recognizer to ONNX with fixed input shapes and submit a compile job for Snapdragon X Elite.
**Proceed if:** it compiles and profiles on NPU.
**If it fails:** stop work on S2 the same day — do not attempt Experiment 5.

### Experiment 5 — S2 gate B: Indic TTS existence check (~45 min, research not code)
Determine whether *any* Hindi TTS model with a working ONNX export and a permissive licence exists that could plausibly compile for QNN — checking AI4Bharat Indic-TTS, `vani-tts`, and sherpa-onnx's model zoo.
**Proceed only if:** a specific, downloadable, correctly-licensed ONNX Hindi voice is identified. `ANALYSIS` This is currently the single least-supported assumption in the entire study.

---

## Recommended sequencing

Run **1 → 2** first. `ANALYSIS` If Experiment 2 passes — and the published Qualcomm numbers strongly suggest it will — **S1 is the concept with the highest probability of producing a complete, evidence-backed submission by 29 September**, because every model on its critical path is first-party, already benchmarked on Snapdragon by Qualcomm, and backed by an official Windows reference app that already performs live-microphone NPU ASR.

Run **3** regardless. It is cheap, and a passing result makes S3 a genuine alternative rather than a fallback — with the one advantage S1 cannot match: a real, publishable accuracy number.

Run **4 and 5** only if you intend to keep S2 alive. On the evidence assembled here, I would not.

**Do not begin building any of the three until Experiments 1 and 2 have returned.**
