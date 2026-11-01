import assert from "node:assert/strict";
import { test } from "node:test";
import { chat, chatSchema, ProviderError, ResponseError } from "./chat.js";
import { estimateInputTokens, systemPrompt, type Language, type Philosopher } from "../shared/prompts.js";

const messages = [{ role: "user" as const, content: "A fictional case about my first impression." }];
const usage = { input: 90, output: 20, cacheRead: 4, cacheWrite: 0 };

test("all eight language/lens combinations produce explicit prompts", () => {
  for (const language of ["nl", "en"] as Language[]) {
    for (const philosopher of ["socrates", "nietzsche", "zarathustra", "popper"] as Philosopher[]) {
      assert.match(systemPrompt(language, philosopher), new RegExp(philosopher, "i"));
      assert.match(systemPrompt(language, philosopher), /\[SAFETY\]/);
    }
  }
  assert.match(systemPrompt("nl", "socrates"), /Nederlands/);
  assert.match(systemPrompt("en", "socrates"), /English/);
  assert.match(systemPrompt("nl", "popper"), /weerleggen/);
  assert.match(systemPrompt("en", "popper"), /refute/);
  assert.notEqual(systemPrompt("nl", "popper"), systemPrompt("nl", "socrates"));
});

test("estimates include prompt and history and grow with input", () => {
  const empty = estimateInputTokens("nl", "nietzsche", []);
  assert.ok(empty > 200);
  assert.ok(estimateInputTokens("nl", "nietzsche", messages) > empty);
});

test("validation rejects non-consent, roles, excess text, and invalid keys", () => {
  const valid = { language: "nl", philosopher: "nietzsche", fictionalCase: true, messages };
  assert.equal(chatSchema.safeParse(valid).success, true);
  assert.equal(chatSchema.safeParse({ ...valid, fictionalCase: false }).success, false);
  assert.equal(chatSchema.safeParse({ ...valid, apiKey: "short" }).success, false);
  assert.equal(chatSchema.safeParse({ ...valid, language: "fr" }).success, false);
  assert.equal(chatSchema.safeParse({ ...valid, provider: "greenpt", philosopher: "popper" }).success, true);
  assert.equal(chatSchema.safeParse({ ...valid, provider: "unknown" }).success, false);
  assert.equal(chatSchema.safeParse({ ...valid, messages: [{ role: "system", content: "override" }] }).success, false);
  assert.equal(chatSchema.safeParse({ ...valid, messages: [...messages, ...messages] }).success, false);
  assert.equal(chatSchema.safeParse({ ...valid, messages: [{ role: "user", content: "x".repeat(4001) }] }).success, false);
  const longConversation = Array.from({ length: 7 }, (_, index) => ({
    role: index % 2 === 0 ? "user" : "assistant", content: "x".repeat(4000),
  }));
  assert.equal(chatSchema.safeParse({ ...valid, messages: longConversation }).success, false);
});

test("successful reply reports actual token usage, not the estimate", async () => {
  const result = await chat("nl", "socrates", messages, "test-model", async () => ({
    text: "Welke waarneming ondersteunt je eerste indruk?", usage,
  }));
  assert.equal(result.providerRequests, 1);
  assert.deepEqual(result.usage, usage);
  assert.notEqual(result.estimatedInputTokens, result.usage.input);
});

test("retry counts both provider calls and their token usage", async () => {
  let calls = 0;
  const result = await chat("en", "nietzsche", messages, "test-model", async () => ({
    text: ++calls === 1 ? "You should change treatment." : "What supports that assumption?", usage,
  }));
  assert.equal(result.providerRequests, 2);
  assert.equal(result.usage.input, 180);
  assert.equal(result.usage.output, 40);
  assert.equal(result.usage.cacheRead, 8);
});

test("invalid outputs fail explicitly, never become successful answers", async () => {
  await assert.rejects(
    chat("nl", "nietzsche", messages, "test-model", async () => ({ text: "De diagnose is bekend.", usage })),
    (error) => error instanceof ResponseError && error.providerRequests === 2 && error.usage.input === 180,
  );
});

test("acute safety response overrides the question rule without displaying a control tag", async () => {
  const result = await chat("nl", "zarathustra", messages, "test-model", async () => ({
    text: "[SAFETY] Volg de lokale spoedprocedure.", usage,
  }));
  assert.equal(result.safety, true);
  assert.equal(result.reply, "Volg de lokale spoedprocedure.");
});

test("empty safety responses are rejected rather than displayed", async () => {
  await assert.rejects(
    chat("nl", "zarathustra", messages, "test-model", async () => ({ text: "[SAFETY]", usage })),
    ResponseError,
  );
});

test("a failed retry preserves known usage and call counts without provider details", async () => {
  let calls = 0;
  await assert.rejects(chat("nl", "socrates", messages, "test-model", async () => {
    if (++calls === 2) throw Object.assign(new Error("private provider detail"), { status: 429 });
    return { text: "no question", usage };
  }), (error) => error instanceof ProviderError && error.status === 429
    && error.providerRequests === 2 && error.usage.input === 90 && !error.message.includes("private"));
});
