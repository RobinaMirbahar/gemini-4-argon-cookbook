#!/usr/bin/env python3
"""
Example 03: Gemini 4 Argon — Autonomous Code Optimization & Cybersecurity Auditor
=================================================================================
Inspired by two flagship real-world stories from the Gemini 4 Argon launch blog post:
  1. `google/adk-python` Overnight Optimization: Eliminated framework overhead, cutting
     in-memory session prep time by 40% in long sessions and speeding up cold imports by 21%.
  2. Wiz "Scan for Good" / Fairwind Program: Chained subtle vulnerabilities (public file
     download bypass -> exposed master key -> admin access) to protect critical infrastructure.

This script uses the Gemini Interactions API (`client.interactions.create`) combining:
  - Custom Function Calling (`inspect_module_source`, `profile_hot_path`)
  - Stateful multi-turn execution (`previous_interaction_id` + `function_result` steps)
  - Structured JSON Schema output (`response_format`) for deterministic remediation reports

Usage:
    python examples/03_security_code_auditor.py --demo
    GEMINI_API_KEY="your-key" python examples/03_security_code_auditor.py
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any

MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-4-argon")

# Sample legacy module containing both a chained security vulnerability and a session-prep bottleneck
SAMPLE_MODULES: dict[str, str] = {
    "session_manager.py": '''import copy
import importlib
import os
import json

# Eagerly importing heavy optional plugins at module load time (hurts cold import by ~21%)
import pandas as _ heavy_df_plugin
import cryptography.hazmat.primitives.asymmetric.rsa as _heavy_crypto

MASTER_SIGNING_KEY_PATH = "/etc/argon_service/keys/master_admin.key"

class SessionManager:
    def __init__(self, base_config: dict):
        self.base_config = base_config
        self.history = []

    def prepare_session_context(self, session_events: list[dict]) -> dict:
        """Called before every turn in long-horizon agent sessions."""
        # Bottleneck: O(N^2) deep-copying entire session history on every event iteration
        ctx = {}
        for event in session_events:
            snapshot = copy.deepcopy(self.base_config)
            snapshot["events"] = [copy.deepcopy(e) for e in session_events]
            ctx[event["id"]] = snapshot
        return ctx

    def download_attachment(self, user_supplied_filename: str) -> bytes:
        """Serves static report templates from /var/app/templates."""
        # Vulnerability Chain Part 1: Naive string replacement can be bypassed via '....//'
        sanitized = user_supplied_filename.replace("../", "")
        target_path = os.path.join("/var/app/templates", sanitized)
        with open(target_path, "rb") as f:
            return f.read()

    def verify_admin_token(self, token_signature: str) -> bool:
        """Vulnerability Chain Part 2: Master key stored at predictable path readable via bypass."""
        with open(MASTER_SIGNING_KEY_PATH, "r", encoding="utf-8") as f:
            master_secret = f.read().strip()
        return token_signature == master_secret
'''
}

TOOLS = [
    {
        "type": "function",
        "name": "inspect_module_source",
        "description": "Reads the source code of a target module in the workspace for auditing.",
        "parameters": {
            "type": "object",
            "properties": {
                "module_name": {
                    "type": "string",
                    "description": "Name of the Python file, e.g., 'session_manager.py'",
                }
            },
            "required": ["module_name"],
        },
    },
    {
        "type": "function",
        "name": "profile_hot_path",
        "description": "Returns CPU and import-time profiling telemetry for a module.",
        "parameters": {
            "type": "object",
            "properties": {
                "module_name": {"type": "string"}
            },
            "required": ["module_name"],
        },
    },
]

AUDIT_REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "chained_vulnerabilities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},
                    "exploit_chain_steps": {"type": "array", "items": {"type": "string"}},
                    "patch_code": {"type": "string"},
                },
                "required": ["title", "severity", "exploit_chain_steps", "patch_code"],
            },
        },
        "performance_optimizations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "bottleneck": {"type": "string"},
                    "expected_speedup": {"type": "string"},
                    "optimized_code": {"type": "string"},
                },
                "required": ["bottleneck", "expected_speedup", "optimized_code"],
            },
        },
    },
    "required": ["chained_vulnerabilities", "performance_optimizations"],
}


def execute_local_tool(name: str, args: dict[str, Any]) -> str:
    if name == "inspect_module_source":
        mod = args.get("module_name", "session_manager.py")
        return SAMPLE_MODULES.get(mod, "# Module not found")
    if name == "profile_hot_path":
        return json.dumps(
            {
                "cold_import_ms": 420.5,
                "prepare_session_context_500_events_ms": 1840.2,
                "hotspot": "copy.deepcopy inside nested loop (89% CPU time)",
            }
        )
    return "{}"


def run_live_audit() -> dict[str, Any]:
    from google import genai

    client = genai.Client()
    prompt = (
        "Audit `session_manager.py` for both chained cybersecurity vulnerabilities and "
        "performance bottlenecks. Call `inspect_module_source` and `profile_hot_path` first, "
        "then return a structured JSON remediation report."
    )

    print(f"🛡️  Starting Gemini 4 Argon Security & Performance Audit (model={MODEL_ID})...")
    interaction = client.interactions.create(
        model=MODEL_ID,
        input=prompt,
        tools=TOOLS,
        generation_config={"thinking_level": "high"},
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AUDIT_REPORT_SCHEMA,
        },
    )

    # Tool execution loop
    while True:
        function_calls = [
            step for step in (getattr(interaction, "steps", []) or [])
            if getattr(step, "type", None) == "function_call"
        ]
        if not function_calls:
            break

        result_steps = []
        for call in function_calls:
            fn_name = call.name
            fn_args = call.arguments if isinstance(call.arguments, dict) else json.loads(call.arguments)
            print(f"  🔧 [Argon Tool Call] {fn_name}({json.dumps(fn_args)})")
            tool_output = execute_local_tool(fn_name, fn_args)
            result_steps.append(
                {
                    "type": "function_result",
                    "call_id": call.id,
                    "name": fn_name,
                    "result": tool_output,
                }
            )

        interaction = client.interactions.create(
            model=MODEL_ID,
            previous_interaction_id=interaction.id,
            input=result_steps,
            tools=TOOLS,
            generation_config={"thinking_level": "high"},
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": AUDIT_REPORT_SCHEMA,
            },
        )

    return json.loads(interaction.output_text)


def run_demo_audit() -> dict[str, Any]:
    print(f"🛡️  [DEMO MODE] Gemini 4 Argon Security & Performance Audit (model={MODEL_ID})")
    print("=" * 76)
    time.sleep(0.1)
    print('  🔧 [Argon Tool Call] inspect_module_source({"module_name": "session_manager.py"})')
    time.sleep(0.1)
    print('  🔧 [Argon Tool Call] profile_hot_path({"module_name": "session_manager.py"})')
    time.sleep(0.15)
    return {
        "chained_vulnerabilities": [
            {
                "title": "Non-Recursive Path Traversal Chained to Master Signing Key Extraction",
                "severity": "CRITICAL",
                "exploit_chain_steps": [
                    "1. `download_attachment()` uses single-pass `.replace('../', '')`, which is bypassed by supplying `....//....//....//etc/argon_service/keys/master_admin.key`.",
                    "2. Attacker downloads `MASTER_SIGNING_KEY_PATH` via the public attachment endpoint.",
                    "3. `verify_admin_token()` compares raw string equality (also vulnerable to timing attacks) against the leaked key, granting full administrator access.",
                ],
                "patch_code": (
                    "base_dir = pathlib.Path('/var/app/templates').resolve()\n"
                    "target_path = (base_dir / pathlib.Path(user_supplied_filename).name).resolve()\n"
                    "if not target_path.is_relative_to(base_dir):\n"
                    "    raise PermissionError('Path traversal blocked')\n"
                    "# Use hmac.compare_digest() for constant-time token verification"
                ),
            }
        ],
        "performance_optimizations": [
            {
                "bottleneck": "O(N^2) redundant copy.deepcopy() inside prepare_session_context()",
                "expected_speedup": "~40% faster session preparation in long-horizon sessions",
                "optimized_code": (
                    "def prepare_session_context(self, session_events: list[dict]) -> dict:\n"
                    "    shared_events = tuple(session_events)  # Immutable structural sharing\n"
                    "    base = self.base_config.copy()\n"
                    "    return {e['id']: {**base, 'events': shared_events} for e in session_events}"
                ),
            },
            {
                "bottleneck": "Eager top-level imports of unused heavy plugins (`pandas`, `rsa`)",
                "expected_speedup": "~21% faster cold module import time",
                "optimized_code": (
                    "# Defer heavy plugin imports to lazy function-level loading or PEP 690 lazy imports"
                ),
            },
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini 4 Argon Autonomous Security & Code Auditor")
    parser.add_argument("--demo", action="store_true", help="Run in offline demo mode")
    args = parser.parse_args()

    if args.demo or not os.environ.get("GEMINI_API_KEY"):
        if not args.demo:
            print("ℹ️  GEMINI_API_KEY not set — running in --demo mode.\n")
        report = run_demo_audit()
    else:
        report = run_live_audit()

    print("\n📋 Structured Audit Report (JSON Schema Validated):")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
