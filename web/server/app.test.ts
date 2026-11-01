import assert from "node:assert/strict";
import { once } from "node:events";
import { test } from "node:test";
import type { AddressInfo } from "node:net";
import { createApp, type CompletionFactory } from "./app.js";

const payload = {
  language: "nl", philosopher: "nietzsche", fictionalCase: true,
  messages: [{ role: "user", content: "Een fictieve oefencasus." }],
};
const usage = { input: 100, output: 25, cacheRead: 0, cacheWrite: 0 };

async function withApp(factory: CompletionFactory, run: (url: string) => Promise<void>, origin?: string, token?: string) {
  const server = createApp({ claude: "test-model", greenpt: "green-test-model" }, factory, origin, token).listen(0, "127.0.0.1");
  await once(server, "listening");
  const url = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  try { await run(url); }
  finally { await new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve())); }
}

test("missing key is explicit and never invokes a model", async () => {
  await withApp(() => null, async (url) => {
    const result = await fetch(`${url}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });

    assert.equal(result.status, 503);
    assert.deepEqual(await result.json(), { error: "MISSING_KEY" });
    assert.equal(result.headers.get("cache-control"), "no-store");
  });
});

test("backend token protects server-key access and preflight permits Authorization without a token", async () => {
  const token = "test-backend-token-of-at-least-32-characters";
  let calls = 0;
  await withApp(() => {
    calls++;
    return async () => ({ text: "Welke aanname onderzoek je?", usage });
  }, async url => {
    const health = await fetch(`${url}/healthz`);
    assert.equal(health.status, 200);
    assert.deepEqual(await health.json(), { status: "ok" });
    const preflight = await fetch(`${url}/api/chat`, {
      method: "OPTIONS", headers: { Origin: "https://bartvanderwal.github.io" },
    });
    assert.equal(preflight.status, 204);
    assert.match(preflight.headers.get("access-control-allow-headers") || "", /Authorization/);
    for (const authorization of ["", "Bearer wrong"]) {
      const denied = await fetch(`${url}/api/chat`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: authorization },
        body: JSON.stringify(payload),
      });
      assert.equal(denied.status, 401);
      assert.deepEqual(await denied.json(), { error: "BACKEND_AUTH" });
    }
    assert.equal(calls, 0);
    const allowed = await fetch(`${url}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ ...payload, provider: "greenpt" }),
    });
    assert.equal(allowed.status, 200);
    assert.ok(!(await allowed.text()).includes(token));
    assert.equal(calls, 1);
  }, "https://bartvanderwal.github.io", token);
});

test("user key is passed only to the factory and is never echoed", async () => {
  const key = "test-key-not-a-real-secret";
  let receivedKey: string | undefined;
  await withApp((value) => {
    receivedKey = value;
    return async () => ({ text: "Welke aanname wil je onderzoeken?", usage });
  }, async (url) => {
    const result = await fetch(`${url}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, apiKey: key }),
    });
    assert.equal(result.status, 200);
    assert.equal(receivedKey, key);
    const text = await result.text();
    assert.ok(!text.includes(key));
    assert.equal(JSON.parse(text).usage.input, 100);
  });
});

test("GET is not a chat endpoint and invalid JSON never calls Claude", async () => {
  await withApp(() => { assert.fail("Must not call Claude"); }, async (url) => {
    assert.equal((await fetch(`${url}/api/chat`)).status, 404);
    const response = await fetch(`${url}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: "{broken",
    });
    assert.equal(response.status, 400);
  });
});

test("CORS permits only configured Pages origin, not arbitrary websites", async () => {
  await withApp(() => null, async (url) => {
    const allowed = await fetch(`${url}/api/chat`, {
      method: "OPTIONS", headers: { Origin: "https://bartvanderwal.github.io" },
    });
    assert.equal(allowed.status, 204);
    assert.equal(allowed.headers.get("access-control-allow-origin"), "https://bartvanderwal.github.io");
    const denied = await fetch(`${url}/api/chat`, {
      method: "OPTIONS", headers: { Origin: "https://other.example" },
    });
    assert.equal(denied.status, 403);
    assert.equal(denied.headers.get("access-control-allow-origin"), null);
  }, "https://bartvanderwal.github.io");
});

test("provider errors are sanitized with known usage and request counts", async () => {
  await withApp(() => async () => { throw Object.assign(new Error("sensitive details"), { status: 401 }); },
    async (url) => {
      const result = await fetch(`${url}/api/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      });

      assert.equal(result.status, 502);
      const body = await result.json();
      assert.equal(body.error, "PROVIDER_AUTH");
      assert.equal(body.providerRequests, 1);
      assert.ok(!JSON.stringify(body).includes("sensitive"));
    });
});

test("GreenPT selection routes its key, model, and Popper prompt to the correct completion", async () => {
  const key = "greenpt-test-key-not-real";
  await withApp((value, provider) => {
    assert.equal(provider, "greenpt");
    assert.equal(value, key);
    return async (system) => {
      assert.match(system, /POPPER/);
      assert.match(system, /weerleggen/);
      return { text: "Welke waarneming kan je hypothese weerleggen?", usage };
    };
  }, async (url) => {
    const response = await fetch(`${url}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, provider: "greenpt", philosopher: "popper", apiKey: key }),
    });
    assert.equal(response.status, 200);
    const result = await response.json();
    assert.equal(result.provider, "greenpt");
    assert.equal(result.model, "green-test-model");
    assert.equal(result.providerRequests, 1);
    assert.ok(!JSON.stringify(result).includes(key));
  });
});

test("request limit blocks the twenty-first call before provider access", async () => {
  let calls = 0;
  await withApp(() => async () => {
    calls++;
    return { text: "Welke aanname onderzoek je?", usage };
  }, async (url) => {
    for (let index = 0; index < 21; index++) {
      const result = await fetch(`${url}/api/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      });
      assert.equal(result.status, index < 20 ? 200 : 429);
    }
    assert.equal(calls, 20);
  });
});
