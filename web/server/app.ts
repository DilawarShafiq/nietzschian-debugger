import express from "express";
import { rateLimit } from "express-rate-limit";
import { chat, chatSchema, ProviderError, ResponseError, type Complete } from "./chat.js";
import type { Provider } from "../shared/prompts.js";
import { timingSafeEqual } from "node:crypto";
import { validationSchema } from "../shared/validate-provider.js";

export type CompletionFactory = (apiKey: string | undefined, provider: Provider) => Complete | null;

export function createApp(
  models: Record<Provider, string>, completionFactory: CompletionFactory,
  frontendOrigin?: string, accessToken?: string,
  validateConnection?: (key: string | undefined, provider: Provider) => Promise<string>,
) {
  const app = express();
  app.disable("x-powered-by");
  app.get("/healthz", (_request, response) => response.json({ status: "ok" }));
  app.use((_request, response, next) => {
    response.setHeader("Referrer-Policy", "no-referrer");
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setHeader("X-Frame-Options", "DENY");
    next();
  });
  app.use("/api", (_request, response, next) => {
    response.setHeader("Cache-Control", "no-store");
    next();
  });
  app.use("/api", (request, response, next) => {
    const origin = request.get("origin");
    if (origin && origin !== `${request.protocol}://${request.get("host")}` && origin !== frontendOrigin) {
      console.warn("Chat request rejected: cross-origin request.");
      response.status(403).json({ error: "FORBIDDEN" });
      return;
    }
    if (origin && origin === frontendOrigin) {
      response.setHeader("Access-Control-Allow-Origin", origin);
      response.setHeader("Vary", "Origin");
      response.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
      response.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }
    if (request.method === "OPTIONS") { response.sendStatus(204); return; }
    next();
  });
  app.use(["/api/chat", "/api/validate"], rateLimit({
    windowMs: 10 * 60 * 1000,
    limit: 20,
    standardHeaders: "draft-8",
    legacyHeaders: false,
    handler: (_request, response) => {
      console.warn("Chat request rejected: local rate limit.");
      response.status(429).json({ error: "RATE_LIMIT" });
    },
  }));
  app.use(["/api/chat", "/api/validate"], (request, response, next) => {
    if (accessToken) {
      const expected = Buffer.from(`Bearer ${accessToken}`);
      const received = Buffer.from(request.get("authorization") || "");
      if (received.length !== expected.length || !timingSafeEqual(received, expected)) {
        console.warn("Chat request rejected: backend authentication.");
        response.status(401).json({ error: "BACKEND_AUTH" });
        return;
      }
    }
    next();
  });
  app.post("/api/validate", express.json({ limit: "4kb" }), async (request, response) => {
    const parsed = validationSchema.safeParse(request.body);
    if (!parsed.success) {
      console.warn("Connection validation rejected: invalid payload.");
      response.status(400).json({ error: "INVALID_REQUEST" }); return;
    }
    if (!validateConnection) {
      console.warn("Connection validation unavailable.");
      response.status(503).json({ error: "PROVIDER_UNAVAILABLE" }); return;
    }
    try {
      const model = await validateConnection(parsed.data.apiKey, parsed.data.provider);
      response.json({ model, provider: parsed.data.provider });
    } catch (error) {
      const status = error instanceof ProviderError ? error.status : undefined;
      console.warn("Connection validation failed.", { provider: parsed.data.provider, status });
      const code = error instanceof Error && error.message === "MISSING_KEY" ? "MISSING_KEY"
        : status === 401 ? "PROVIDER_AUTH" : status === 403 ? "PROVIDER_FORBIDDEN"
        : status === 429 ? "PROVIDER_RATE_LIMIT" : "PROVIDER_UNAVAILABLE";
      response.status(502).json({ error: code });
    }
  });
  app.post("/api/chat", express.json({ limit: "128kb" }), async (request, response) => {
    const parsed = chatSchema.safeParse(request.body);
    if (!parsed.success) {
      console.warn("Chat request rejected: invalid payload.");
      response.status(400).json({ error: "INVALID_REQUEST" });
      return;
    }
    const { provider } = parsed.data;
    try {
      const complete = completionFactory(parsed.data.apiKey, provider);
      if (!complete) {
        console.warn("Chat unavailable: provider key is not configured.", { provider });
        response.status(503).json({ error: "MISSING_KEY" });
        return;
      }
      const { language, philosopher, messages } = parsed.data;
      response.json({ ...await chat(language, philosopher, messages, models[provider], complete), provider });
    } catch (error) {
      if (error instanceof ResponseError) {
        console.warn("Model response rejected after retry.", { provider });
        response.status(502).json({
          error: "INVALID_RESPONSE", usage: error.usage, providerRequests: error.providerRequests,
        });
        return;
      }
      const status = error instanceof ProviderError ? error.status : undefined;
      console.error("Model request failed.", { provider, status: typeof status === "number" ? status : "unknown" });
      const code = status === 403 ? "PROVIDER_FORBIDDEN" : status === 401 ? "PROVIDER_AUTH"
        : status === 429 ? "PROVIDER_RATE_LIMIT" : "PROVIDER_UNAVAILABLE";
      response.status(status === 429 ? 429 : 502).json({
        error: code,
        ...(error instanceof ProviderError ? { usage: error.usage, providerRequests: error.providerRequests } : {}),
      });
    }
  });
  app.use("/api", (_request, response) => response.status(404).json({ error: "INVALID_REQUEST" }));
  app.use((error: unknown, _request: express.Request, response: express.Response, next: express.NextFunction) => {
    if (!error) { next(); return; }
    console.warn("Request body rejected.");
    response.status(400).json({ error: "INVALID_REQUEST" });
  });
  return app;
}
