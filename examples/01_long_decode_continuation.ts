/**
 * Example 01 (TypeScript): Gemini 2.5 Pro — 1M Token Long-Decode Continuation Protocol
 * ====================================================================================
 * Uses the official `@google/genai` (>= 2.3.0) Interactions API (`ai.interactions.create`)
 * to stream long-horizon reasoning and code generation up to 1,000,000 tokens,
 * automatically resuming whenever `status === 'incomplete'` and `continuation_token` is present.
 *
 * Run:
 *   GEMINI_API_KEY="your-key" npx tsx examples/01_long_decode_continuation.ts
 */

import { GoogleGenAI } from "@google/genai";

const MODEL = process.env.GEMINI_MODEL || "gemini-2.5-pro";
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

async function runStreamingLongDecode(ai: GoogleGenAI, prompt: string) {
  console.log(`🚀 Starting Gemini 2.5 Pro Long-Decode Stream (model=${MODEL})`);
  console.log("=".repeat(72));

  let interactionId: string | undefined;
  let continuationToken: string | undefined;
  let status: string | undefined;
  let continuationCount = 0;

  do {
    const stream = await ai.interactions.create({
      model: MODEL,
      input: continuationToken ? undefined : prompt,
      previous_interaction_id: interactionId,
      continuation_token: continuationToken,
      generation_config: {
        thinking_level: "high",
        thinking_summaries: "auto",
      },
      stream: true,
    });

    status = undefined;
    for await (const event of stream) {
      if (event.event_type === "step.delta") {
        if (event.delta?.type === "thought_summary" && event.delta.text) {
          process.stdout.write(`\n💭 [Gemini 2.5 Pro Thought] ${event.delta.text}\n`);
        } else if (event.delta?.type === "text") {
          process.stdout.write(event.delta.text ?? "");
        }
      } else if (event.event_type === "interaction.completed") {
        interactionId = event.interaction.id;
        status = event.interaction.status;
        continuationToken = event.interaction.continuation_token;
      }
    }

    if (status === "incomplete" && continuationToken) {
      continuationCount += 1;
      console.log(
        `\n\n🔄 [Long-Decode Continuation #${continuationCount}] Resuming ${interactionId}...`
      );
    }
  } while (status === "incomplete" && continuationToken);

  console.log(`\n\n✅ Final stream status: ${status}`);
}

async function main() {
  if (!GEMINI_API_KEY) {
    console.log("ℹ️  Set GEMINI_API_KEY to run against the live Gemini 2.5 Pro API.");
    console.log("   Example: GEMINI_API_KEY='...' npx tsx examples/01_long_decode_continuation.ts");
    return;
  }

  const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });
  await runStreamingLongDecode(
    ai,
    "Design a zero-copy, lock-free telemetry pipeline in TypeScript and Rust WebAssembly capable of processing 1M events/sec."
  );
}

main().catch(console.error);
