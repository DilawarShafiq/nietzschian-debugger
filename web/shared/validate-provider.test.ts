import assert from "node:assert/strict";
import { test } from "node:test";
import { validateProvider } from "./validate-provider.js";
import { browserChatError } from "./browser-chat.js";
import { DEFAULT_MODELS } from "./providers.js";

test("Claude validation uses authenticated model lookup with browser opt-in, not a paid completion", async () => {
  const result = await validateProvider("claude", "fake-key", undefined, async (url, init) => {
    assert.equal(String(url), `https://api.anthropic.com/v1/models/${DEFAULT_MODELS.claude}`);
    const headers = new Headers(init?.headers);
    assert.equal(headers.get("x-api-key"), "fake-key");
    assert.equal(headers.get("anthropic-dangerous-direct-browser-access"), "true");
    assert.equal(init?.body, undefined);
    return new Response(JSON.stringify({ id: DEFAULT_MODELS.claude }));
  }, true);
  assert.equal(result, DEFAULT_MODELS.claude);
});

test("GreenPT validation requires the configured model in the authenticated catalogue", async () => {
  const result = await validateProvider("greenpt", "fake-key", undefined, async (url, init) => {
    assert.equal(String(url), "https://api.greenpt.ai/v1/models");
    assert.equal(new Headers(init?.headers).get("authorization"), "Bearer fake-key");
    return new Response(JSON.stringify({ data: [{ id: DEFAULT_MODELS.greenpt }] }));
  });
  assert.equal(result, DEFAULT_MODELS.greenpt);
  await assert.rejects(validateProvider("greenpt", "fake-key", undefined, async () =>
    new Response(JSON.stringify({ data: [] }))));
});

test("invalid keys, forbidden access, malformed catalogues and CORS failures cannot validate", async () => {
  for (const [status, expected] of [[401, "PROVIDER_AUTH"], [403, "PROVIDER_FORBIDDEN"]] as const) {
    await assert.rejects(validateProvider("greenpt", "fake-key", undefined, async () =>
      new Response("Forbidden", { status })), error => browserChatError(error).error === expected);
  }
  await assert.rejects(validateProvider("greenpt", "fake-key", undefined, async () =>
    new Response(JSON.stringify({ data: "invalid" }))));
  await assert.rejects(validateProvider("greenpt", "fake-key", undefined, async () => {
    throw new TypeError("Failed to fetch");
  }), error => browserChatError(error).error === "PROVIDER_NETWORK");
});
