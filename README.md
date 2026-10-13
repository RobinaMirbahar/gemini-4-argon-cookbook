# 🚀 Gemini 4 Argon Cookbook & Live 3D Starter Kit

[![Model: Gemini 4 Argon](https://img.shields.io/badge/Model-gemini--4--argon-4285F4?style=for-the-badge&logo=google)](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/)
[![Live 3D Demo](https://img.shields.io/badge/🎮_Live_3D_Studio-Play_in_Browser-00C853?style=for-the-badge)](https://robinamirbahar.github.io/gemini-4-argon-cookbook/)
[![Context & Output: 1M Unified](https://img.shields.io/badge/Tokens-1M_Input_%2F_1M_Output-34A853?style=for-the-badge)](https://aistudio.google.com/docs/long-decode)
[![SDK: google-genai >= 2.25.0](https://img.shields.io/badge/SDK-Interactions_API_v2-FBBC04?style=for-the-badge)](https://ai.google.dev/gemini-api/docs/interactions)

> **Built to solve your hardest problems.**
> Hands-on, production-ready examples for **[Gemini 4 Argon](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/)** using the **Gemini Interactions API** (`client.interactions.create`), featuring a **Live Interactive 3D & Image/Video-to-3D WebGL Studio**, **100% Pure-Python 3D Raytracer**, **1M unified output continuation protocol**, **first-class thought signatures**, and **autonomous code auditing**.

<p align="center">
  <a href="https://robinamirbahar.github.io/gemini-4-argon-cookbook/">
    <img src="./assets/argon_3d_live_animation.svg" alt="Gemini 4 Argon Live 3D Spatial Engine Animation" width="100%" />
  </a>
</p>

<p align="center">
  <a href="https://robinamirbahar.github.io/gemini-4-argon-cookbook/">
    <img src="https://img.shields.io/badge/▶_LAUNCH_LIVE_3D_WEBGL_STUDIO_(IMAGE_&_VIDEO_TO_3D)-1d4ed8?style=for-the-badge&logoColor=white" alt="Launch Live 3D Studio" />
  </a>
</p>

---

## 🌐 Live 3D & Multimodal Image/Video-to-3D Showcase

Gemini 4 Argon sets a new state of the art in **Embodied 3D Reasoning (87.0% on ERQA)** and **Long Video Understanding (91.7% on LVBench)**. This repository includes **three live 3D experiences**:

### 1. [Interactive 3D Spatial Studio (`index.html`)](https://robinamirbahar.github.io/gemini-4-argon-cookbook/)
- **Upload Any Image or Video $\rightarrow$ 3D Point-Cloud Mesh**: Drop any photo or video clip directly into the browser studio to reconstruct a live, depth-mapped 3D point cloud in Three.js.
- **Built-in 3D Video Recorder (`.webm`) & PNG Snapshot**: Record and download `.webm` 3D videos or `.png` renders directly from the WebGL canvas with one click.

### 2. Pure-Python Zero-Dependency 3D Ray-Tracing Engine ([`examples/04_vanilla_3d_raytracer.py`](./examples/04_vanilla_3d_raytracer.py))
Inspired by Google DeepMind's showcase where Argon wrote its own 3D ray-tracing engine in 100% pure Python with zero external libraries:

<p align="center">
  <img src="./assets/argon_sunlit_study.png" alt="Gemini 4 Argon Pure-Python 3D Ray-Traced Scene" width="85%" />
</p>

### 3. Official Gemini 4 Argon 3D & Video-to-Sim Showcases (Click to Watch)

| 🏎️ Image $\rightarrow$ Playable 3D Desk Racer | ☀️ 100% Pure-Python 3D Raytracer Video | 🤖 Video-to-Sim-to-Real Robotics (Apollo) |
| :---: | :---: | :---: |
| [![Desk Racer 3D](https://img.youtube.com/vi/zvoNbz_0q3k/hqdefault.jpg)](https://www.youtube.com/watch?v=zvoNbz_0q3k) | [![Python 3D Raytracer](https://img.youtube.com/vi/h2Dk1TlEX-U/hqdefault.jpg)](https://www.youtube.com/watch?v=h2Dk1TlEX-U) | [![Robotics Cornhole](https://img.youtube.com/vi/9PICEmtfpWU/hqdefault.jpg)](https://www.youtube.com/watch?v=9PICEmtfpWU) |
| *Turns desk photos into a Three.js game* | *Zero-dependency Python 3D raytracer* | *Learns 3D physics directly from raw video* |

---

## ✨ What's New in Gemini 4 Argon

| Capability | Gemini 4 Argon Highlight |
| :--- | :--- |
| **Unified Token Horizon** | **1,000,000 input / 1,000,000 output tokens** (15.6× increase from 64K) via the Long-Decode Continuation Protocol |
| **Software Engineering** | **77.9% on DeepSWE v1.1** (SOTA); untangled 6M+ lines of Chromium and sped up `google/adk-python` session prep by **40%** |
| **Enterprise & Finance** | **#1 on the Vals Index** across finance, legal, tax, and coding; **51.3% (#1) on AutomationBench** |
| **Spatial & 3D Reasoning** | **87% on Embodied Reasoning (ERQA)** and **91.7% on LVBench**; powers Video-to-Sim-to-Real robotics and 3D engines |
| **Safety & Alignment** | **0.7% attack success on Gray Swan IPI** (indirect prompt injection) and **2% shortcut rate** |
| **Introductory Pricing** | **\$2.00 / 1M input tokens** • **\$10.00 / 1M output tokens** • **95% off cached input tokens (\$0.10 / 1M)** |

---

## 📂 Repository Structure

| File | Description |
| :--- | :--- |
| [`index.html`](./index.html) | **Live 3D WebGL Spatial Studio** — Interactive Stellarator coils, sunlit ray-traced study, Image/Video-to-3D point cloud reconstructor, and `.webm` video recorder. |
| [`examples/01_long_decode_continuation.py`](./examples/01_long_decode_continuation.py) | **1M Output Long-Decode Continuation (Python)** — Unary & streaming continuation loop with `continuation_token` and live cost estimation. |
| [`examples/01_long_decode_continuation.ts`](./examples/01_long_decode_continuation.ts) | **1M Output Long-Decode Continuation (TypeScript)** — Full `@google/genai` streaming continuation implementation. |
| [`examples/02_deep_reasoning_thoughts.py`](./examples/02_deep_reasoning_thoughts.py) | **Deep Reasoning & First-Class `thought` Steps** — Stream `thought_summary` and `thought_signature` deltas and control `thinking_level`. |
| [`examples/03_security_code_auditor.py`](./examples/03_security_code_auditor.py) | **Autonomous Code Optimization & Cyber Auditor** — Multi-step tool use + JSON Schema structured output to chain security vulnerabilities and find 40%-class Python speedups. |
| [`examples/04_vanilla_3d_raytracer.py`](./examples/04_vanilla_3d_raytracer.py) | **100% Pure-Python Zero-Dependency 3D Ray-Tracing Engine** — Renders a 3D architectural study with reflections, soft shadows, and parquet floor. |
| [`examples/06_enterprise_research_workflow.py`](./examples/06_enterprise_research_workflow.py) | **Enterprise Multi-Tool Synthesis (Finance/Legal/Science)** — Combines `code_execution` and stateful `previous_interaction_id` chaining. |
| [`examples/07_multimodal_image_video_to_3d.py`](./examples/07_multimodal_image_video_to_3d.py) | **Multimodal Image & Video $\rightarrow$ 3D Scene Reconstructor** — Sends an image or video to `gemini-4-argon` and outputs a JSON Schema 3D scene graph with PBR materials and rigid-body mass. |

---

## ⚡ Quick Start

```bash
git clone https://github.com/RobinaMirbahar/gemini-4-argon-cookbook.git
cd gemini-4-argon-cookbook
pip install -r requirements.txt

# 1. Run Multimodal Image/Video -> 3D Scene Reconstruction
python examples/07_multimodal_image_video_to_3d.py --demo
# Or with a live API key + image/video:
# GEMINI_API_KEY="your-key" python examples/07_multimodal_image_video_to_3d.py --image assets/argon_sunlit_study.png

# 2. Render the 100% Pure-Python 3D Raytracer
python examples/04_vanilla_3d_raytracer.py

# 3. Run the 1M Token Long-Decode Continuation Protocol
python examples/01_long_decode_continuation.py --demo
```

---

## 📜 License

Licensed under the [Apache 2.0 License](./LICENSE).
