# Snapdragon® AI Lab Build & Present Challenge — Opportunity Research

**Prepared:** 22 September 2026
**Status:** Stage 1 research only. No idea selected. No code written.
**Convention used throughout:** `FACT` = verified against a cited source. `ANALYSIS` = my inference, clearly labelled and arguable.

---

## 0. Read this first — the single most important finding

`FACT` The submission window closes **30 September 2026, 11:59 PM IST**. The Unstop listing showed **"8 Days Left"** and **10,333 registered participants** when read on 22 Sep 2026. ([Unstop listing](https://unstop.com/competitions/crp-snapdragon-ai-lab-build-present-challenge-qualcomm-1748893))

`ANALYSIS` This reframes the entire exercise. This is not a semester project. Every recommendation below is filtered through "can a solo participant produce a *credible, evidence-backed* submission in ~8 days." Two consequences:

1. **Scope must be one vertical slice, executed to a high finish**, not a platform.
2. **The highest-leverage differentiator is not the app — it is measured evidence on real Snapdragon silicon.** See §3.4: Qualcomm AI Hub Workbench will run your model on physical Snapdragon X Elite / X2 devices in Qualcomm's cloud, for free, and hand you latency + memory numbers. Almost none of 10,333 entrants will do this. It maps directly onto the #1 evaluation criterion.

---

## 1. Executive Summary

**What the competition actually rewards.** `FACT` Four criteria, listed in this order: Technical Implementation, Application Use Case & Innovation, Deployment & Accessibility, Presentation & Documentation. `FACT` Ties are broken "by comparing scores in the first applicable criterion listed above, then the next applicable criterion as needed." `ANALYSIS` No weights are published, but the tie-break rule reveals a **priority ordering**. Technical Implementation is the dominant axis. A beautiful deck with a thin technical core loses to a rigorous technical core with a decent deck.

**What the rules permit that most entrants will miss.** `FACT` The solution must be "designed, developed, **or intended to be** optimised for Snapdragon-powered HP PCs." `ANALYSIS` "Intended to be" means **you do not need to own a Snapdragon HP laptop to submit legitimately**. You need a defensible optimisation *plan* plus evidence. Combined with free AI Hub Workbench cloud profiling on real devices, a participant on an x86 or Mac machine can still produce genuine Snapdragon numbers.

**The physics insight that should drive idea selection.** `FACT` A June 2026 peer-reviewed benchmark on a Snapdragon X Elite laptop measured the Hexagon NPU at **786.7 tok/s prefill vs 43.4 on CPU (18.1×)** but only **14.2 tok/s decode vs 8.17 on CPU (1.74×)**; energy per query 315 J on NPU vs 1,251 J CPU and 2,051 J GPU. ([Cheng & Lai, arXiv:2606.11257](https://arxiv.org/html/2606.11257v1)) `ANALYSIS` **The Hexagon NPU's advantage is overwhelmingly in encoding, not generation.** Therefore: pick a problem whose compute is dominated by *perception, encoding, embedding, classification and prefill* — vision, audio, OCR, retrieval, continuous monitoring — and where LLM output is *short*. Any idea whose demo is "watch the chatbot write three paragraphs" throws away 90% of the Snapdragon argument and will benchmark barely better than a CPU.

**Where the crowd is going.** `ANALYSIS` Public GitHub repos already tagged to this challenge cluster into five visible archetypes: accessibility copilot (EchoSight), AI tutor (PadhAI), privacy productivity dashboard (SnapGuardian), security analyst (SnapShield), disaster response, sign language (SetuAI), interview practice (InterviewerOS), creator studio. With 10,333 registrants, assume every "obvious" framing is submitted dozens of times. Differentiation now comes from **specificity and measured rigour**, not from category.

**What is already taken by the platform owners themselves.** `FACT` Qualcomm AI Hub now hosts Nexa AI, whose **Hyperlink** product is an on-device agentic-RAG assistant over local files, demoed at CES 2026 with Hexagon NPU acceleration. ([Qualcomm AI Hub GenAI](https://aihub.qualcomm.com/genai), [Nexa](https://nexa.ai/blogs/hyperlink-v1)) `FACT` Windows ships Recall, Click to Do, Live Captions with translation, Windows Studio Effects and improved local search as NPU-exclusive Copilot+ features. ([Microsoft](https://www.microsoft.com/en-us/windows/business/devices/copilot-plus-pcs)) `ANALYSIS` "Chat with your local documents," "search everything you saw," "live caption translation," and "webcam background effects" are **first-party features of the judge's own platform**. Proposing them is the fastest way to look uninformed.

**Recommended direction (not yet a decision).** Three shortlisted concepts survive every filter in this report most cleanly — S1 (real-time social-engineering / scam shield), S3 (local privacy airlock for cloud AI), and S2 (Indic document accessibility engine). Each is prefill/perception-dominated, structurally impossible to do well in the cloud, and demoable in under 90 seconds. Full analysis in §9; my ranking rationale and open questions are in §14.

---

## 2. Competition Analysis (Part A)

### 2.1 Verified facts

All items below were read directly from the official Unstop listing on 22 Sep 2026 and the Qualcomm Snapdragon AI Lab page.

| Item | `FACT` |
|---|---|
| Organiser | Qualcomm |
| Platform | Unstop (FLIVE Consulting Pvt Ltd) |
| Stage | Single round — "Solution Submission Round" |
| Opens | 04 Sep 2026, 12:00 PM IST |
| **Closes** | **30 Sep 2026, 11:59 PM IST** |
| Team size | **Individual participation only** |
| Registrations | 10,333 (as of 22 Sep 2026) |
| Mode | Online |
| Eligibility | Residents of India, 18+ |
| Excluded | Non-residents; individuals affiliated with government agencies or state-owned entities; Restricted Persons; entities/employees involved in running the Challenge and their households; any judge or a judge's employer; affiliates of excluded orgs; anyone with a real or apparent conflict of interest |
| Employer permission | Participant's own responsibility to obtain |
| Core requirement | Solution "must be designed, developed, or intended to be optimised for Snapdragon-powered HP PCs" |
| Novelty rule | May be newly created; if pre-existing, must be "significantly modified to add AI models from Qualcomm AI Hub **or other open-source platforms**" |
| Ownership | "The proposal must be the work and/or idea solely owned by the participant" |
| Submission limit | **One per participant; only the first counts if duplicates are received** |
| Immutability | **"A submission cannot be changed after it has been properly submitted"** |
| Criteria | Technical Implementation; Application Use Case & Innovation; Deployment & Accessibility; Presentation & Documentation |
| Tie-break | First criterion, then next, then judges vote |
| IP | **Rights remain solely with the participant**, except IP originally owned by Sponsor/affiliates/third parties |
| Confidentiality | **"Entrant Materials must not contain confidential information or trade secrets… will not be treated as confidential and may be made available to the public"** |
| Language | English, or with specified English translations |
| 1st prize | Snapdragon X2 Plus-powered HP OmniBook Ultra + opportunity for a Qualcomm internship (subject to eligibility) + showcase at a Qualcomm event |
| 2nd prize | Snapdragon X-powered HP OmniBook 3 + showcase opportunity |
| 3rd & 4th | One year of executive mentorship from Qualcomm leaders, quarterly virtual sessions |
| All | Certificate of participation |
| Award limit | Max one award per participant |
| Internship eligibility | `FACT` (from Qualcomm AI Lab page) BTech/MTech in CS, ECE or related; CGPA 7.5+ |
| Programme context | `FACT` Snapdragon AI Lab is a workshop programme with Qualcomm Academy instructors, an Arduino® UNO Q board tie-in (₹2,500 off with a Snapdragon PC purchase), ending in "Work on your AI solution & present it to Qualcomm mentors" ([qualcomm.com/snapdragon/ai-lab](https://www.qualcomm.com/snapdragon/ai-lab)) |

### 2.2 What is NOT documented — do not invent it

I could not verify any of the following from official sources, and you should not assume them:

- **Numeric weights** for the four criteria. Only the ordering is implied by the tie-break rule.
- **The exact intake-form fields.** The Unstop submission form is behind login. `ANALYSIS` **Action item: register and open the form immediately** so you know whether it wants a PDF, a video link, a GitHub URL, a word-limited abstract, or all four. Designing the artefact before knowing the container is a real risk given the one-shot, no-edit rule.
- **Whether a working prototype is mandatory.** The wording "proposals… designed, developed, or intended to be optimised" strongly suggests it is not. But see §2.3.
- **Whether hardware is loaned to participants.** Nothing in the listing says so.
- **Video/demo length limits, page limits, or a required template.**
- **Judge identities or their technical depth.**
- **Whether Qualcomm AI Hub usage is mandatory.** `FACT` The rule says AI Hub "**or other open-source platforms**" — so open-source models are explicitly allowed. `ANALYSIS` But using AI Hub is free, directly on-brand, and gives you profiling evidence. Not using it is a self-inflicted wound.

### 2.3 `ANALYSIS` — Reading the criteria like a judge

**Technical Implementation (highest priority).** This is where a Qualcomm engineer will look for: correct runtime choice (QAIRT / ONNX Runtime QNN EP / GenieX / LiteRT), explicit quantisation decisions (INT8/INT4, per-channel, calibration), a real understanding of what runs on NPU vs GPU vs CPU and why, memory footprint, and ideally **measured latency on actual Snapdragon hardware**. Hand-waving "accelerated by the 45 TOPS NPU" is the single most common failure mode and is trivially detectable by the audience you are pitching to.

**Application Use Case & Innovation.** Judges at a silicon company reward use cases that *justify the silicon*. The question behind the question is: "does this need our NPU, or is it a webapp?" A use case that is merely *compatible* with on-device AI scores far worse than one that is *impossible without it*.

**Deployment & Accessibility.** `ANALYSIS` This criterion is under-appreciated and cheap to win. It likely covers: does it actually install and run on Windows on ARM64? Is there a packaged installer? Does it work offline? Is it usable by people with disabilities, in multiple languages, on modest hardware? Concrete deliverables — an ARM64-native build, a signed installer or MSIX, a "works with zero internet" claim you can demonstrate by turning off Wi-Fi on camera, keyboard navigation and screen-reader labels — are checkable and most entrants will skip them.

**Presentation & Documentation.** Lowest tie-break priority, but it is the *only* channel through which the other three are perceived. A README with an architecture diagram, a model/runtime table, a benchmark table, and a 60–90 s demo video is the minimum credible artefact.

### 2.4 `ANALYSIS` — Implied advantages, ranked by how strongly the rules support them

| Attribute | Support in the rules | Strength |
|---|---|---|
| **On-device AI** | Core requirement is optimisation for Snapdragon PCs; the entire programme is about on-device compute | **Very strong — effectively mandatory** |
| **NPU acceleration** | Not named in the Unstop rules, but the whole Snapdragon PC value proposition and AI Hub tooling is NPU-centric | **Very strong (implied)** |
| **Qualcomm AI Hub usage** | Named explicitly as the first-listed model source | **Strong** |
| **Windows application** | "Snapdragon-powered HP PCs" = Windows on ARM64 | **Strong (implied)** |
| **Offline capability** | Not named | Moderate — a proxy for genuine on-device-ness, and easy to demo |
| **Privacy** | Not named | Moderate — strong narrative, but *everyone* will claim it; it only scores if you show what specifically cannot be sent to a cloud |
| **Low latency** | Not named | Moderate-to-strong if you *measure* it |
| **Multimodal AI** | Not named | Moderate — a good fit for NPU strengths, not itself a criterion |
| **Accessibility** | **Named in a criterion title** ("Deployment & Accessibility") | Strong, though the phrase is ambiguous between "easy to deploy/obtain" and "a11y" — `ANALYSIS` cover both |
| **Real-world usefulness** | "Application Use Case" | Strong |

### 2.5 `ANALYSIS` — Rules-derived risks specific to this contest

1. **One-shot, immutable submission.** Build a full dry-run of the submission package days early. No "I'll fix the video later."
2. **Sole ownership.** Do not use a teammate's code, a college group project, or anything whose IP is shared. Check licences of every model you bundle — note that "solely owned by the participant" refers to the proposal; third-party open-source models are explicitly contemplated, but their licences must permit your use.
3. **Submissions are public and non-confidential.** Do not put anything you want to keep secret in it. Conversely, a public GitHub repo is entirely compatible with the rules.
4. **Individual only.** No team credit. Scope accordingly.
5. **Government affiliation excludes you.** If you hold a position at a state-owned entity or a government agency, verify eligibility before investing effort.
6. **English requirement.** If your demo is in an Indian language (a strong use case), you must caption/translate it in the submission.

---

## 3. Snapdragon AI Capability Analysis (Part B)

### 3.1 Silicon

| Platform | CPU | NPU | Notes |
|---|---|---|---|
| Snapdragon X | 8-core Oryon, ~3.0 GHz | `FACT` Hexagon, **45 TOPS** | Entry Copilot+ tier; the **2nd-prize HP OmniBook 3** sits here |
| Snapdragon X Plus | 10-core Oryon, up to ~3.4 GHz | `FACT` 45 TOPS | |
| Snapdragon X Elite | 12-core Oryon, 3.4–4.2 GHz, 42 MB cache | `FACT` 45 TOPS | The device used in the RAG benchmark below |
| Snapdragon X2 Plus | `FACT` 10-core (X2P-64-100), up to 4.0 GHz | `FACT` **80 TOPS** Hexagon | **1st-prize HP OmniBook Ultra** config |
| Snapdragon X2 Elite | `FACT` up to 18 Oryon cores (3rd-gen), prime up to 5.0 GHz | `FACT` 80 TOPS (HP claims an **85 TOPS** exclusive variant) | NPU6 generation |
| Snapdragon X2 Elite Extreme | 18 cores | 80–85 TOPS | Up to 128 GB on-package memory |

`FACT` Copilot+ certification floor is 40 TOPS NPU, 16 GB RAM, 256 GB storage — all Snapdragon X parts clear it. ([Tom's Hardware](https://www.tomshardware.com/laptops/snapdragon-elite-x-windows-ai-pcs-get-official-starting-at-dollar1099-acer-dell-hp-and-lenovo-are-all-onboard-with-some-models-promising-multi-day-battery-life))

`FACT` X2 Elite memory subsystem: LPDDR5X up to 9,533 MT/s, 192-bit interface, **peak 224 GB/s**, up to 128 GB on-package; TSMC N3, ~31B transistors; NPU6 with "143% increase in scalar performance"; dual micro embedded **eNPUs** with 6× the X1's performance. ([HotHardware architecture deep dive](https://hothardware.com/reviews/qualcomm-snapdragon-x2-elite-architecture-deep-dive))

`ANALYSIS` Two under-discussed details worth exploiting in a proposal:
- **Unified memory at 224 GB/s with up to 128 GB.** The NPU, GPU and CPU share it. This is why a laptop can hold a vision encoder, an ASR model, an embedding model and a 4B LLM resident *simultaneously* — a multi-model pipeline is architecturally natural here in a way it is not on a discrete-GPU machine with 8 GB VRAM. **A multi-model always-resident pipeline is a genuinely Snapdragon-flavoured design.**
- **The eNPUs (micro embedded NPUs)** point at always-on, ultra-low-power sensing as a first-class design target. `ANALYSIS` I could not find developer-facing documentation for directly targeting the eNPUs, so do not claim you are programming them — but "always-on perception" is clearly an intended workload class.

`FACT` Sustained-load caveat: reporting indicates effective sustained AI throughput settles around 40–56 TOPS rather than the 80 TOPS peak. ([tech-insider](https://tech-insider.org/qualcomm-snapdragon-x2-elite-review-benchmarks-2026/)) `ANALYSIS` Treat peak TOPS as a marketing number in your own writing; judges will respect you more for saying so.

### 3.2 The prefill/decode asymmetry — the most decision-relevant fact in this report

`FACT` Cheng & Lai (Stanford / U. Rochester), *"Energy-Efficient On-Device RAG on a Mobile NPU,"* arXiv:2606.11257, 9 June 2026. Dell XPS 13 9345, Snapdragon X Elite, 45 TOPS INT8 NPU, Adreno X1-85, 64 GB LPDDR5x. Models: EmbeddingGemma 300M, Jina Reranker v2 Base Multilingual (278M), Qwen3-4B-Instruct.

| Metric | NPU | CPU | GPU |
|---|---|---|---|
| Prefill throughput | **786.7 tok/s** | 43.4 | 25.2 |
| Decode throughput | **14.2 tok/s** | 8.17 | 4.65 |
| Query latency (120 queries) | **9.48 s** | 37.98 s | 63.61 s |
| Energy per query | **315 J** | 1,251 J | 2,051 J |
| Indexing energy | **19.6 kJ** | 241 kJ | — |

Answer quality was at parity (NPU 9.32/10, CPU 8.95, GPU 9.03 under GPT-4.1-as-judge; ~87% identical scores).

`ANALYSIS` Four conclusions, each of which should shape idea selection:

1. **18× on prefill, 1.7× on decode.** Build something that ingests a lot and says a little.
2. **12.3× lower energy on indexing.** Bulk one-time or continuous *ingestion* is the killer NPU workload. "Index your 10,000 documents / 40 hours of lecture video overnight on battery" is a Snapdragon story. "Write me an essay" is not.
3. **The integrated GPU is the *worst* backend** — 1.7× slower than CPU and 6.5× more energy. This is counterintuitive and very few entrants will know it. Saying "we deliberately route X to NPU and Y to CPU, and explicitly avoid the Adreno for this workload, because…" is an instant credibility signal.
4. **Quality parity.** You can pre-empt the obvious judge objection ("doesn't quantised on-device inference degrade output?") with a citation.

`FACT` Corroborating the same asymmetry from the tooling side: mainstream local-LLM tools (Ollama, llama.cpp, LM Studio, text-generation-webui) **run CPU-only on these ARM chips**; touching the NPU requires NexaSDK/GenieX, AnythingLLM's bundled QNN engine, or hand-built QNN context binaries; NPU-optimised LLMs top out around 4B parameters. ([runaihome analysis](https://runaihome.com/blog/npu-vs-gpu-local-llm-2026/)) `ANALYSIS` This is a **huge** practical trap. If you "prove on-device AI" by running Ollama on the laptop, you have demonstrated the CPU and used none of Qualcomm's differentiator. Judges will know.

### 3.3 Software stack

`FACT` Qualcomm AI Hub has four surfaces ([aihub.qualcomm.com](https://aihub.qualcomm.com/)):
- **Models** — 300+ optimised ML and GenAI models (the Compute catalogue reports 221 models / 501 variants)
- **Apps** — sample native applications
- **Workbench** — convert, quantise, **profile on real cloud-hosted devices**, deploy
- **GenieX** — unified generative-AI runtime

`FACT` Supported conversion/deployment runtimes: **LiteRT**, **ONNX Runtime**, **Qualcomm AI Runtime (QAIRT)**. Workflow: convert PyTorch or ONNX → quantise → profile on 50+ device types hosted in the cloud → deploy.

`FACT` **GenieX** (developer preview, from the Nexa AI team now part of Qualcomm AI Hub): on-device generative-AI runtime; runs on **Windows ARM64 (Snapdragon X)**, Android, Linux ARM64, Dragonwing IoT; targets **Hexagon NPU, Adreno GPU, or CPU**; supports LLMs and VLMs; "almost any GGUF on Hugging Face"; entry points via CLI, Python SDK, Java/Kotlin, Docker, and an **OpenAI-compatible server**; two backends — llama.cpp (broad coverage) and Qualcomm AI Engine Direct (`geniex_qairt`, NPU-only, highest performance, compiled via AI Hub Workbench). ([GenieX docs](https://geniex.aihub.qualcomm.com/en/get-started/what-is-geniex), [Qualcomm blog](https://www.qualcomm.com/developer/blog/2026/06/geniex-developer-preview), [GitHub](https://github.com/qualcomm/GenieX))

`ANALYSIS` The **OpenAI-compatible local server** is the highest-value practical detail in this whole section. It means you can build your application against a normal OpenAI-style client, develop against any model, and swap in NPU-backed local inference — and it makes a "no network" demo trivially provable.

`FACT` **ONNX Runtime QNN Execution Provider** is the supported path for custom ONNX models on Snapdragon X NPU on Windows; AI Hub supports `--target_runtime precompiled_qnn_onnx`; target the device with `hub.Device("Snapdragon X Elite CRD")`. ([ONNX Runtime QNN EP docs](https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html), [Qualcomm blog](https://www.qualcomm.com/developer/blog/2025/05/deploy-ai-models-on-snapdragon-x-elite-with-qualcomm-ai-hub))

`FACT` **Windows AI Foundry / Windows AI APIs** provide first-party local LLM (Phi Silica), imaging, **OCR**, and semantic-search APIs on Copilot+ PCs with no model management; **Foundry Local** exposes 20+ open-source LLM and speech models over an OpenAI-compatible API on any Windows hardware. ([Microsoft Learn](https://learn.microsoft.com/en-us/windows/ai/windows-ai-comparison)) `ANALYSIS` Useful as a *fallback/complement*, but be careful: a submission built entirely on Windows AI APIs is a Microsoft demo, not a Qualcomm one. Use Windows OCR for convenience, but keep your differentiated compute on QNN/GenieX so the Snapdragon story is yours.

### 3.4 AI Hub Workbench — the free Snapdragon hardware you do not own

`FACT` AI Hub Workbench is **currently completely free**; requires a Qualcomm ID and an API token; **automatically provisions physical devices in Qualcomm's cloud** for on-device profiling and inference; profile jobs measure the resources needed to run an optimised model across a wide array of real devices, reporting load, compile and inference timing plus memory, designed to tell you "if a model fits within your time and memory budget." ([Workbench docs](https://workbench.aihub.qualcomm.com/docs/hub/index.html), [FAQ](https://workbench.aihub.qualcomm.com/docs/hub/faq.html))

`FACT` Recent Workbench release notes list QAIRT 2.45.0 / 2.46.0 / 2.47.0 and continually added devices.

`ANALYSIS` **This is the strategic centrepiece of any submission.** Within a day you can: export your chosen models via `qai_hub_models`, compile for `Snapdragon X Elite` / `X2` targets, submit profile jobs, and receive a table of real measured on-device inference latency and memory. That table, in your README and on a slide, converts "Technical Implementation" from an assertion into evidence. It is available to every one of the 10,333 entrants and will be used by very few.

### 3.5 Known practical traps (`FACT`, and each is a real schedule risk)

- **ARM64 Python is not the supported path for AI Hub tooling.** Only AMD64 Python is supported on Windows for Snapdragon X / X2 users; ONNX Runtime quantisation utilities are x86_64-only because `onnx` fails to install on ARM64. Recommended workaround: quantise on an x64 machine, or keep a separate x64 Python on the ARM64 laptop. ([ai-hub-models issue #258](https://github.com/qualcomm/ai-hub-models/issues/258), Qualcomm docs)
- **Windows on ARM app compatibility is good but not total.** `FACT` >93% of apps users spend time in run natively on Windows ARM; Visual Studio 2022, .NET and VS Code all have native ARM64 builds; Electron requires care (arch-selection logic often picks wrong; native modules must build against MSVC v142 with ARM64 `.dll`/`.lib` available); kernel-adjacent and anti-cheat software remains problematic. ([Electron docs](https://www.electronjs.org/docs/latest/tutorial/windows-arm), [Windows on ARM compatibility tier list 2026](https://www.witechpedia.com/windows-on-arm-app-compatibility/))
- **Mainstream local-LLM runtimes ignore the NPU entirely** (see §3.2).
- **NPU LLM ceiling is ~4B parameters** on this class of device.

`ANALYSIS` Implication for tech choice: **prefer C++/C# (WinUI 3 or WPF) or a Python backend + lightweight web UI over Electron**, and never make NPU access depend on a fragile toolchain you cannot rebuild the night before the deadline.

---

## 4. Qualcomm AI Hub Capability Map (Part B, deliverable)

Format: **CAPABILITY → AVAILABLE MODELS → SNAPDRAGON SUPPORT → RUNTIME → POSSIBLE APPLICATION**

Model names below are `FACT` from the AI Hub Models catalogue and the compute model list. ([ai-hub-models](https://github.com/qualcomm/ai-hub-models), [AI Hub compute models](https://aihub.qualcomm.com/compute/models))

| Capability | Available models | Snapdragon support | Runtime | Possible application |
|---|---|---|---|---|
| **Speech recognition** | Whisper (multiple sizes), Distil-Whisper, Whisper-Large-v3-Turbo, DeepSpeech2 | X / X Elite / X2; Whisper exportable as `precompiled_qnn_onnx` (separate encoder + decoder) | QNN / ONNX RT QNN EP | Real-time transcription, live captioning, voice-driven data entry |
| **Text-to-speech** | MeloTTS, PiperTTS | Compute-capable | ONNX / QNN | Document reading for low-vision users, spoken alerts |
| **Audio classification** | YamNet | Yes | ONNX / QNN | Acoustic event detection, environment/context sensing |
| **OCR / text detection** | EasyOCR (+ Windows AI OCR API as a complement) | Yes | ONNX / QNN | Scanned document ingestion, screen text extraction |
| **Image classification** | MobileNet-v2/v3, ResNet, EfficientNet, ViT, Swin, ConvNext, RepViT, LeViT, RegNet (50+) | Yes | ONNX / QNN / LiteRT | Triage/gating stage in a perception pipeline |
| **Object detection** | YOLOv3→v11, DETR variants, Faster R-CNN, SSD, CenterNet, RTMDet, MediaPipe Face/Hand, OWL-ViT (open-vocab) | Yes | ONNX / QNN | UI element detection, document region detection, safety/QC |
| **Segmentation** | DeepLab, U-Net, FCN, FFNet, DDRNet, Mask2Former, **SAM variants (SAM3 Windows sample exists)** | Yes | ONNX / QNN | Document layout, region isolation, redaction masking |
| **Pose / landmarks** | MediaPipe Pose, HRNet, MoveNet, RTMPose, facial landmarks | Yes | ONNX / QNN / LiteRT | Gesture input, ergonomics, sign-language front end |
| **Depth estimation** | Depth-Anything, MiDaS | Yes | ONNX / QNN | Scene understanding, AR-ish overlays |
| **Super resolution / restoration** | ESRGAN, Real-ESRGAN, QuickSRNet, LaMa, DnCNN | Yes | ONNX / QNN | Enhancing low-quality scans before OCR |
| **Embeddings / retrieval** | CLIP, text embedding models (EmbeddingGemma 300M and Jina Reranker v2 demonstrated on X Elite in the arXiv benchmark) | Yes | ONNX / QNN | **Local semantic index — the strongest NPU-fit workload** |
| **LLM (text)** | Qwen3-0.6B / 1.7B / 4B / 4B-Instruct-2507 / 8B, GPT-OSS-20B (MoE, extended context), Llama, Mistral, Phi, Gemma, Falcon, Granite | Compute tier explicitly listed; practical NPU ceiling ~4B | **GenieX** (`geniex_qairt` NPU-only, or llama.cpp backend), QAIRT/Genie SDK | Short structured generation, classification, summarisation, tool-calling |
| **VLM (multimodal)** | Qwen2.5-VL-7B-Instruct, Qwen3-VL-4B / 8B-Instruct, Gemma-4-E2B/E4B-it, Intern3.5-VL-2B | Compute tier | GenieX | **Screen understanding, document understanding, scene description** |
| **Image generation** | Stable Diffusion v1.5 / v2.1, ControlNet-Canny | Yes (Windows Python sample) | ONNX | Creative tooling (crowded; see red flags) |
| **Translation** | Translation models in catalogue; **IndicTrans2** (open-source, all 22 scheduled Indic languages) as an external option | Needs own conversion | ONNX / QNN | Indic-language document and speech workflows |
| **Indic ASR** | **IndicConformer** (AI4Bharat, 30M params, 22 languages; ONNX INT8 conversions exist for 8 languages) | Needs own conversion + profiling | ONNX / QNN | Indic voice input, offline, tiny footprint |

`FACT` **Existing Windows sample apps** in `qualcomm/ai-hub-apps`: ChatApp (C++, Genie SDK), Image Classification (C++, ONNX), Object Detection (C++, ONNX), Super Resolution (C++, ONNX), **Whisper Speech-to-Text (Python, ONNX)**, **Stable Diffusion (Python, ONNX)**, **SAM3 Segmentation (Python, ONNX)**, GenieX Chat Windows (Go).

`ANALYSIS` These samples are your scaffolding and your schedule insurance. Whisper + SAM3 + a VLM through GenieX, glued together, is the fastest credible path to a working multimodal pipeline in 8 days. They also tell you what Qualcomm considers a *baseline* — so a submission that is essentially one of these samples with a new UI will read as unambitious.

---

## 5. AI Problem Landscape (Parts C & D)

### 5.1 The filter I applied to every domain

For each domain I asked the twelve questions in the brief, but three of them do almost all the discriminating work:

- **Q6 — does an NPU provide meaningful value?** Only "yes" if the workload is *continuous*, *high-volume*, *encoder/prefill-dominated*, or *battery-constrained*. A once-a-minute LLM call does not qualify.
- **Q5 — is local genuinely better?** Only "yes" if there is a *structural* reason: the data legally or practically cannot leave (call audio, patient records, unreleased source code, court documents), the latency budget is sub-100 ms in a perception loop, the volume makes cloud cost prohibitive, or there is no network.
- **Q11 — feasible solo in 8 days?** Brutal filter. Anything needing data collection, model training, or a novel dataset is out.

### 5.2 `ANALYSIS` — What becomes possible when AI runs continuously and locally (Part D)

Cloud AI is *transactional*: you pay per call, you accept 300–2000 ms of round trip, and you must be willing to upload the data. Local NPU AI is *ambient*: marginal cost ≈ 0, latency is tens of milliseconds, and nothing leaves. The workflows that only exist on the far side of that line are:

1. **Continuous perception with a veto.** Anything that must watch *everything* to catch a rare event — a scam pattern in a live call, a PII leak in an outbound prompt, a defect on a line, a phishing overlay on screen. Cloud economics kill "analyse every second"; NPU economics make it free. **This is the strongest structural category.**
2. **Bulk private ingestion.** Indexing an entire drive, a decade of email, 40 hours of lecture video, a firm's contract archive. 12.3× energy advantage on indexing is a real product fact, and the data often legally cannot be uploaded.
3. **Closed perception-action loops faster than human reaction.** Live captioning, live interpretation, gaze/gesture input, real-time guidance overlays. A 700 ms cloud round trip destroys the experience; 40 ms local does not.
4. **Personalisation from data that must never leave.** A model that adapts to *your* files, *your* voice, *your* habits without a training pipeline that uploads them.
5. **Work in places with no network at all.** Fieldwork, factory floors, rural clinics, aircraft, secure facilities, disaster zones.

`ANALYSIS` **Critically — these characteristics do not make an idea good.** Each is necessary, none is sufficient. "Privacy" in particular is the most over-claimed and least differentiating attribute in this entire competition: with 10,333 entrants, "it's private because it's local" will appear in thousands of decks. Privacy only *scores* when you can name a specific dataset that is *legally or contractually prohibited* from leaving the machine, and show the feature that depends on having it.

### 5.3 Domains surveyed

I examined 22 domains. Rather than pad this section, here is the honest triage:

**Domains that survived (detailed in §6):** digital safety / fraud, accessibility, privacy-preserving AI tooling, education (specifically Indic/offline), document & legal intelligence, developer/security engineering, field/offline work, journalism & research, HCI / screen understanding, knowledge work, healthcare-adjacent documentation, SME operations.

**Domains I examined and largely rejected for *this* competition, with reasons:**

- **Content creation / creators.** `ANALYSIS` Stable Diffusion on Snapdragon is a solved, shipped sample. The space is saturated commercially and among entrants ("Zero-Cloud Local Creator Studio" already exists as a submission). Image-gen quality on a 4B-class local model will look worse than free cloud tools on camera. Weak demo economics.
- **Meetings / note-taking.** `FACT` Already a crowded *local-first* market: Meetily (MIT-licensed, 100% local, on-device diarization), LUCI (on-device diarization on Mac and Windows, 4-hour sessions), OpenWhispr (MIT, local system-audio capture, on-device Whisper/Parakeet + diarization), BB Recorder. ([Meetily](https://meetily.ai/), [buildbetter comparison](https://blog.buildbetter.ai/best-granola-alternatives-private-meeting-notes-2026/)) The differentiated version is already free and open source. Rejected as a primary idea.
- **Personal knowledge management / "chat with my files."** `FACT` **Qualcomm itself now ships this** via Hyperlink (Nexa AI, part of AI Hub), NPU-accelerated, demoed at CES 2026. Rejected — you would be pitching the sponsor's own product back to them.
- **Manufacturing / retail computer vision.** `ANALYSIS` Real problems, but the deployment target is a camera on a line, not an HP consumer laptop, and you cannot obtain a credible defect dataset in 8 days. The demo would be a toy.
- **Travel, finance/personal productivity, parents.** `ANALYSIS` Real but low AI-necessity; these are mostly CRUD apps with a summarisation feature. They fail the "would this be impossible without AI?" test.
- **Gaming workload intelligence.** Already a visible entrant archetype (SnapPlay); NPU relevance is thin; hard to measure.
- **Government/public service workflows.** `ANALYSIS` Note the eligibility rule excludes people *affiliated with* government agencies — building *for* government is fine, but you cannot pilot with one, and any demo will be mocked data. Keep as a use-case flavour, not the core.

`ANALYSIS` I want to be explicit that rejecting a domain is not a judgement about its importance. ASHA workers' documentation burden is a far more consequential problem than anything else in this report — `FACT` 160,000+ ASHAs in Uttar Pradesh alone serve ~232 million people, juggling seven apps plus WhatsApp groups, Sheets and Excel, with mandatory parallel paper records, sometimes working to midnight. ([PMC13245931](https://pmc.ncbi.nlm.nih.gov/articles/PMC13245931/), [New Lines Magazine](https://newlinesmag.com/reportage/indias-digital-health-push-is-overworking-its-front-line-women/)) It is rejected as a *primary* concept only because the delivery device is a ₹6,000 Android phone in a village, not a ₹1.5 lakh Snapdragon HP laptop — which makes "why Snapdragon PC?" structurally hard to answer honestly. Forcing it would be exactly the kind of contrivance §8 warns against.

---

## 6. Opportunity Matrix — 25 Problems (Part H)

### 6.1 Scoring rubric (internal analysis only, 1–5)

These are not vibes. Each axis has a defined meaning:

- **Innovation (INN):** 1 = exists as a shipped consumer feature; 3 = exists but poorly/expensively/cloud-only; 5 = no credible existing implementation of this specific mechanism.
- **Usefulness (USE):** 1 = nice-to-have; 3 = saves real time weekly; 5 = prevents serious harm or unblocks something currently impossible.
- **Local advantage (LOC):** 1 = cloud equally fine; 3 = local is meaningfully better; 5 = cloud version cannot legally/practically exist.
- **Snapdragon/NPU advantage (NPU):** 1 = NPU idle; 3 = NPU helps throughput; 5 = continuous/prefill-dominated workload where NPU changes what's possible per watt.
- **Prototype feasibility in 8 days solo (FEA):** 1 = impossible; 3 = a convincing slice; 5 = comfortably done.
- **Demo strength (DEM):** 1 = you must explain why it's impressive; 5 = a judge understands and reacts within 15 seconds.
- **Differentiation vs other entrants (DIF):** 1 = dozens of near-identical submissions expected; 5 = unlikely to be duplicated.

`ANALYSIS` I deliberately did **not** average these into a single score. A 5/5/5/5/1 idea is worthless and a mean would hide that. FEA and DIF act as gates.

### 6.2 The matrix

| # | Problem | Target user | INN | USE | LOC | NPU | FEA | DEM | DIF |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Live social-engineering / scam-call & screen-coercion detection | Anyone on a call; elderly & first-time internet users especially | 4 | 5 | 5 | 5 | 3 | 5 | 4 |
| 2 | Indic document accessibility (scanned PDF → structured → Indic TTS) | Blind/low-vision Indian students & professionals | 4 | 5 | 4 | 4 | 4 | 4 | 3 |
| 3 | Local "AI airlock" — PII/secret redaction gateway for cloud AI | Devs, lawyers, healthcare, anyone pasting into ChatGPT | 4 | 5 | 5 | 4 | 4 | 5 | 5 |
| 4 | Code-switched (Hinglish) live lecture/meeting captioning + translation | Indian students, multilingual workplaces | 4 | 4 | 4 | 5 | 3 | 4 | 3 |
| 5 | Offline voice→structured-form intake in Indic languages | Field workers, clinic front desks, surveyors | 3 | 5 | 5 | 4 | 4 | 3 | 3 |
| 6 | Screen-understanding "guide me through this" for low-digital-literacy users | First-time PC users, elderly, govt-portal users | 5 | 5 | 4 | 5 | 2 | 5 | 5 |
| 7 | Air-gapped code & repo security triage | Regulated/defence/fintech dev teams | 2 | 4 | 5 | 3 | 4 | 2 | 2 |
| 8 | Offline viva/oral-exam practice with rubric scoring | Students, ESL speakers | 2 | 3 | 2 | 3 | 4 | 3 | 1 |
| 9 | Continuous webcam ergonomics/attention wellbeing | Knowledge workers, students | 2 | 2 | 5 | 5 | 4 | 3 | 2 |
| 10 | Multimodal lecture-archive search (video+slides+speech) | Students with recorded courses | 3 | 4 | 4 | 5 | 3 | 4 | 3 |
| 11 | Confidential interview/qualitative-research workbench | Journalists, social scientists, HR investigators | 4 | 4 | 5 | 4 | 4 | 3 | 4 |
| 12 | Offline contract/clause risk diff | Small law firms, founders | 3 | 4 | 5 | 3 | 3 | 3 | 3 |
| 13 | Non-diagnostic clinical documentation scribe, offline | Small clinics, rural doctors | 3 | 5 | 5 | 4 | 3 | 3 | 3 |
| 14 | Laptop + USB-camera visual QC for micro-factories | MSME manufacturers | 3 | 4 | 4 | 4 | 2 | 4 | 3 |
| 15 | Offline crop-disease + advisory for extension workers | Agri extension officers | 2 | 4 | 5 | 3 | 2 | 3 | 2 |
| 16 | Indian Sign Language interpretation | Deaf users | 4 | 5 | 4 | 5 | 1 | 5 | 1 |
| 17 | Offline personal-finance statement ingestion | Individuals, small traders | 2 | 3 | 4 | 3 | 4 | 2 | 2 |
| 18 | Local dataset-labelling accelerator | ML researchers/students | 3 | 3 | 3 | 5 | 4 | 2 | 3 |
| 19 | On-device child/elder digital-safety guardian | Families sharing a PC | 3 | 4 | 5 | 5 | 3 | 4 | 3 |
| 20 | Semantic screen recorder → reproducible bug report | QA engineers, support desks | 4 | 4 | 3 | 4 | 3 | 4 | 4 |
| 21 | Offline multilingual counter-assistant for kirana/retail | Small retailers | 2 | 3 | 4 | 3 | 3 | 2 | 2 |
| 22 | Offline translation of scanned regional-language govt records | Citizens, RTI users, land-record disputes | 3 | 4 | 4 | 4 | 3 | 3 | 3 |
| 23 | Real-time Indic classroom captioning with no internet | Rural/low-connectivity classrooms | 3 | 5 | 5 | 5 | 3 | 4 | 3 |
| 24 | Local DLP for shared/family PCs | Households, cyber-cafés, labs | 2 | 3 | 5 | 4 | 3 | 2 | 2 |
| 25 | Battery/thermal-aware local AI scheduler (meta-tool) | Developers building on-device AI | 3 | 2 | 3 | 4 | 3 | 1 | 4 |

### 6.3 Per-opportunity detail

Below: current workaround · existing products · AI opportunity · local advantage · Snapdragon advantage · candidate models · multimodal potential · risk · evidence. (Abbreviated for the low-ranked entries.)

**1. Live social-engineering / scam-call & screen-coercion detection.**
*Workaround:* awareness campaigns, caller-ID blocklists, after-the-fact bank complaints. *Existing:* Truecaller (metadata/reputation, not content); bank SMS warnings; `FACT` Fraunhofer built a prototype combining audio+video analysis to warn of AI-generated participants in live videoconferences, **running locally on a high-performance laptop specifically to avoid uploading sensitive footage** ([Biometric Update, Aug 2026](https://www.biometricupdate.com/202608/fraunhofer-develops-real-time-deepfake-detector-for-video-calls)). *AI opportunity:* detect the *script* of a scam — authority impersonation, urgency, isolation instructions, remote-access/screen-share coercion, payment redirection — rather than the caller's identity. *Local advantage:* you cannot stream a citizen's live phone/video call to a cloud service; that is itself a privacy catastrophe and probably unlawful. *Snapdragon advantage:* continuous ASR + classification for the full duration of every call, at NPU wattage; a cloud version costs money per minute and leaks everything. *Models:* Whisper / IndicConformer for streaming ASR, a small text classifier or Qwen3-1.7B for intent scoring, optional YamNet for acoustic context, optional screen OCR for overlay/remote-desktop detection. *Multimodal:* audio + screen state is the killer combination — "someone is talking about police cases AND asking you to install AnyDesk AND a bank page is open" is a far stronger signal than any single channel. *Risk:* false positives; adversarial evolution; the ethics of listening to calls (must be explicitly user-initiated and local-only). *Evidence:* `FACT` Indians lost ~₹22,495 crore to cyber fraud in 2025 per MHA/I4C; digital-arrest/impersonation scams cost >₹4,000 crore between 2022 and mid-2026; RBI reported ₹48,021 crore of fraud in FY26, up 46.4%; 65% of Indian organisations reported at least one deepfake-driven attack (Thales 2026). ([ScamWatchHQ summary](https://scamwatchhq.com/india-scams-2026-digital-arrest-upi-fraud-epidemic/), [Caller Digital](https://caller.digital/blog/ai-voice-deepfake-fraud-caller-trust-india-2026)) A Bengaluru software engineer lost ₹11.8 crore to a single digital-arrest scam ([Deccan Herald](https://www.deccanherald.com/india/karnataka/bengaluru/software-engineer-in-bengaluru-loses-rs-118-crore-to-digital-arrest-scam-3329400)).

**2. Indic document accessibility engine.**
*Workaround:* NVDA/JAWS + sighted help; retyping; abandoning materials. *Existing:* NVDA, JAWS, Windows Narrator, Adobe OCR, Google Lens. *Gap:* `FACT` "Many screen readers and OCR tools struggle with Indian scripts like Hindi, Tamil and Bengali"; NVDA/JAWS Indian-language TTS and OCR accuracy is "inconsistent"; image-only PDFs, slide decks and image-only newspapers are unreadable; **students have changed university courses because they could not read course PDFs**. ([The Wire](https://m.thewire.in/article/rights/bridging-the-digital-divide-for-visually-impaired-south-asians-language-technology-and-inclusion), [Newslaundry](https://www.newslaundry.com/2025/03/04/available-tech-affordability-drawbacks-all-you-need-to-know-about-indias-accessibility-gap)) *AI opportunity:* scanned page → deskew/denoise → layout segmentation → reading-order reconstruction → Indic OCR → structured semantic document → Indic TTS, with figure/table description by a VLM. *Local advantage:* course material, medical records and legal papers are personal; and accessibility tools must work without a network to be dependable. *Snapdragon advantage:* full-document OCR + layout + VLM description is exactly the bulk-encoder workload the NPU wins at (12.3× lower indexing energy); batch-processing a 300-page textbook on battery is the story. *Models:* EasyOCR, Real-ESRGAN/QuickSRNet pre-enhancement, DDRNet/Mask2Former for layout, Qwen3-VL-4B for figure description, MeloTTS/PiperTTS or Indic TTS. *Risk:* **EchoSight, a direct competitor, already exists in this challenge**; Indic OCR accuracy may disappoint on real scans. *DIF is 3, not 5, for that reason.*

**3. Local "AI airlock" — PII/secret redaction gateway for cloud AI.**
*Workaround:* corporate policies telling people not to paste secrets into ChatGPT, which they ignore. *Existing:* `FACT` a real and growing category — llm-redact-proxy (local proxy scrubbing PII/tokens before requests reach api.anthropic.com, regex floor from gitleaks + a local MLX privacy-filter model), Microsoft's PII Shield (FastAPI anonymise/deanonymise proxy), SurrogateShield (arXiv 2606.29567 — surrogates that preserve semantic utility), LLM-Redactor (arXiv 2604.12064), Casper (arXiv 2408.07004), RedactionBench (arXiv 2606.18782). ([LogRocket walkthrough](https://blog.logrocket.com/build-local-ai-proxy-redact-pii-before-llms/), [llm-redact-proxy](https://github.com/CupOfGeo/llm-redact-proxy)) *Gap:* the existing tools are mostly **regex + a CPU model on developer machines**, text-only, and they degrade answer quality by destroying context. *AI opportunity:* NER + a small LLM doing *surrogate substitution* (stable, type-consistent fake entities) rather than blunt masking, extended to **screenshots and documents**, with reversible de-anonymisation on the way back. *Local advantage:* structurally absolute — a cloud redaction service that receives your un-redacted data defeats its own purpose. This is one of the very few ideas where cloud is *logically impossible*, not merely worse. *Snapdragon advantage:* every keystroke/paste/screenshot must be scanned continuously with a <100 ms budget and zero battery impact; this is the definitional NPU workload. *Models:* a token-classification NER model (ONNX), Qwen3-0.6B/1.7B for context-sensitive judgement, EasyOCR + Qwen3-VL for screenshot redaction, SAM for visual masking. *Multimodal:* redacting a screenshot before it goes to a cloud VLM is a genuinely novel and very visual demo. *Risk:* recall failures are catastrophic by nature (one missed Aadhaar number = product failure); needs a fail-closed design. *DIF 5 because the multimodal + surrogate + NPU combination is not, as far as I can find, shipped anywhere.*

**4. Code-switched Hinglish live captioning + translation.**
*Existing:* Windows Live Captions with translation (`FACT` NPU-accelerated, Copilot+ exclusive), Google/Teams captions. *Gap:* `FACT` most STT uses *utterance-level* language ID, committing to one language per segment, so intra-sentential code-switching pushes English phonemes through a Hindi model and vice versa, producing substitutions and deletions; global models hit 14–16% WER on noisy Hindi-English code-mixed telephony vs 11–14% for Indic-specialised models; **>250 million people in India code-switch**. ([Gnani.ai](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr), [HiACC corpus](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12329218/), [Interspeech 2025](https://www.isca-archive.org/interspeech_2025/biswas25_interspeech.pdf)) *AI opportunity:* run Whisper and IndicConformer **in parallel on the NPU** and fuse at the segment or token level, instead of picking one. *Snapdragon advantage:* dual-model concurrent streaming ASR is only affordable with a dedicated accelerator and unified memory. *Risk:* fusion quality is a research problem; you would need to show honest WER numbers, and they may not beat the baseline.

**5. Offline voice→structured-form intake in Indic languages.** *Evidence:* `FACT` the ASHA documentation-burden literature above; an offline on-device app where workers photograph blank forms, fields are extracted, and they complete them by speaking in their native language is already being prototyped elsewhere. *Risk:* device mismatch (phone problem, not laptop problem) — see §5.3.

**6. Screen-understanding "guide me through this."** *Existing:* `FACT` Microsoft OmniParser V2 parses UI screenshots into structured interactable elements + OCR + icon descriptions, works as a plugin for Phi-3.5-V and Llama-3.2-V, and tops WindowsAgentArena ([arXiv:2408.00203](https://arxiv.org/abs/2408.00203)); Windows Click to Do uses local vision models on screen content; `FACT` an A11y-CUA dataset paper (arXiv:2602.09310) characterises the accessibility gap in computer-use agents. *AI opportunity:* not an agent that clicks for you — a **coach that points**, showing the next step as an overlay, in the user's language, on any application including legacy government portals with no API. *Snapdragon advantage:* screen parsing must run every frame the UI changes; cloud round-trips make it unusable and uploading a citizen's screen is unacceptable. *Risk:* **FEA is 2** — UI grounding is hard, overlays are fiddly, and failure is visible. Genuinely exciting, genuinely risky in 8 days.

**7. Air-gapped code security triage.** *Existing:* `FACT` a mature commercial category — Tabnine Enterprise (air-gapped, hybrid local models), Tabby (open source, self-hosted, local by default), Sourcegraph Cody on-prem, Bodega One Code air-gap mode ([IntuitionLabs review](https://intuitionlabs.ai/articles/enterprise-ai-code-assistants-air-gapped-environments)). *Why rejected:* DIF 2 — you would be a student re-implementing a funded product category, and the demo is text scrolling past. NPU value is moderate.

**8–9, 17, 21, 24, 25.** Kept in the matrix for completeness; all fail either DIF or DEM. #9 (webcam ergonomics) has perfect LOC/NPU scores and is a favourite of hackathon entrants precisely because it's easy — which is why it will be duplicated and why USE is only 2.

**10. Multimodal lecture-archive search.** Strong NPU fit (bulk indexing of video — the 12.3× energy case). Risk: overlaps Hyperlink and Recall conceptually; must be framed around *video+slide+speech alignment*, which neither does well, to survive.

**11. Confidential interview/qualitative-research workbench.** *Users:* journalists protecting sources, social scientists with ethics-board constraints, HR investigators. *Local advantage:* 5 — source protection and IRB/ethics approvals frequently *prohibit* cloud upload outright. *Gap:* NVivo/ATLAS.ti are expensive and not AI-native; Otter trains on user data (`FACT`). *Why not top-3:* DEM 3 — thematic coding is hard to make visually exciting in 60 seconds.

**13. Offline clinical documentation scribe.** High USE and LOC. Risk: regulatory sensitivity; must stay strictly non-diagnostic; hallucinated clinical text is a serious harm vector, which makes it an uncomfortable thing to demo live.

**16. Indian Sign Language.** FEA 1 and DIF 1 — `FACT` a submission (SetuAI) already exists in this very challenge, and it is honest about being a "9-sign starter vocabulary, rule-based classifier." That is the tell: real ISL recognition needs datasets you cannot obtain in 8 days. **Avoid.**

**19. Child/elder digital-safety guardian.** Overlaps #1 and #3; probably better folded into #1 as a persona than pursued separately.

**20. Semantic screen recorder → reproducible bug report.** `ANALYSIS` Underrated. Developers already record screens for bug reports; turning a recording into structured repro steps + environment + a diffable trace is a real unmet need, NPU-suited (dense frame analysis), and unlikely to be duplicated. Weakness: narrow audience, and "Deployment & Accessibility" is hard to argue for a dev tool.

**22–23. Indic government records / classroom captioning.** `FACT` Supporting evidence: rural teledensity 60.74% with 554.41M rural subscribers as of April 2026, but a **29% gap in reliable connectivity between rural and urban schools**, with many government schools lacking electricity and internet, and digital content misaligned with state syllabi and local languages. ([IBEF](https://www.ibef.org/blogs/impact-of-the-digital-india-programme-on-rural-connectivity), [VidyaXR](https://vidyaxr.in/blog/digital-learning-in-rural-india)) `ANALYSIS` Real problem, honest offline argument — but again, the deployment device in a rural school is rarely a premium Snapdragon laptop. Usable as a *secondary* framing for #4 or #23 only if you are candid about the device assumption (e.g. one teacher laptop serving a classroom, which is actually defensible).

---

## 7. Existing Solution Landscape (Part E)

### 7.1 What the platform owners already ship — treat as off-limits

| Capability | Who already ships it | Implication |
|---|---|---|
| Chat with your local files, agentic RAG, cited answers, 100% offline | `FACT` **Hyperlink by Nexa AI — now part of Qualcomm AI Hub**, NPU-accelerated, CES 2026 demo | Do not propose. You would be pitching the sponsor's product to the sponsor. |
| Search everything you saw on screen | `FACT` Windows **Recall** (Copilot+ exclusive, NPU) | Do not propose. |
| Local vision analysis of on-screen content, table→Excel extraction | `FACT` Windows **Click to Do** | Do not propose the generic version. |
| Live captions with translation | `FACT` Windows **Live Captions**, NPU, Copilot+ exclusive | Only viable with a specific, defensible gap (e.g. code-switching, §6.3 #4). |
| Webcam background blur, eye contact, auto-framing | `FACT` **Windows Studio Effects**, NPU | Do not propose. |
| Local image generation / restyle | `FACT` **Cocreator / Photo Restyle in Paint**; plus the official Stable Diffusion Windows sample in `ai-hub-apps` | Saturated. |
| Local LLM chat app on NPU | `FACT` Official **ChatApp** (C++, Genie SDK) and **GenieX Chat Windows** (Go) samples | A chat UI is the *starting point*, not the submission. |
| Local OCR, image description, text summarisation, Phi Silica chat | `FACT` **Windows AI APIs** on Copilot+ PCs | Use as a component; never as the differentiator. |

### 7.2 What competing entrants appear to be building

`FACT` Public GitHub repositories self-identifying with this challenge, as of 22 Sep 2026:

| Project | Positioning |
|---|---|
| EchoSight | "On-device accessibility copilot… real-time captioning, scene narration, document reading on the Hexagon NPU" |
| PadhAI | AI tutor; "entire pipeline on-device… Qualcomm AI Hub models on the Hexagon NPU — no cloud, no per-query cost" |
| SnapGuardian AI | "On-device, zero-cloud privacy, multimodal productivity engine… 45 TOPS Hexagon NPU via Qualcomm AI Hub and ONNX Runtime" |
| SnapShield | "Autonomous on-device network threat intelligence analyst… sub-5ms packet anomaly screening, local Llama 3.2 3B threat triage" |
| SetuAI | Indian Sign Language; self-described "9-sign starter vocabulary, rule-based classifier, in-browser" |
| ResponseNet offline | "Whisper STT + on-device LLM triage… disaster-response requests work with zero internet" |
| InterviewerOS | Interview practice |
| SnapPlay AI | Gaming workload intelligence |
| Zero-Cloud Local Creator Studio | Creator tooling |

`ANALYSIS` Three inferences:

1. **The archetypes are saturated.** Accessibility copilot, AI tutor, privacy productivity dashboard, security analyst, offline disaster response — each will have dozens to hundreds of near-identical submissions among 10,333 entrants.
2. **Most are shallow.** SetuAI's own README admits a rule-based 9-sign classifier running in-browser — i.e. no NPU at all. `ANALYSIS` The median submission will *claim* NPU acceleration without demonstrating it. This is the gap you exploit: **measured numbers beat claimed numbers**, and the bar is lower than it looks.
3. **Framing beats category.** You can still enter a crowded category if your framing is specific enough to be memorable ("the scam that took ₹11.8 crore from one Bengaluru engineer" is a different pitch from "AI security assistant").

### 7.3 Adjacent state of the art (academic + open source)

- **On-device RAG on Snapdragon:** `FACT` arXiv:2606.11257 (§3.2) — the reference benchmark. Cite it.
- **Sustained-load edge LLM efficiency:** `FACT` arXiv:2603.23640, "LLM Inference at the Edge: Mobile, NPU, and GPU Performance Efficiency Trade-offs Under Sustained Load."
- **Screen/GUI understanding:** `FACT` OmniParser & OmniParser V2 (Microsoft Research, arXiv:2408.00203).
- **Computer-use agent accessibility gap:** `FACT` arXiv:2602.09310, "A11y-CUA Dataset."
- **Prompt sanitisation / redaction:** `FACT` Casper (arXiv:2408.07004), SurrogateShield (arXiv:2606.29567), LLM-Redactor (arXiv:2604.12064), RedactionBench (arXiv:2606.18782).
- **Audio deepfake detection:** `FACT` A May 2026 neutral benchmark compared 8 systems (4 commercial APIs, 4 open-source) and found production detection requires real-time inference below RTF 1.0 and sub-second latency; **"a detector trained on 2019 attacks does not generalize to 2026 attacks."** ([Resemble AI benchmark](https://www.resemble.ai/resources/audio-deepfake-detection-benchmark-results-how-8-systems-performed-in-2026)) `ANALYSIS` Important caution for §9 S1: do **not** build your scam detector primarily on synthetic-voice detection. Detect the *social-engineering script*, which does not go stale the way spoofing artefacts do.
- **Local-first meeting tools:** `FACT` Meetily (MIT, fully local, on-device diarization), LUCI, OpenWhispr, BB Recorder.
- **NPU-first local LLM runtime:** `FACT` `npurun` — "NPU-first local LLM runtime for Snapdragon X Elite (Windows on ARM)," reporting ≥3× a CPU baseline. ([GitHub](https://github.com/bpbonker/npurun))
- **Indic models:** `FACT` AI4Bharat IndicConformer (30M-param conformer ASR, 22 languages, ONNX INT8 conversions for 8 languages exist), IndicTrans2 (all 22 scheduled languages, distilled 200M variants published on AIKosh). ([AI4Bharat](https://ai4bharat.iitm.ac.in/areas/asr), [HF ONNX conversion](https://huggingface.co/meetsync/indic-conformer-onnx-sherpa))

`ANALYSIS` On honesty of claims: for every shortlisted idea below I have found *something* adjacent. **Nothing here is unprecedented.** The correct language for the submission is "differentiation opportunity" — specifically, the combination of (multimodal) × (continuous/local) × (Snapdragon NPU-measured) is where the genuine whitespace is, not in any single capability.

---

## 8. Snapdragon-Specific Opportunity Analysis (Part F)

### 8.1 The test

`ANALYSIS` For each idea, I wrote the honest "Without Snapdragon" case. If the answer was "it works basically the same," the idea is disqualified regardless of how good the problem is. This is the filter most submissions will fail.

### 8.2 Without vs With

| Idea | Without Snapdragon (any ordinary laptop / cloud) | With Snapdragon | Verdict |
|---|---|---|---|
| **S1 Scam shield** | Continuous ASR + classification on CPU costs 30–40 W, halves battery, and thermally throttles within an hour — so it gets used "only when suspicious," i.e. never at the moment it matters. Cloud version requires streaming private call audio to a server: unacceptable and probably unlawful. | `FACT` NPU handles this class at ~5–10 W with 5–10× better TOPS/W; prefill-dominated classification is the 18× case; 315 J vs 1,251 J per query. Always-on becomes free, so protection is present *before* you suspect anything. | **Material. Keep.** |
| **S2 Indic doc accessibility** | Cloud OCR works, but personal/medical/legal documents can't be uploaded, and rural users have no reliable link. CPU OCR of a 300-page book takes hours on battery. | `FACT` 12.3× lower indexing energy; batch-encode an entire textbook offline on battery. | **Material. Keep.** |
| **S3 AI airlock** | Cloud redaction is *logically self-defeating*. CPU-based scanning adds visible latency to every paste and cannot cover screenshots in real time. | Sub-100 ms multimodal scanning on every outbound payload, continuously, free. | **Material — the strongest structural case in the report. Keep.** |
| **S4 Hinglish captioning** | Running two ASR models concurrently on CPU is not real-time. Cloud can do it but drops offline and leaks classroom/meeting audio. | Unified 224 GB/s memory + NPU makes concurrent dual-model streaming ASR viable on battery. | **Material. Keep.** |
| **S5 Screen-understanding coach** | Every-frame UI parsing on CPU is impossible; cloud requires uploading the user's screen continuously. | NPU vision encoder per frame-change; screen never leaves. | **Material. Keep (but FEA-limited).** |
| **S6 Confidential research workbench** | Actually runs fine on a CPU laptop overnight. | Faster, cooler, quieter — but not *different*. | **Weak Snapdragon case.** Only survives if reframed around bulk multimodal indexing. |
| Air-gapped code triage | Runs on any air-gapped x86 box with a GPU, often better. | Marginal. | **Reject — Snapdragon adds nothing.** |
| Offline finance/statement ingestion | A few PDFs a month; CPU is fine. | Nothing changes. | **Reject.** |
| Local viva practice | One LLM call per answer. | Nothing changes. | **Reject.** |
| Image generation studio | Discrete NVIDIA GPU beats Snapdragon decisively. | Actively *worse* than alternatives. | **Reject — Snapdragon is a liability here.** |

`ANALYSIS` The pattern is unmistakable: **Snapdragon's advantage is duty cycle, not peak capability.** The question that separates a winning idea from a losing one is not "can the NPU do this?" but **"does this need to run all the time, or over a lot of data, on battery, on data that cannot leave?"** Every surviving idea answers yes.

---

## 9. Shortlisted Opportunities (Part I)

Nine concepts, ordered by my assessment of expected value given the 8-day constraint.

---

### S1 — "Perception Firewall": live social-engineering & coercion detection

**Problem.** Scam victims are not stupid; they are *steered*. A caller establishes authority ("CBI, your Aadhaar is linked to a money-laundering case"), creates urgency, isolates the victim ("do not disconnect, do not tell your family"), then induces a remote-access install and a transfer. Nothing in the victim's computing environment notices any of this.

**User.** Anyone taking calls on or near a PC, with acute value for elderly users, first-time internet users, and people handling payments. Secondary: an SME finance clerk who receives a "CEO" voice note.

**Current solution.** Caller-reputation blocklists (Truecaller), bank SMS warnings, awareness campaigns, and post-hoc cybercrime complaints. All are either metadata-only or after the money is gone.

**Gap.** No mainstream tool looks at the *content and choreography* of an in-progress manipulation. Blocklists fail against fresh numbers and spoofed IDs. And the one thing that could work — understanding what is being said — is precisely the thing you cannot outsource to a cloud service.

**AI intervention.** Continuous streaming ASR of the call (user-initiated), feeding a rolling classifier that scores a short taxonomy of manipulation primitives: authority impersonation, legal threat, urgency/time pressure, isolation instruction, secrecy demand, remote-access request, payment redirection, verification refusal. Fuse with **screen state**: is a remote-desktop tool being installed? Is a banking page open? Is a screen share active? Raise a calm, non-accusatory interstitial: *"This call matches 5 of 8 patterns used in digital-arrest scams. Real police do not arrest people over video calls. Consider hanging up and calling 1930."*

**Local AI advantage.** Absolute. Streaming a citizen's live call audio to a server to protect them from fraud is a worse privacy violation than the fraud. This idea *requires* local inference to be ethically coherent — which is a far stronger claim than "we chose local for privacy."

**Snapdragon advantage.** See §8.2. Duty cycle is the whole product: a detector you must remember to switch on is useless, because by the time you are suspicious you have already been socially engineered. `FACT` NPU at 5–10 W and 5–10× TOPS/W vs GPU makes always-on viable; `FACT` prefill-dominated classification is the 18.1× regime; `FACT` 315 J vs 1,251 J per query.

**Technical implementation.** Whisper (AI Hub, `precompiled_qnn_onnx`, encoder/decoder split) or IndicConformer for Hindi/Hinglish → rolling 20–30 s transcript window → Qwen3-1.7B via GenieX (`geniex_qairt`) doing structured classification with a constrained JSON output (short generation = plays to NPU strengths) → optional EasyOCR/Qwen3-VL-4B on periodic screen captures for the remote-access/banking-page signal → a WinUI overlay. All orchestrated through GenieX's OpenAI-compatible local server so the app code stays simple.

**Innovation.** Detecting the *script* rather than the *speaker*. `FACT` This matters because synthetic-voice detectors go stale — "a detector trained on 2019 attacks does not generalize to 2026 attacks" — whereas the social-engineering playbook (authority → urgency → isolation → payment) has been stable for decades. That argument alone will differentiate you from every deepfake-detection submission.

**MVP (8 days).** Live mic capture → streaming Whisper on NPU → sliding-window classifier over the 8 primitives → risk meter + interstitial. Screen signal as a stretch goal. Ship with a scripted scam audio file so the demo is reproducible, *plus* a live mic mode.

**Demo (see §10).** Devastating if executed.

**Risk.** (a) False positives on legitimate calls from banks — mitigate by framing output as "patterns matched," never "this is a scam." (b) Ethics/optics of an always-listening tool — mitigate with explicit per-call activation, a visible indicator, and a "nothing leaves this device, ever" architecture slide. (c) You have no scam-call dataset — mitigate by using *published, publicly reported* scam transcripts and clearly labelling synthesised demo audio as reconstruction. **Do not fabricate a fake accuracy number.** (d) Hinglish ASR quality (§6.3 #4).

**Expansion.** Enterprise vishing protection; bank/telecom partnership; an SDK for softphones; India's 1930 helpline integration.

---

### S2 — "Paath": Indic document accessibility engine

**Problem.** `FACT` Image-only PDFs, slide decks and image-only newspapers are unreadable to screen readers; NVDA/JAWS Indic TTS and OCR accuracy is inconsistent; students have changed university courses because they could not read PDFs.

**User.** Blind and low-vision students and professionals reading Hindi/Tamil/Bengali/Marathi material; secondarily anyone with a pile of bad scans.

**Current solution.** Sighted assistance, paid OCR services, abandoning the document.

**Gap.** English-first tooling; poor Indic script handling; cloud OCR unusable for personal/medical/legal documents and unavailable offline.

**AI intervention.** A pipeline, not a feature: enhance (super-resolution/denoise) → segment layout → reconstruct reading order → Indic OCR → describe figures and tables via a VLM → emit a *structured, navigable* document (headings, tables, alt text) → high-quality Indic TTS with heading/table navigation.

**Local advantage.** Personal documents; offline dependability; zero per-page cost so a whole textbook is free to process.

**Snapdragon advantage.** `FACT` 12.3× lower indexing energy makes "process this 300-page book on battery while you sleep" real.

**Technical implementation.** Real-ESRGAN/QuickSRNet → DDRNet or Mask2Former for layout → EasyOCR (plus Windows AI OCR API as a fallback/comparison) → Qwen3-VL-4B for figure/table description → MeloTTS/PiperTTS or an Indic TTS. All available via AI Hub except the Indic TTS.

**Innovation.** Reading *order and structure*, not just text — the actual difference between "OCR output" and "a readable document." Plus figure description, which no screen reader does.

**MVP.** One language (Hindi), one document type (scanned textbook page), end-to-end, with a side-by-side "NVDA output vs ours" comparison.

**Risk.** **EchoSight is a direct competitor in this contest.** Indic OCR may underperform on real scans. Mitigate by going narrow and deep (reading order + figure description) rather than broad.

**Expansion.** NVDA plug-in; DAISY/EPUB export; partnership with Samarthanam or the Blind People's Association.

---

### S3 — "Airlock": local multimodal privacy gateway for cloud AI

**Problem.** People paste customer records, patient details, contract text, API keys and proprietary code into cloud AI tools dozens of times a day. Policy does not stop it. Blocking the tools does not stop it either — it just moves it to personal accounts.

**User.** Developers, lawyers, healthcare admin, HR, finance, consultants — anyone under NDA, DPDP Act, HIPAA, SOC 2 or ISO 27001 obligations who nonetheless wants to use ChatGPT/Claude/Gemini.

**Current solution.** `FACT` A real but immature category: llm-redact-proxy, PII Shield, SurrogateShield, LLM-Redactor, Casper. Mostly regex + a local text model, text-only, on developer machines.

**Gap.** Three concrete ones. (1) **Text-only** — nobody handles screenshots, yet pasting a screenshot into a cloud VLM is now routine. (2) **Blunt masking degrades answers** — `[REDACTED]` destroys the context the model needed. (3) **CPU-bound** — scanning every paste adds perceptible lag, so people disable it.

**AI intervention.** A local gateway that intercepts outbound AI traffic (proxy + clipboard + screenshot hook), runs NER + a small LLM to identify sensitive spans *in context*, substitutes **stable, type-consistent surrogates** ("Priya Sharma" → "Anita Rao", not `[NAME]`), forwards only sanitised content, and **restores the real values in the response** before you see it. For images: OCR + VLM → SAM-masked visual redaction before upload.

**Local advantage.** Structural and absolute — a cloud-based redaction service must first receive your unredacted data. There is no cloud version of this product. `ANALYSIS` This is the single cleanest "local is mandatory" argument in the entire report.

**Snapdragon advantage.** Every paste, every screenshot, every prompt, scanned with a <100 ms budget, all day, on battery. `FACT` This is the definitional NPU duty-cycle workload; on CPU it is a visible tax users will switch off.

**Technical implementation.** ONNX token-classification NER (NPU) for the fast path → Qwen3-0.6B/1.7B via GenieX for ambiguous spans → EasyOCR + Qwen3-VL-4B + SAM3 for the image path → a local HTTP proxy with an OpenAI-compatible surface (GenieX already provides one to model against) → reversible surrogate map held only in memory.

**Innovation.** Multimodal (screenshots) + surrogate substitution that preserves answer quality + NPU-speed so it is always on. `ANALYSIS` I could not find this combination shipped anywhere — but state it as a differentiation opportunity, never as "nobody has built this."

**MVP.** Clipboard + proxy interception for text, with surrogate substitution and response restoration; screenshot redaction as the second slice. A live "leak counter" showing what was caught today.

**Risk.** Recall failure is catastrophic by nature — one missed Aadhaar number is a product failure, not a bug. Mitigate with a fail-closed design and honest precision/recall reporting on a public PII benchmark (RedactionBench exists). Also: intercepting traffic on Windows is fiddly; prefer an explicit proxy endpoint over TLS interception.

**Expansion.** Enterprise DLP; browser extension; MCP-layer integration; a compliance audit log.

---

### S4 — "Dobhashi": code-switched Hinglish live captioning
Covered in §6.3 #4. **Strongest honest technical thesis** (parallel dual-ASR fusion on NPU), **weakest honest outcome guarantee** (the fusion may not beat baseline, and you must report that truthfully). Choose only if you are comfortable presenting a negative result well.

### S5 — Screen-understanding coach for low-digital-literacy users
Covered in §6.3 #6. Highest ceiling, highest execution risk (FEA 2). If you had 6 weeks this would be my recommendation.

### S6 — Confidential interview/qualitative-research workbench
Covered in §6.3 #11. Excellent local argument, mediocre demo. Best fallback if S1 proves too risky.

### S7 — Multimodal lecture-archive search
Covered in §6.3 #10. Best pure showcase of the 12.3× indexing-energy advantage; must be framed around video+slide+speech alignment to avoid colliding with Hyperlink and Recall.

### S8 — Semantic screen recorder → reproducible bug report
Covered in §6.3 #20. Genuinely differentiated, narrow audience, weak on the Accessibility criterion.

### S9 — Offline Indic voice→form intake
Covered in §6.3 #5. Best social impact of the nine; weakest "why a Snapdragon *laptop*" answer. Only pursue with an honest device story (e.g. a PHC/clinic front-desk laptop, not a field phone).

---

## 10. WOW Demo Analysis (Part J)

`ANALYSIS` Rules I applied: no chatbot. The judge must understand the value before you finish the sentence. Something must be *visibly impossible* without local AI. And there must be a moment where a **number on screen** proves the Snapdragon claim.

### 10.1 S1 — Perception Firewall (the strongest demo in this report)

> **0–10 s.** Screen shows an ordinary laptop desktop, Wi-Fi icon visible. Presenter clicks "Airplane mode." **Network off, on camera.** A small badge in the corner reads `Local · NPU`.
>
> **10–30 s.** A phone on speaker plays a scam call: *"This is Inspector Sharma, CBI. Your Aadhaar is linked to a money-laundering case. Do not disconnect this call. Do not inform your family. You are under digital arrest."* As it plays, a panel fills in **in real time** — `Authority impersonation ✓` … `Legal threat ✓` … `Isolation instruction ✓` — each with the timestamp and the exact phrase that triggered it. The risk meter climbs.
>
> **30–60 s.** The caller says "install AnyDesk so I can verify your account." The presenter actually opens a remote-desktop installer. A **second, screen-side signal fires** and the meter jumps to red. A full-screen calm interstitial appears: *"5 of 8 digital-arrest patterns detected. Real police do not arrest people over calls. Hang up and dial 1930."*
>
> **60–90 s.** Cut to a benchmark panel: ASR + classification latency **measured on a real Snapdragon X Elite via AI Hub Workbench**, side by side with the CPU-only figure, plus a power estimate and "hours of continuous protection per charge." Closing line: *"This ran with the network off. The call never left the laptop. It can run like this all day — which is the only way it protects anyone, because by the time you're suspicious, it's already too late."*

`ANALYSIS` Why this works: the problem is visceral and locally famous; the AI output is *legible* (named patterns with evidence, not a black-box score); airplane mode is an unfakeable proof of on-device execution; the multimodal fusion moment at 30–60 s is genuinely surprising; and it ends on a measured number, which is exactly what criterion #1 rewards.

### 10.2 S3 — Airlock

> **0–10 s.** Presenter opens ChatGPT in a browser and pastes a realistic customer support email containing a name, phone number, Aadhaar-style ID, and an API key.
>
> **10–30 s.** Before it sends, a slim overlay shows the outbound payload **diffed**: real values on the left struck through, surrogates on the right. Counter: "4 sensitive spans replaced · 0 left this device." The prompt goes out sanitised.
>
> **30–60 s.** The cloud reply comes back referring to "Anita Rao." The overlay **restores the real name** in the displayed answer. The point lands without narration: *full answer quality, zero leakage.*
>
> **60–90 s.** The presenter screenshots a spreadsheet of patient records and pastes the image. The screenshot is **visually redacted in place** before upload — black boxes appearing over exactly the right cells, live. Then the numbers: per-paste scan latency on NPU vs CPU, and "scans per hour at X watts."

`ANALYSIS` The screenshot-redaction moment is the "I didn't know that was possible" beat. The restoration step at 30–60 s pre-empts the obvious objection about degraded answers.

### 10.3 S2 — Paath

> **0–10 s.** A visibly bad scan of a Hindi textbook page — skewed, two-column, with a diagram — is dropped onto the app. Network off.
>
> **10–30 s.** Overlays animate: deskew, column detection, reading-order arrows numbering the blocks 1→7, diagram boxed and labelled "figure."
>
> **30–60 s.** Audio plays: correct Hindi, correct reading order, and when it reaches the diagram it *describes* it. Split-screen: NVDA reading the same file produces garbled interleaved columns.
>
> **60–90 s.** "Process entire book (312 pages)" → progress bar completes in seconds-per-page, with NPU vs CPU time and energy shown, and battery drain measured.

### 10.4 S5 — Screen coach

> **0–15 s.** A real, ugly government portal is open. On-screen prompt in Hindi: "मुझे आय प्रमाण पत्र चाहिए" (I need an income certificate).
> **15–45 s.** A translucent arrow lands precisely on the right menu item — on a page with no API, no accessibility tree cooperation, purely from pixels. Step 1 of 6 appears in Hindi.
> **45–75 s.** The user clicks; the coach re-grounds on the new page and points again. It *never clicks for them.*
> **75–90 s.** Per-frame screen-parse latency on NPU, and the line: "Your screen never left this machine."

### 10.5 Demos I considered and rejected

`ANALYSIS` "Ask the local LLM a question and watch it stream" — tests nothing, shows the NPU's *weakest* axis (decode, 1.7×), and will be in thousands of submissions. "Generate an image locally" — a judge with a phone can do better in the same 30 seconds. "Summarise this PDF" — the judge's own laptop already does this. Any demo whose punchline is text appearing is a wasted 90 seconds.

---

## 11. Technical Feasibility (Part M §11)

### 11.1 Recommended stack

| Layer | Choice | Why |
|---|---|---|
| Runtime (LLM/VLM) | **GenieX** with `geniex_qairt` backend | `FACT` NPU-only, compiled via Workbench, highest on-device performance; OpenAI-compatible local server makes app code portable |
| Runtime (CV/ASR) | **ONNX Runtime + QNN EP**, models from AI Hub as `precompiled_qnn_onnx` | `FACT` The documented path for custom ONNX on Snapdragon X NPU on Windows |
| Model source | **Qualcomm AI Hub Models** (`pip install qai_hub_models`) | On-brand, pre-optimised, exportable |
| Profiling | **AI Hub Workbench** cloud devices | `FACT` Free; real Snapdragon X Elite / X2 hardware; produces the evidence table |
| UI | **WinUI 3 / WPF (C#)** or Python backend + local web UI | `ANALYSIS` Avoid Electron — ARM64 native-module and arch-selection pitfalls are real and you cannot afford to debug them on deadline night |
| Packaging | ARM64-native build + MSIX or a simple installer | Directly serves the "Deployment" criterion |

### 11.2 The 8-day critical path (`ANALYSIS`)

1. **Day 0 (today):** Register on Unstop and **open the submission form** to learn the exact required fields. Create a Qualcomm ID and an AI Hub API token.
2. **Day 1:** Pick the concept. Export your 2–3 chosen models via `qai_hub_models`, compile for `Snapdragon X Elite` and an X2 target, submit profile jobs. **Get the numbers early — they are your differentiator and your fallback.** Even if the app slips, a rigorous benchmark + architecture document is a respectable submission.
3. **Days 2–5:** Build the single vertical slice. Nothing else.
4. **Day 6:** Package an ARM64 build; write the README (architecture diagram, model/runtime table, benchmark table, limitations section).
5. **Day 7:** Record the 60–90 s demo. Record it twice.
6. **Day 8 (29 Sep):** Submit. **Do not submit on the 30th** — the submission is immutable and the platform will be under load.

### 11.3 Feasibility risks, ranked

| Risk | Severity | Mitigation |
|---|---|---|
| `FACT` ARM64 Python unsupported for AI Hub tooling; ONNX quantisation is x86_64-only | High | Do all export/quantisation on an x64 machine (which is likely what you have anyway); keep the target artefacts pre-compiled |
| No Snapdragon hardware to test on | High | Workbench cloud devices give real inference + latency; be explicit and honest in the README that end-to-end app testing was done on x64 with model-level validation on Snapdragon |
| `FACT` NPU LLM ceiling ~4B params | Medium | Design for short structured outputs; use Qwen3-1.7B/4B, not an 8B+ model |
| `FACT` Mainstream runtimes (Ollama/llama.cpp/LM Studio) are CPU-only on ARM | High (credibility) | Never demo through them; use GenieX/QNN or explicitly label a CPU fallback as such |
| Streaming ASR latency/chunking complexity | Medium | Start from the official Whisper Windows sample in `ai-hub-apps` |
| Electron/native-module ARM64 breakage | Medium | Avoid Electron |
| Demo fails live | Medium | Pre-record; also ship a deterministic scripted input file |

---

## 12. Competitive Differentiation (Part M §12)

`ANALYSIS` Given 10,333 individual entrants, your edge will come from four things, in this order:

1. **Measured Snapdragon numbers.** A table of real AI Hub Workbench latency/memory figures across NPU vs CPU, with the device names printed. Nearly free to obtain; nearly nobody will.
2. **Correct architectural reasoning, stated out loud.** "We route the encoder to the NPU and deliberately avoid the Adreno GPU, because on this class of part the iGPU measured *slower than CPU* and 6.5× less efficient" — with a citation. This signals you understand the silicon rather than the slogan.
3. **A problem framing so specific it cannot be confused with another submission.** Not "AI for safety" but "the eight-step script used in the digital-arrest scam that cost one Bengaluru engineer ₹11.8 crore."
4. **Intellectual honesty.** A "Limitations and what I could not verify" section. `ANALYSIS` Counterintuitively this *raises* scores with engineer-judges, because it is the strongest available signal that the rest of your claims are real. Everyone else's deck will claim 100%.

**Language discipline:** write "differentiation opportunity," "I could not find an existing implementation that combines X, Y and Z," and "to the best of my research." Never "the world's first" or "nobody has built this." A judge who knows of one counterexample will discount everything else you wrote.

---

## 13. Major Risks & Red-Flag Ideas (Parts K & M §13)

### 13.1 Ideas that look impressive and should be avoided

| Red flag | Why it is weak |
|---|---|
| **Generic AI chatbot / "assistant"** | `FACT` Qualcomm ships ChatApp and GenieX Chat as *samples*. You would submit the tutorial. Also exercises the NPU's weakest axis (decode, 1.7×). |
| **Generic PDF summariser** | Windows AI APIs do summarisation natively; Hyperlink does cited document Q&A on the NPU. Zero differentiation. |
| **Generic note-taking / meeting app** | `FACT` Meetily, LUCI, OpenWhispr already do fully local transcription + on-device diarization, free and open source. You cannot beat them in 8 days. |
| **Generic local image generator** | Official Stable Diffusion Windows sample exists; a discrete NVIDIA GPU crushes Snapdragon here — the hardware argument runs *against* you. |
| **Thin wrapper around a cloud API** | Directly contradicts the premise of the challenge. Instantly disqualifying in substance. |
| **Anything cloud-dependent at the core** | Same. If your demo breaks in airplane mode, you have no Snapdragon story. |
| **"Runs on Snapdragon" with no NPU workload** | `ANALYSIS` The most common failure. If the only compute is one LLM call per user action, an Intel laptop performs identically and the entire premise collapses under one question from a judge. |
| **Ollama/LM Studio-based "on-device AI"** | `FACT` These are **CPU-only on ARM**. You will have demonstrated that you did not use Qualcomm's hardware, to Qualcomm. |
| **Requires training a model or collecting a dataset** | Infeasible in 8 days. `FACT` See SetuAI's honest "9-sign, rule-based" scope as the predictable outcome. |
| **Requires proprietary data** (medical imaging, factory defects, bank transactions) | You cannot get it legally in 8 days; a mocked demo reads as fake. |
| **Recall / Click to Do / Live Captions / Studio Effects clones** | `FACT` Shipped Windows features on the same hardware. |
| **"Chat with your files"** | `FACT` Shipped by Qualcomm itself (Hyperlink). |
| **Anything needing kernel/driver access or anti-cheat-adjacent hooks** | `FACT` The weakest area of Windows-on-ARM compatibility. |
| **Platform-scale ideas** ("an OS-level AI layer", "a marketplace") | Too large for the timeline; will present as vapour. |
| **Unfalsifiable accuracy claims** | Engineer-judges probe these first. Report real numbers or report none. |

### 13.2 Risks that apply regardless of idea

- **Deadline (30 Sep).** The dominant risk. Everything above is subordinate to it.
- **Immutable one-shot submission.** Dry-run the whole package by Day 6.
- **Public, non-confidential submissions.** Do not include anything you want to keep.
- **Sole-ownership requirement.** No shared/team IP; verify every model licence.
- **No Snapdragon device.** Manageable via Workbench, but be transparent about what you did and did not test on-device. An honest note costs you far less than an inflated claim that a judge catches.
- **The privacy-claim commodity trap.** "It's private because it's local" is worth ~0 points when thousands of submissions say it. Only a *specific prohibited dataset* makes it worth points.
- **Over-scoping.** One vertical slice, finished, beats four features, half-working. The demo is 90 seconds; you cannot show four features anyway.

---

## 14. Recommended Research Directions — what to resolve before choosing (Part M §14)

`ANALYSIS` I am deliberately not selecting an idea. Five things should be resolved first, in this order, and four of them take under two hours:

1. **Open the Unstop submission form (today, ~15 min).** Everything downstream depends on whether it wants a deck, a video, a repo, or a 500-word abstract. The one-shot rule makes this non-negotiable.
2. **Run one AI Hub Workbench profile job end to end (~2 h).** Export Whisper-small and Qwen3-1.7B, compile for Snapdragon X Elite, profile. This simultaneously (a) validates that the toolchain works on your machine, (b) produces your differentiating evidence, and (c) tells you your real latency budget — which determines whether S1's always-on premise actually holds. **If this fails, every idea in this report changes.**
3. **Sanity-check Indic ASR quality (~2 h) if S1, S2, S4 or S9 is in play.** Run Whisper and IndicConformer on 10 minutes of real Hinglish audio and measure. `FACT` The literature predicts 14–16% WER for global models on code-mixed telephony audio. If your measured numbers are much worse, S4 dies and S1 must be demoed in English.
4. **Decide your honesty posture on hardware.** Whether you claim "developed on x64, model-level validated on Snapdragon via AI Hub" or attempt to borrow/rent a Snapdragon device changes your README and your risk profile. `ANALYSIS` I strongly recommend the transparent version.
5. **Then choose between S1 and S3.** My reading: **S1 has the better story and the better demo; S3 has the better structural argument and lower execution risk.** S1 wins on Application Use Case & Innovation; S3 wins on Technical Implementation, which is the higher-priority criterion. That is a genuine trade-off, and it should be made after step 2 tells you what latency you actually have.

**What I could not verify and would want to know:** criterion weights; whether a runnable prototype is required or a proposal suffices; the judging panel's technical depth; whether any Snapdragon hardware access is offered to participants; and the exact intake-form structure.

---

## 15. Source Bibliography (Part L)

**Competition (primary)**
| Source | Org | Date | URL | Supports |
|---|---|---|---|---|
| Snapdragon® AI Lab Build & Present Challenge listing | Qualcomm / Unstop | read 22 Sep 2026 | [link](https://unstop.com/competitions/crp-snapdragon-ai-lab-build-present-challenge-qualcomm-1748893) | All rules, dates, eligibility, criteria, prizes, IP, tie-break |
| Snapdragon AI Lab programme page | Qualcomm | read 22 Sep 2026 | [link](https://www.qualcomm.com/snapdragon/ai-lab) | Programme structure, internship eligibility (CGPA 7.5+, CS/ECE), Arduino UNO Q tie-in |

**Qualcomm platform (primary)**
| Source | Org | URL | Supports |
|---|---|---|---|
| Qualcomm AI Hub | Qualcomm | [link](https://aihub.qualcomm.com/) | Four surfaces; 300+ models; runtimes LiteRT/ONNX/QAIRT; workflow |
| AI Hub Compute model catalogue | Qualcomm | [link](https://aihub.qualcomm.com/compute/models) | 221 models/501 variants; Qwen3, Gemma-4, Qwen3-VL, GPT-OSS-20B on compute tier |
| AI Hub Workbench docs | Qualcomm | [link](https://workbench.aihub.qualcomm.com/docs/hub/index.html) | Free; cloud device provisioning; profiling metrics |
| Workbench FAQ | Qualcomm | [link](https://workbench.aihub.qualcomm.com/docs/hub/faq.html) | Free-to-use; Qualcomm ID/token requirement |
| What is GenieX | Qualcomm | [link](https://geniex.aihub.qualcomm.com/en/get-started/what-is-geniex) | Windows ARM64/Android/Linux; NPU/GPU/CPU; LLM+VLM; OpenAI-compatible server; llama.cpp vs AI Engine Direct backends |
| GenieX developer preview | Qualcomm | Jun 2026 | [link](https://www.qualcomm.com/developer/blog/2026/06/geniex-developer-preview) | Launch, unified runtime |
| qualcomm/ai-hub-models | Qualcomm | [link](https://github.com/qualcomm/ai-hub-models) | Full model zoo by category; runtimes per OS |
| qualcomm/ai-hub-apps | Qualcomm | [link](https://github.com/quic/ai-hub-apps) | Windows samples: ChatApp, Whisper, Stable Diffusion, SAM3, GenieX Chat |
| Deploy AI Models on Snapdragon X Elite with AI Hub | Qualcomm | May 2025 | [link](https://www.qualcomm.com/developer/blog/2025/05/deploy-ai-models-on-snapdragon-x-elite-with-qualcomm-ai-hub) | QNN EP on Windows; `hub.Device("Snapdragon X Elite CRD")` |
| AI Hub — Windows on Snapdragon docs | Qualcomm | [link](https://docs.qualcomm.com/bundle/publicresource/topics/80-62010-1/ai-hub.html) | Windows ARM64 deployment guidance |
| ai-hub-models issue #258 | Qualcomm / community | [link](https://github.com/qualcomm/ai-hub-models/issues/258) | **x64-only Python; ARM64 quantisation limitation** |
| Snapdragon X2 Elite product brief | Qualcomm | [link](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-X2-Elite-Product-Brief.pdf) | Official X2 Elite specs (binary PDF; specs corroborated below) |
| Qualcomm AI Hub GenAI / Nexa | Qualcomm | [link](https://aihub.qualcomm.com/genai) | **Nexa AI now part of Qualcomm AI Hub** |

**Silicon**
| Source | Org | URL | Supports |
|---|---|---|---|
| Inside Snapdragon X2 Elite architecture deep dive | HotHardware | [link](https://hothardware.com/reviews/qualcomm-snapdragon-x2-elite-architecture-deep-dive) | 3rd-gen Oryon, 18 cores, 5.0 GHz, **224 GB/s LPDDR5X**, 128 GB on-package, NPU6, eNPUs, TSMC N3 |
| HP OmniBook Ultra 14 with X2 | Tom's Hardware | [link](https://www.tomshardware.com/laptops/hps-new-omnibook-ultra-14-gets-panther-lake-and-snapdragon-x2-options-inside-exclusive-variant-of-qualcomm-chip-has-85-tops) | X2 Plus 80 TOPS; HP-exclusive 85 TOPS X2 Elite |
| Snapdragon X series Copilot+ launch | Tom's Hardware | [link](https://www.tomshardware.com/laptops/snapdragon-elite-x-windows-ai-pcs-get-official-starting-at-dollar1099-acer-dell-hp-and-lenovo-are-all-onboard-with-some-models-promising-multi-day-battery-life) | 45 TOPS across X/X Plus/X Elite; Copilot+ 40 TOPS floor |
| X2 Elite review / sustained TOPS | tech-insider | [link](https://tech-insider.org/qualcomm-snapdragon-x2-elite-review-benchmarks-2026/) | Sustained throughput 40–56 TOPS vs 80 peak |

**Benchmarks & research**
| Source | Authors | Date | URL | Supports |
|---|---|---|---|---|
| Energy-Efficient On-Device RAG on a Mobile NPU (arXiv:2606.11257) | Cheng (Stanford), Lai (U. Rochester) | 9 Jun 2026 | [link](https://arxiv.org/html/2606.11257v1) | **The core prefill/decode/energy numbers; iGPU worst backend; quality parity** |
| LLM Inference at the Edge under Sustained Load (arXiv:2603.23640) | — | 2026 | [link](https://arxiv.org/pdf/2603.23640) | Sustained-load NPU/GPU efficiency trade-offs |
| OmniParser for Pure Vision Based GUI Agent (arXiv:2408.00203) | Microsoft Research | 2024–25 (V2) | [link](https://arxiv.org/abs/2408.00203) | Screen parsing SOTA; WindowsAgentArena |
| A11y-CUA Dataset (arXiv:2602.09310) | — | 2026 | [link](https://arxiv.org/pdf/2602.09310) | Accessibility gap in computer-use agents |
| SurrogateShield (arXiv:2606.29567) | — | 2026 | [link](https://arxiv.org/pdf/2606.29567) | Surrogate substitution preserves utility vs redaction |
| LLM-Redactor (arXiv:2604.12064) / Casper (2408.07004) / RedactionBench (2606.18782) | — | 2024–26 | [1](https://arxiv.org/pdf/2604.12064) [2](https://arxiv.org/pdf/2408.07004) [3](https://arxiv.org/pdf/2606.18782) | Prior art + a benchmark for S3 |
| HiACC Hinglish code-switched corpus | — | 2025 | [link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12329218/) | >250M code-switchers; Whisper/Wav2Vec2 baselines |
| Adapting Whisper for Hindi-English code-mix | Biswas et al. | Interspeech 2025 | [link](https://www.isca-archive.org/interspeech_2025/biswas25_interspeech.pdf) | Code-switch adaptation methods |

**Ecosystem & competitive**
| Source | Org | URL | Supports |
|---|---|---|---|
| Choose your Windows AI solution | Microsoft Learn | [link](https://learn.microsoft.com/en-us/windows/ai/windows-ai-comparison) | Windows AI APIs (OCR, imaging, Phi Silica), Foundry Local |
| Copilot+ PCs for business | Microsoft | [link](https://www.microsoft.com/en-us/windows/business/devices/copilot-plus-pcs) | Recall, Click to Do, Live Captions translation, Studio Effects on NPU |
| QNN Execution Provider | ONNX Runtime | [link](https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html) | Custom ONNX → Snapdragon NPU path |
| Windows on ARM (Electron) | Electron | [link](https://www.electronjs.org/docs/latest/tutorial/windows-arm) | ARM64 native-module and arch-selection pitfalls |
| Windows on ARM compatibility tier list 2026 | WiTechpedia | [link](https://www.witechpedia.com/windows-on-arm-app-compatibility/) | >93% native app coverage; remaining kernel/anti-cheat gaps |
| NPU vs discrete GPU for local LLMs 2026 | runaihome | [link](https://runaihome.com/blog/npu-vs-gpu-local-llm-2026/) | **Ollama/llama.cpp/LM Studio are CPU-only on ARM; ~4B NPU ceiling** |
| npurun | bpbonker | [link](https://github.com/bpbonker/npurun) | NPU-first local LLM runtime for Snapdragon X Elite |
| Hyperlink by Nexa AI | Nexa | [link](https://nexa.ai/blogs/hyperlink-v1) | On-device agentic RAG over local files; NPU-accelerated |
| Meetily | Meetily | [link](https://meetily.ai/) | Fully local meeting transcription + diarization, MIT |
| Granola alternatives / local-first comparison | BuildBetter | [link](https://blog.buildbetter.ai/best-granola-alternatives-private-meeting-notes-2026/) | LUCI, OpenWhispr, BB Recorder on-device diarization |
| Enterprise AI code assistants for air-gapped environments | IntuitionLabs | [link](https://intuitionlabs.ai/articles/enterprise-ai-code-assistants-air-gapped-environments) | Tabnine, Tabby, Cody, Bodega air-gap category maturity |
| Build a local AI proxy to redact PII before LLMs | LogRocket | [link](https://blog.logrocket.com/build-local-ai-proxy-redact-pii-before-llms/) | Local redaction-proxy pattern |
| llm-redact-proxy | CupOfGeo | [link](https://github.com/CupOfGeo/llm-redact-proxy) | Existing local redaction proxy (regex + local model) |

**Problem evidence (India)**
| Source | URL | Supports |
|---|---|---|
| India Scams 2026 (MHA/I4C, RBI figures) | [link](https://scamwatchhq.com/india-scams-2026-digital-arrest-upi-fraud-epidemic/) | ₹22,495 cr cyber-fraud losses 2025; digital-arrest >₹4,000 cr 2022–mid-2026; RBI ₹48,021 cr FY26 (+46.4%) |
| AI voice deepfake fraud India 2026 | [link](https://caller.digital/blog/ai-voice-deepfake-fraud-caller-trust-india-2026) | 65% of Indian orgs hit by a deepfake-driven attack (Thales 2026) |
| Bengaluru engineer loses ₹11.8 cr | Deccan Herald | [link](https://www.deccanherald.com/india/karnataka/bengaluru/software-engineer-in-bengaluru-loses-rs-118-crore-to-digital-arrest-scam-3329400) | Individual-case severity |
| Fraunhofer real-time deepfake detector for video calls | Biometric Update, Aug 2026 | [link](https://www.biometricupdate.com/202608/fraunhofer-develops-real-time-deepfake-detector-for-video-calls) | **Prior art: local-on-laptop audio+video detection** |
| Audio deepfake detection benchmark 2026 | Resemble AI | [link](https://www.resemble.ai/resources/audio-deepfake-detection-benchmark-results-how-8-systems-performed-in-2026) | RTF<1.0 / sub-second requirements; detectors do not generalise across years |
| Bridging the digital divide for visually impaired South Asians | The Wire | [link](https://m.thewire.in/article/rights/bridging-the-digital-divide-for-visually-impaired-south-asians-language-technology-and-inclusion) | Indic screen-reader/OCR failures; course-abandonment impact |
| India's accessibility gap | Newslaundry | [link](https://www.newslaundry.com/2025/03/04/available-tech-affordability-drawbacks-all-you-need-to-know-about-indias-accessibility-gap) | Affordability + Indic script tooling gaps |
| Digital health competency framework for FLHWs (PMC13245931) | PMC | [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC13245931/) | 160,000+ ASHAs in UP serving ~232M |
| India's digital health push is overworking its front-line women | New Lines Magazine | [link](https://newlinesmag.com/reportage/indias-digital-health-push-is-overworking-its-front-line-women/) | Seven apps + WhatsApp + Sheets; parallel paper records; midnight documentation |
| Why speech recognition fails on Hinglish | Gnani.ai | [link](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr) | Utterance-level LID failure mode; 14–16% vs 11–14% WER |
| AI4Bharat ASR / IndicConformer | AI4Bharat, IIT Madras | [link](https://ai4bharat.iitm.ac.in/areas/asr) | 30M-param conformer, 22 languages |
| IndicConformer ONNX (sherpa) | Hugging Face | [link](https://huggingface.co/meetsync/indic-conformer-onnx-sherpa) | INT8 ONNX conversion, 8 languages |
| Digital India rural connectivity | IBEF | [link](https://www.ibef.org/blogs/impact-of-the-digital-india-programme-on-rural-connectivity) | Rural teledensity 60.74%; 554.41M rural subscribers (Apr 2026) |
| Digital learning in rural India | VidyaXR | [link](https://vidyaxr.in/blog/digital-learning-in-rural-india) | 29% rural-urban school connectivity gap; syllabus/language misalignment |

**Source-quality note.** `ANALYSIS` Tier 1 (Qualcomm/Microsoft/ONNX official docs, arXiv, PMC/Interspeech) carries the technical claims. Tier 2 (Tom's Hardware, HotHardware, Deccan Herald, The Wire, Newslaundry, Biometric Update, IBEF) carries hardware specs and reported events. A small number of Tier 3 commercial-blog sources (runaihome, tech-insider, witechpedia, scamwatchhq, gnani.ai, caller.digital) are used for figures I could not find first-party — **these are flagged here deliberately and any claim resting on them should be re-verified before it goes into a submission**, particularly the sustained-TOPS figure and the aggregate fraud-loss numbers.

---

## Appendix — Decision summary

| | S1 Perception Firewall | S3 Airlock | S2 Paath |
|---|---|---|---|
| Criterion 1 — Technical Implementation | Strong (multimodal streaming) | **Strongest** (continuous, measurable, clean architecture) | Strong (multi-stage pipeline) |
| Criterion 2 — Use Case & Innovation | **Strongest** (₹22,495 cr problem, visceral) | Strong (compliance-driven) | Strong (named harm, real users) |
| Criterion 3 — Deployment & Accessibility | Good | Good | **Strongest** (literally an accessibility product) |
| Criterion 4 — Presentation | **Strongest** (best 90-second demo) | Strong | Strong |
| Execution risk in 8 days | Medium-high (streaming ASR) | **Lowest** | Medium (Indic OCR quality) |
| Duplication risk among 10,333 entrants | Medium | **Lowest** | **Highest** (EchoSight exists) |

`ANALYSIS` No recommendation is final until §14 steps 1–3 are done. But if forced to bet today: **S3 for the highest floor, S1 for the highest ceiling.**
