#!/usr/bin/env python3
"""
Example 01: Gemini 4 Argon — 1M Unified Token Limit & Long-Decode Continuation Protocol
========================================================================================
Demonstrates how to use `gemini-4-argon` with the Gemini Interactions API (`google-genai >= 2.25.0`)
to sustain massive multi-step outputs (up to 1,000,000 tokens) using the `continuation_token`
protocol across both unary and streaming calls.

 Pricing telemetry included:
- Introductory Input:  $2.00 / 1M tokens (95% discount on cached input: $0.10 / 1M)
- Introductory Output: $10.00 / 1M tokens

Usage:
    python examples/01_long_decode_continuation.py --demo
    GEMINI_API_KEY="your-key" python examples/01_long_decode_continuation.py
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass

MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-4-argon")

# Introductory pricing through November 30, 2026 (USD per 1M tokens)
INPUT_PRICE_PER_1M = 2.00
CACHED_INPUT_PRICE_PER_1M = 0.10  # 95% off input price
OUTPUT_PRICE_PER_1M = 10.00


@dataclass
class TokenTelemetry:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    continuations: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.cached_input_tokens + self.output_tokens

    @property
    def estimated_cost_usd(self) -> float:
        billable_input = max(0, self.input_tokens - self.cached_input_tokens)
        return (
            (billable_input / 1_000_000) * INPUT_PRICE_PER_1M
            + (self.cached_input_tokens / 1_000_000) * CACHED_INPUT_PRICE_PER_1M
            + (self.output_tokens / 1_000_000) * OUTPUT_PRICE_PER_1M
        )


def print_interaction_text(interaction) -> None:
    """Safely extracts and prints text from an Interaction object."""
    if getattr(interaction, "output_text", None):
        print(interaction.output_text, end="", flush=True)
        return
    for step in getattr(interaction, "steps", []) or []:
        if getattr(step, "type", None) == "model_output":
            for block in getattr(step, "content", []) or []:
                if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                    print(block.text, end="", flush=True)


def run_streaming_long_decode(prompt: str) -> TokenTelemetry:
    """
    Runs a streaming interaction with automatic continuation_token resumption
    for long-horizon outputs up to 1M tokens.
    """
    from google import genai

    client = genai.Client()
    telemetry = TokenTelemetry()

    interaction_id: str | None = None
    continuation_token: str | None = None
    status: str | None = None

    print(f"🚀 Starting Gemini 4 Argon Long-Decode Stream (model={MODEL_ID})\n" + "=" * 72)

    while True:
        stream = client.interactions.create(
            model=MODEL_ID,
            input=None if continuation_token else prompt,
            previous_interaction_id=interaction_id,
            continuation_token=continuation_token,
            generation_config={
                "thinking_level": "high",
                "thinking_summaries": "auto",
            },
            stream=True,
        )

        status = None
        for event in stream:
            if event.event_type == "step.delta":
                delta_type = getattr(event.delta, "type", None)
                if delta_type == "thought_summary":
                    summary_text = getattr(event.delta, "text", "")
                    if summary_text:
                        print(f"\n💭 [Argon Thought] {summary_text}", end="", flush=True)
                elif delta_type == "text":
                    print(getattr(event.delta, "text", ""), end="", flush=True)
            elif event.event_type == "interaction.completed":
                interaction = event.interaction
                interaction_id = interaction.id
                status = interaction.status
                continuation_token = getattr(interaction, "continuation_token", None)

                usage = getattr(interaction, "usage", None)
                if usage:
                    telemetry.input_tokens += getattr(usage, "input_tokens", 0) or 0
                    telemetry.cached_input_tokens += getattr(usage, "cached_tokens", 0) or 0
                    telemetry.output_tokens += getattr(usage, "output_tokens", 0) or 0

        if status == "incomplete" and continuation_token:
            telemetry.continuations += 1
            print(
                f"\n\n🔄 [Long-Decode Continuation #{telemetry.continuations}] "
                f"Resuming interaction {interaction_id}...\n"
            )
        else:
            break

    print(f"\n\n✅ Final stream status: {status}")
    return telemetry


def run_demo_simulation() -> TokenTelemetry:
    """Simulates a multi-chunk 1M Long-Decode trajectory when run with --demo."""
    print(f"🚀 [DEMO MODE] Gemini 4 Argon Long-Decode Stream (model={MODEL_ID})\n" + "=" * 72)
    chunks = [
        (
            "thought_summary",
            "Analyzing Chromium legacy TabContents architecture (~6M LOC boundary). "
            "Planning zero-reload view reparenting across tab, side-panel, and floating window hosts...",
        ),
        (
            "text",
            "\n### Phase 1: Decoupling WebContents View Ownership\n"
            "To allow live webpages to move fluidly between tabs, side panels, and floating windows "
            "without reloading, we extract `WebPageHostController` from the legacy browser frame tree:\n\n"
            "```cpp\n"
            "class WebPageHostController : public content::WebContentsObserver {\n"
            " public:\n"
            "  void AttachToSlot(ui::ViewSlot* target_slot) {\n"
            "    ScopedViewReparentLock lock(web_contents());\n"
            "    target_slot->MountNativeView(web_contents()->GetNativeView());\n"
            "  }\n"
            "};\n"
            "```\n",
        ),
        ("continuation", "v1_cont_argon_89f2a1c4_segment_1"),
        (
            "thought_summary",
            "Verifying lifetime invariants across 142 call sites to eliminate use-after-free crashes during tab detachment...",
        ),
        (
            "text",
            "\n### Phase 2: Formal Lifetime & State Preservation Guarantee\n"
            "By retaining the compositor surface handle inside `ScopedViewReparentLock`, active WebRTC "
            "streams, WebGL contexts, and service worker channels remain uninterrupted across host transitions.\n",
        ),
    ]

    for kind, content in chunks:
        time.sleep(0.15)
        if kind == "thought_summary":
            print(f"\n💭 [Argon Thought] {content}\n")
        elif kind == "text":
            print(content, end="", flush=True)
        elif kind == "continuation":
            print(
                f"\n🔄 [Long-Decode Continuation #1] status='incomplete' | "
                f"continuation_token='{content}' -> Resuming seamlessly..."
            )

    print("\n✅ Final stream status: completed")
    return TokenTelemetry(
        input_tokens=185_400,
        cached_input_tokens=160_000,
        output_tokens=142_850,
        continuations=1,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gemini 4 Argon 1M Unified Token Limit & Long-Decode Continuation Example"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in offline demonstration mode without requiring GEMINI_API_KEY",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=(
            "Architect a complete, production-grade C++20 to Rust incremental migration plan "
            "for a high-throughput video decoder, including safe SIMD auto-vectorization patterns."
        ),
        help="Prompt to send to Gemini 4 Argon",
    )
    args = parser.parse_args()

    if args.demo or not os.environ.get("GEMINI_API_KEY"):
        if not args.demo:
            print("ℹ️  GEMINI_API_KEY not set — running in --demo mode.\n")
        telemetry = run_demo_simulation()
    else:
        telemetry = run_streaming_long_decode(args.prompt)

    print("\n📊 Gemini 4 Argon Telemetry & Cost Summary")
    print("-" * 44)
    print(f"  Input Tokens        : {telemetry.input_tokens:,}")
    print(f"  Cached Input Tokens : {telemetry.cached_input_tokens:,} (95% discount: $0.10/1M)")
    print(f"  Output Tokens       : {telemetry.output_tokens:,} (1M max limit)")
    print(f"  Continuations Used  : {telemetry.continuations}")
    print(f"  Estimated Cost (USD): ${telemetry.estimated_cost_usd:.4f}")


if __name__ == "__main__":
    main()
