import Anthropic from "@anthropic-ai/sdk";
import dotenv from "dotenv";
import express from "express";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createApp } from "./app.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const production = here.includes(`${path.sep}dist${path.sep}server${path.sep}`);
const root = path.resolve(here, production ? "../../.." : "..");
dotenv.config({ path: path.join(root, ".env"), quiet: true });
dotenv.config({ path: path.join(root, "../.env"), quiet: true });

const apiKey = process.env.ANTHROPIC_API_KEY?.trim();
const model = process.env.CLAUDE_MODEL || "claude-haiku-4-5-20251001";
const frontendOrigin = process.env.FRONTEND_ORIGIN;
if (frontendOrigin && new URL(frontendOrigin).origin !== frontendOrigin) {
  throw new Error("FRONTEND_ORIGIN must be an exact origin, without a path or trailing slash.");
}
const app = createApp(model, (userKey) => {
  // Public demos require visitors' own keys unless explicitly enabled by the operator.
  const key = userKey || (!frontendOrigin || process.env.ALLOW_SERVER_KEY === "true" ? apiKey : undefined);
  if (!key) return null;
  const client = new Anthropic({ apiKey: key, maxRetries: 0, timeout: 45000 });
  return async (system, messages) => {
    const result = await client.messages.create({ model, system, messages, max_tokens: 512 });
    return {
      text: result.stop_reason === "max_tokens" ? "" :
        result.content.filter((block) => block.type === "text").map((block) => block.text).join("\n"),
      usage: {
        input: result.usage.input_tokens,
        output: result.usage.output_tokens,
        cacheRead: result.usage.cache_read_input_tokens || 0,
        cacheWrite: result.usage.cache_creation_input_tokens || 0,
      },
    };
  };
}, frontendOrigin);

if (production) {
  const clientPath = path.join(root, "dist/client");
  if (!existsSync(path.join(clientPath, "index.html"))) throw new Error("Run npm run build before npm start.");
  app.use(express.static(clientPath));
  app.get("/{*path}", (_request, response) => response.sendFile(path.join(clientPath, "index.html")));
} else {
  const { createServer } = await import("vite");
  const vite = await createServer({ root, server: { middlewareMode: true }, appType: "spa" });
  app.use(vite.middlewares);
}

const port = Number(process.env.PORT || 3080);
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error("PORT must be between 1 and 65535.");
const host = process.env.HOST || "127.0.0.1";
const server = app.listen(port, host, () => {
  console.log(`Nietzschian AI Clinician: http://${host}:${port} (${model})`);
  if (!apiKey) console.warn("Add ANTHROPIC_API_KEY to web/.env; live chat is currently unavailable.");
});
server.on("error", (error) => {
  console.error("Web server could not start.", error.message);
  process.exit(1);
});
