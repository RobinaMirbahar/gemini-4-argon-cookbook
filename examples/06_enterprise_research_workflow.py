#!/usr/bin/env python3
"""
Example 06: Gemini 2.5 Pro — Enterprise Multi-Tool Research & Financial Workflow
================================================================================
Inspired by Gemini 2.5 Pro's #1 ranking on the Vals Index (finance, legal, tax, coding)
and Kepler's benchmark (>99% match with analyst-built multi-year SEC financial models).

Demonstrates:
  - Combining built-in Gemini Interactions API tools (`google_search`, `code_execution`, `url_context`)
  - Stateful multi-turn refinement via `previous_interaction_id`
  - Direct, cliché-free executive memo synthesis

Usage:
    python examples/06_enterprise_research_workflow.py --demo
    GEMINI_API_KEY="your-key" python examples/06_enterprise_research_workflow.py
"""

from __future__ import annotations

import argparse
import os
import time

MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")


def run_live_enterprise_workflow() -> None:
    from google import genai

    client = genai.Client()
    print(f"📈 Running Enterprise Multi-Tool Workflow with {MODEL_ID}...\n")

    # Turn 1: Grounded research + Python code execution for sensitivity analysis
    turn1 = client.interactions.create(
        model=MODEL_ID,
        input=(
            "Analyze the unit economics of switching a high-volume enterprise document pipeline "
            "(500M input tokens/day, 80% cache hit rate, 40M output tokens/day) to Gemini 2.5 Pro "
            "at its introductory pricing ($2/1M input, $0.10/1M cached input, $10/1M output). "
            "Use code_execution to compute daily, monthly, and annual costs and compare against "
            "an uncached baseline."
        ),
        tools=[{"type": "code_execution"}],
        generation_config={"thinking_level": "high"},
    )
    print("=== Turn 1: Quantitative Cost & Sensitivity Model ===")
    print(turn1.output_text)

    # Turn 2: Stateful follow-up using previous_interaction_id
    turn2 = client.interactions.create(
        model=MODEL_ID,
        previous_interaction_id=turn1.id,
        input=(
            "Draft a concise, direct 3-bullet CFO executive brief summarizing the ROI of "
            "95% context caching and the 1M unified output limit for automated SEC filing analysis."
        ),
    )
    print("\n=== Turn 2: CFO Executive Brief (Stateful Follow-Up) ===")
    print(turn2.output_text)


def run_demo_enterprise_workflow() -> None:
    print(f"📈 [DEMO MODE] Enterprise Multi-Tool Workflow with {MODEL_ID}")
    print("=" * 72)
    time.sleep(0.15)
    print(
        "=== Turn 1: Quantitative Cost & Sensitivity Model (with `code_execution`) ===\n"
        "🔧 [Step: code_execution_call] Running Python financial model...\n"
        "```python\n"
        "daily_input_m = 500.0\n"
        "cache_hit_ratio = 0.80\n"
        "daily_output_m = 40.0\n\n"
        "uncached_input_cost = (daily_input_m * (1 - cache_hit_ratio)) * 2.00  # $200/day\n"
        "cached_input_cost   = (daily_input_m * cache_hit_ratio) * 0.10        # $40/day (95% off)\n"
        "output_cost         = daily_output_m * 10.00                          # $400/day\n"
        "total_daily_usd     = uncached_input_cost + cached_input_cost + output_cost\n"
        "```\n\n"
        "| Cost Component (Daily Volume) | Volume | Rate (Introductory) | Daily Cost | Monthly (30d) |\n"
        "| :--- | :---: | :---: | :---: | :---: |\n"
        "| **Uncached Input (20%)** | 100M tokens | $2.00 / 1M | $200.00 | $6,000 |\n"
        "| **Cached Input (80% @ 95% off)** | 400M tokens | $0.10 / 1M | $40.00 | $1,200 |\n"
        "| **Output Generation** | 40M tokens | $10.00 / 1M | $400.00 | $12,000 |\n"
        "| **Total With 95% Cache Discount** | **540M tokens** | — | **$640.00** | **$19,200** |\n"
        "| *Baseline Without Context Caching* | *540M tokens* | — | *$1,400.00* | *$42,000* |\n\n"
        "💡 **Net Savings from 95% Context Caching:** **$22,800 / month ($273,600 / year — 54.3% total reduction)**.\n"
    )
    time.sleep(0.15)
    print(
        "=== Turn 2: CFO Executive Brief (`previous_interaction_id` Chained) ===\n"
        "- **54.3% Lower Total Inference Spend:** Leveraging Gemini 2.5 Pro's 95% cached input discount ($0.10/1M tokens) reduces monthly pipeline expenditure from $42,000 to $19,200 at 500M daily input tokens.\n"
        "- **Single-Pass Multi-Year SEC Filing Synthesis:** The expanded 1M unified input/output token limit eliminates multi-stage chunking errors across 10-K/10-Q cohorts.\n"
        "- **Price Lock Window:** Introductory rates ($2/1M input, $10/1M output) apply through November 30, 2026 before standard tier pricing ($4/1M input, $20/1M output) takes effect."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini 2.5 Pro Enterprise Multi-Tool Workflow")
    parser.add_argument("--demo", action="store_true", help="Run in offline demo mode")
    args = parser.parse_args()

    if args.demo or not os.environ.get("GEMINI_API_KEY"):
        if not args.demo:
            print("ℹ️  GEMINI_API_KEY not set — running in --demo mode.\n")
        run_demo_enterprise_workflow()
    else:
        run_live_enterprise_workflow()


if __name__ == "__main__":
    main()
