import assert from "node:assert/strict";
import { test } from "node:test";
import { completion, GREENPT_BASE_URL, greenMessages, greenUsage } from "./providers.js";

test("GreenPT uses the official fixed EU endpoint and preserves system instructions", () => {
  assert.equal(GREENPT_BASE_URL, "https://api.greenpt.ai/v1");
  assert.deepEqual(greenMessages("Dutch Popper instructions", [{ role: "user", content: "A fictional case." }]), [
    { role: "system", content: "Dutch Popper instructions" },
    { role: "user", content: "A fictional case." },
  ]);
});

test("GreenPT usage does not double-count cached prompt tokens", () => {
  assert.deepEqual(greenUsage({
    prompt_tokens: 100, completion_tokens: 15, prompt_tokens_details: { cached_tokens: 30 },
  }), { input: 70, output: 15, cacheRead: 30, cacheWrite: 0 });
  assert.deepEqual(greenUsage({ prompt_tokens: 100, completion_tokens: 15 }),
    { input: 100, output: 15, cacheRead: 0, cacheWrite: 0 });
});

test("missing or invalid usage is rejected, not reported as zero", () => {
  assert.throws(() => greenUsage(undefined));
  assert.throws(() => greenUsage({ prompt_tokens: -1, completion_tokens: 15 }));
  assert.throws(() => greenUsage({
    prompt_tokens: 10, completion_tokens: 15, prompt_tokens_details: { cached_tokens: 30 },
  }));
});

test("GreenPT SDK sends bearer auth, model, system prompt and output limit to the documented endpoint", async () => {
  let calls = 0;
  const fetcher: typeof fetch = async (input, init) => {
    calls++;
    assert.equal(String(input), "https://api.greenpt.ai/v1/chat/completions");
    assert.equal(new Headers(init?.headers).get("authorization"), "Bearer fake-test-key");
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body));
    assert.equal(body.model, "mistral-small-3.2-24b-instruct-2506");
    assert.equal(body.max_tokens, 512);
    assert.equal(body.messages[0].role, "system");
    assert.equal(body.messages[0].content, "POPPER Dutch system prompt");
    return new Response(JSON.stringify({
      choices: [{ finish_reason: "stop", message: { role: "assistant", content: "Welke waarneming zou dit weerleggen?" } }],
      usage: { prompt_tokens: 120, completion_tokens: 12 },
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  };
  const result = await completion("greenpt", "fake-test-key", "mistral-small-3.2-24b-instruct-2506", fetcher)(
    "POPPER Dutch system prompt", [{ role: "user", content: "A fictional case." }],
  );
  assert.equal(calls, 1);
  assert.equal(result.text, "Welke waarneming zou dit weerleggen?");
  assert.equal(result.usage.input, 120);
});
