import dotenv from "dotenv";
import express from "express";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createApp } from "./app.js";
import { completion } from "./providers.js";
import type { Provider } from "../shared/prompts.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const production = here.includes(`${path.sep}dist${path.sep}server${path.sep}`);
const root = path.resolve(here, production ? "../../.." : "..");
dotenv.config({ path: path.join(root, ".env"), quiet: true });
dotenv.config({ path: path.join(root, "../.env"), quiet: true });

const keys: Record<Provider, string | undefined> = {
  claude: process.env.ANTHROPIC_API_KEY?.trim(),
  greenpt: process.env.GREENPT_API_KEY?.trim(),
};
const models: Record<Provider, string> = {
  claude: process.env.CLAUDE_MODEL || "claude-haiku-4-5-20251001",
  greenpt: process.env.GREENPT_MODEL || "mistral-small-3.2-24b-instruct-2506",
};
const frontendOrigin = process.env.FRONTEND_ORIGIN;
const accessToken = process.env.BACKEND_ACCESS_TOKEN?.trim();
if (process.env.ALLOW_SERVER_KEY === "true" && (!accessToken || accessToken.length < 32)) {
  throw new Error("Server-key access requires BACKEND_ACCESS_TOKEN with at least 32 characters.");
}
if (frontendOrigin && new URL(frontendOrigin).origin !== frontendOrigin) {
  throw new Error("FRONTEND_ORIGIN must be an exact origin, without a path or trailing slash.");
}
const app = createApp(models, (userKey, provider) => {
  // Public demos require visitors' own keys unless explicitly enabled by the operator.
  const key = userKey || (!frontendOrigin || process.env.ALLOW_SERVER_KEY === "true" ? keys[provider] : undefined);
  if (!key) return null;
  return completion(provider, key, models[provider]);
}, frontendOrigin, accessToken);

if (process.env.API_ONLY === "true") {
  app.use((_request, response) => response.sendStatus(404));
} else if (production) {
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
  console.log(`Nietzschian AI Clinician: http://${host}:${port}`);
  if (!keys.claude && !keys.greenpt) console.warn("No server keys configured; enter a temporary provider key in the UI.");
});
server.on("error", (error) => {
  console.error("Web server could not start.", error.message);
  process.exit(1);
});
