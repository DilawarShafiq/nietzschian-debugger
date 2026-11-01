import assert from "node:assert/strict";
import { test } from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";
import { MessageContent } from "./MessageContent.js";

const render = (content: string) => renderToStaticMarkup(createElement(MessageContent, { content }));

test("renders emphasis, strong text, paragraphs and lists as HTML", () => {
  const result = render("Wat ik *wel* kan.\n\n**Welke aanname toets je?**\n\n- Observatie\n- Interpretatie");
  assert.match(result, /<em>wel<\/em>/);
  assert.match(result, /<strong>Welke aanname toets je\?<\/strong>/);
  assert.match(result, /<ul>/);
  assert.match(result, /<li>Observatie<\/li>/);
});

test("does not run raw HTML, unsafe links or load remote images", () => {
  const result = render('<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n[click](javascript:alert%281%29)\n\n![tracking](https://example.com/track.png)');
  assert.ok(!result.includes("<script"));
  assert.ok(!result.includes("<img"));
  assert.ok(!result.includes("javascript:"));
  assert.ok(!result.includes("onerror"));
  assert.ok(!result.includes("https://example.com/track.png"));
});
