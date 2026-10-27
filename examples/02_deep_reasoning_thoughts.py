#!/usr/bin/env python3
"""
Example 02: Gemini 2.5 Pro — Deep Reasoning & First-Class Thought Steps
=======================================================================
In the Gemini Interactions API (`client.interactions.create`), model reasoning is surfaced
as first-class `thought` steps in the `interaction.steps` timeline, complete with:
  - `signature`: Cryptographic representation of Gemini 2.5 Pro's internal reasoning state
  - `summary`: Human-readable reasoning summary blocks when `thinking_summaries="auto"`

Inspired by Gemini 2.5 Pro's scientific & mathematical breakthroughs:
  - 100x spacetime reduction for formally verified quantum `arcsin` circuits in Lean
  - Broader class of counterexamples to Grad's 1967 conjecture for nuclear fusion stellarators

Usage:
    python examples/02_deep_reasoning_thoughts.py --demo
    GEMINI_API_KEY="your-key" python examples/02_deep_reasoning_thoughts.py
"""

from __future__ import annotations

import argparse
import os
import time

MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")

SCIENTIFIC_PROMPT = (
    "We are designing a fault-tolerant quantum subroutine for computing arcsin(x) "
    "within a block-encoded Hamiltonian simulation. Show how a polynomial Chebyshev "
    "approximation combined with reversible lookup-addition reduces T-depth and "
    "spacetime volume (qubits x gates) compared to a standard iterative CORDIC circuit, "
    "and sketch the Lean 4 error-bound theorem signature."
)


def run_live_thinking(prompt: str) -> None:
    from google import genai

    client = genai.Client()
    print(f"🧠 Querying {MODEL_ID} with thinking_level='high' & thinking_summaries='auto'...\n")

    interaction = client.interactions.create(
        model=MODEL_ID,
        input=prompt,
        generation_config={
            "thinking_level": "high",
            "thinking_summaries": "auto",
        },
    )

    for idx, step in enumerate(getattr(interaction, "steps", []) or [], start=1):
        step_type = getattr(step, "type", "unknown")
        if step_type == "thought":
            sig = getattr(step, "signature", "")
            sig_preview = f"{sig[:24]}...{sig[-12:]}" if len(sig) > 40 else sig
            print(f"🔒 [Step {idx}: thought] Cryptographic Signature: {sig_preview}")
            for block in getattr(step, "summary", []) or []:
                if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                    print(f"💭 Thought Summary:\n{block.text}\n")
        elif step_type == "model_output":
            print(f"✨ [Step {idx}: model_output]")
            for block in getattr(step, "content", []) or []:
                if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                    print(block.text)

    usage = getattr(interaction, "usage", None)
    if usage:
        print(f"\n📊 Total Tokens Used: {getattr(usage, 'total_tokens', 'N/A')}")


def run_demo_thinking() -> None:
    print(f"🧠 [DEMO MODE] Querying {MODEL_ID} with thinking_level='high' & thinking_summaries='auto'...\n")
    time.sleep(0.15)
    print("🔒 [Step 1: thought] Cryptographic Signature: Ev8BCkYIAhIAGiC94a7b2e1f8c3d...9a0e4b12c8d1")
    print(
        "💭 Thought Summary:\n"
        "  1. Compare spacetime volume (Q * T_count) of n-bit quantum CORDIC vs. piecewise Chebyshev polynomial.\n"
        "  2. Standard quantum CORDIC requires O(n) serial rotation stages, each invoking ripple-carry additions "
        "and ancilla uncomputation, scaling as O(n^2) Toffoli gates.\n"
        "  3. By partitioning [-1, 1] into dyadic intervals near the singular derivative at |x| -> 1 and applying "
        "a degree-d minimax polynomial with QROM lookup + out-of-place Karatsuba multiply, spacetime cost drops >100x.\n"
    )
    time.sleep(0.15)
    print(
        "✨ [Step 2: model_output]\n"
        "### Spacetime-Optimized Quantum `arcsin(x)` Subroutine\n\n"
        "| Metric ($n = 16$ bits precision) | Baseline Quantum CORDIC | Gemini 2.5 Pro Piecewise-Chebyshev QROM | Reduction |\n"
        "| :--- | :---: | :---: | :---: |\n"
        "| **Toffoli / T-Gate Count** | $14,820$ | $312$ | **47.5×** |\n"
        "| **Logical Ancilla Qubits** | $96$ | $42$ | **2.28×** |\n"
        "| **Spacetime Volume (Qubits × Depth)** | $1.42 \\times 10^6$ | $1.31 \\times 10^4$ | **108.4×** |\n\n"
        "#### Formal Verification Specification (Lean 4)\n"
        "```lean\n"
        "import Mathlib.Analysis.SpecialFunctions.Trigonometric.Inverse\n\n"
        "theorem quantum_arcsin_chebyshev_bound\n"
        "    (x : ℝ) (hx : x ∈ Set.Icc (-1 + 2^(-16 : ℤ)) (1 - 2^(-16 : ℤ))) :\n"
        "    |polyApproxArcsin 16 x - Real.arcsin x| ≤ (2 : ℝ)^(-16 : ℤ) := by\n"
        "  -- Verified minimax residual bound across dyadic boundary segments\n"
        "  exact chebyshev_dyadic_interval_bound x hx\n"
        "```"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini 2.5 Pro Deep Reasoning & Thought Steps")
    parser.add_argument("--demo", action="store_true", help="Run in offline demo mode")
    args = parser.parse_args()

    if args.demo or not os.environ.get("GEMINI_API_KEY"):
        if not args.demo:
            print("ℹ️  GEMINI_API_KEY not set — running in --demo mode.\n")
        run_demo_thinking()
    else:
        run_live_thinking(SCIENTIFIC_PROMPT)


if __name__ == "__main__":
    main()
