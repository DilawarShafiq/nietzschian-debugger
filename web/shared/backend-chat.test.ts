import assert from "node:assert/strict";
import { test } from "node:test";
import { backendChat, backendOrigin, BackendChatError } from "./backend-chat.js";

const payload = {
  provider: "greenpt", language: "nl", philosopher: "popper", fictionalCase: true,
  messages: [{ role: "user", content: "Een fictieve casus." }],
};

test("backend URLs require HTTPS except for localhost and cannot contain credentials or paths", () => {
  assert.equal(backendOrigin("https://api.example.com"), "https://api.example.com");
  assert.equal(backendOrigin("http://127.0.0.1:3080"), "http://127.0.0.1:3080");
  for (const value of ["http://api.example.com", "https://user:pass@api.example.com",
    "https://api.example.com/api/chat", "https://api.example.com?key=secret"]) {
    assert.throws(() => backendOrigin(value));
  }
});

test("configured backend receives only access token and conversation, never a server GreenPT key", async () => {
  const result = await backendChat("https://api.example.com", "fake-access-token", payload, async (url, init) => {
    assert.equal(String(url), "https://api.example.com/api/chat");
    assert.equal(new Headers(init?.headers).get("Authorization"), "Bearer fake-access-token");
    const body = JSON.parse(String(init?.body));
    assert.equal(body.provider, "greenpt");
    assert.equal(body.apiKey, undefined);
    return new Response(JSON.stringify({
      reply: "Welke waarneming weerlegt je aanname?", safety: false, provider: "greenpt",
      model: "test", providerRequests: 1, estimatedInputTokens: 100,
      usage: { input: 100, output: 12, cacheRead: 0, cacheWrite: 0 },
    }));
  });
  assert.equal(result.usage.input, 100);
});

test("backend errors remain explicit and invalid responses are not successful replies", async () => {
  await assert.rejects(backendChat("https://api.example.com", "fake", payload, async () =>
    new Response(JSON.stringify({ error: "BACKEND_AUTH" }), { status: 401 })),
  error => error instanceof BackendChatError && error.failure.error === "BACKEND_AUTH");
  await assert.rejects(backendChat("https://api.example.com", "fake", payload, async () =>
    new Response(JSON.stringify({ reply: "missing usage" }))),
  error => error instanceof BackendChatError && error.failure.error === "BACKEND_UNAVAILABLE");
  await assert.rejects(backendChat("https://api.example.com", "fake", payload, async () => {
    throw new TypeError("Failed to fetch");
  }), error => error instanceof BackendChatError && error.failure.error === "BACKEND_UNAVAILABLE");
});
