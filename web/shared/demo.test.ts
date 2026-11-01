import assert from "node:assert/strict";
import { test } from "node:test";
import { customDemoReply, demoQuestions, demoReply, initialDemoTopics, type DemoTopic } from "./demo.js";
import type { Language, Philosopher } from "./prompts.js";

test("every demo option has a single reflection question in both languages for every lens", () => {
  for (const topic of Object.keys(demoQuestions) as DemoTopic[]) {
    for (const language of ["nl", "en"] as Language[]) {
      assert.ok(demoQuestions[topic].label[language].length > 10);
      for (const philosopher of ["socrates", "nietzsche", "zarathustra"] as Philosopher[]) {
        const reply = demoReply(topic, language, philosopher);
        assert.equal(reply.split("?").length, 2);
        assert.equal(reply, demoReply(topic, language, philosopher));
      }
    }
    assert.equal(demoQuestions[topic].next.length, 3);
    for (const next of demoQuestions[topic].next) assert.ok(demoQuestions[next]);
  }
  assert.equal(initialDemoTopics.length, 3);
});

test("custom text gets a clear no-LLM notice rather than a simulated clinical answer", () => {
  assert.equal(demoReply(undefined, "nl", "nietzsche"), customDemoReply.nl);
  assert.match(demoReply(undefined, "en", "socrates"), /no actual LLM integration/);
});

test("changing the philosopher changes the scripted reflection", () => {
  assert.notEqual(demoReply("assumptions", "nl", "socrates"), demoReply("assumptions", "nl", "nietzsche"));
});
