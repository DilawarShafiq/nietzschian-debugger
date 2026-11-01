import assert from "node:assert/strict";
import { test } from "node:test";
import { browserChat, browserChatError } from "./browser-chat.js";
import { DEFAULT_MODELS, PROVIDER_ENDPOINTS } from "./providers.js";
import { systemPrompt, type Provider } from "./prompts.js";

const input = {
  language: "nl", philosopher: "popper", fictionalCase: true,
  apiKey: "fake-browser-test-key",
  messages: [{ role: "user", content: "Een fictieve casus." }],
};
const question = "Welke waarneming zou je aanname weerleggen?";

function response(provider: Provider, text = question) {
  return new Response(JSON.stringify(provider === "claude" ? {
    id: "test", type: "message", role: "assistant", model: DEFAULT_MODELS.claude,
    stop_reason: "end_turn", content: [{ type: "text", text }],
    usage: { input_tokens: 100, output_tokens: 12 },
  } : {
    choices: [{ finish_reason: "stop", message: { role: "assistant", content: text } }],
    usage: { prompt_tokens: 100, completion_tokens: 12 },
  }), { headers: { "Content-Type": "application/json" } });
}

for (const provider of ["claude", "greenpt"] as const) {
  test(`${provider} browser calls go directly to the fixed provider, with key and actual bilingual prompt`, async () => {
    let calls = 0;
    const fetcher: typeof fetch = async (url, init) => {
      calls++;
      assert.equal(String(url), PROVIDER_ENDPOINTS[provider]);
      const headers = new Headers(init?.headers);
      const body = JSON.parse(String(init?.body));
      assert.equal(body.model, DEFAULT_MODELS[provider]);
      assert.equal(body.max_tokens, 512);
      if (provider === "claude") {
        assert.equal(headers.get("x-api-key"), input.apiKey);
        assert.equal(headers.get("anthropic-dangerous-direct-browser-access"), "true");
        assert.equal(body.system, systemPrompt("nl", "popper"));
      } else {
        assert.equal(headers.get("authorization"), `Bearer ${input.apiKey}`);
        assert.equal(body.messages[0].content, systemPrompt("nl", "popper"));
        assert.equal(body.messages[0].role, "system");
      }
      assert.ok(!JSON.stringify(body).includes(input.apiKey));
      return response(provider);
    };
    const result = await browserChat({ ...input, provider }, fetcher);
    assert.equal(calls, 1);
    assert.equal(result.providerRequests, 1);
    assert.equal(result.provider, provider);
    assert.equal(result.reply, question);
    assert.deepEqual(result.usage, { input: 100, output: 12, cacheRead: 0, cacheWrite: 0 });
    assert.ok(!JSON.stringify(result).includes(input.apiKey));
  });

  test(`${provider} network/CORS failure is explicit, with no retry or proxy fallback`, async () => {
    let calls = 0;
    await assert.rejects(browserChat({ ...input, provider }, async () => {
      calls++;
      throw new TypeError("Failed to fetch");
    }), error => {
      const failure = browserChatError(error);
      assert.equal(failure.error, "PROVIDER_NETWORK");
      assert.equal(failure.providerRequests, 1);
      assert.ok(!JSON.stringify(failure).includes(input.apiKey));
      return true;
    });
    assert.equal(calls, 1);
  });
}

test("readable GreenPT 403 is distinct from a browser network/CORS failure", async () => {
  await assert.rejects(browserChat({ ...input, provider: "greenpt" }, async () =>
    new Response("Forbidden", { status: 403 })), error => {
    assert.equal(browserChatError(error).error, "PROVIDER_FORBIDDEN");
    return true;
  });
});

test("browser preserves reflection retry rules and counts both requests and token usage", async () => {
  let calls = 0;
  const result = await browserChat({ ...input, provider: "claude" }, async () =>
    response("claude", ++calls === 1 ? "You should decide now." : question));
  assert.equal(calls, 2);
  assert.equal(result.providerRequests, 2);
  assert.equal(result.usage.input, 200);
  assert.equal(result.usage.output, 24);
});

test("missing keys, absent consent and endpoint injection are rejected before network access", async () => {
  let calls = 0;
  const fetcher: typeof fetch = async () => { calls++; throw new Error("Must not be reached"); };
  await assert.rejects(browserChat({ ...input, apiKey: undefined }, fetcher), error => {
    assert.equal(browserChatError(error).error, "MISSING_KEY");
    return true;
  });
  for (const invalid of [
    { ...input, fictionalCase: false }, { ...input, baseURL: "https://example.com" },
    { ...input, provider: "unknown" },
  ]) {
    await assert.rejects(browserChat(invalid, fetcher), error => {
      assert.equal(browserChatError(error).error, "INVALID_REQUEST");
      return true;
    });
  }
  assert.equal(calls, 0);
});
