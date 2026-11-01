import express from "express";
import { rateLimit } from "express-rate-limit";
import { chat, chatSchema, ProviderError, ResponseError, type Complete } from "./chat.js";

export type CompletionFactory = (apiKey?: string) => Complete | null;

export function createApp(model: string, completionFactory: CompletionFactory, frontendOrigin?: string) {
  const app = express();
  app.disable("x-powered-by");
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
      response.setHeader("Access-Control-Allow-Headers", "Content-Type");
    }
    if (request.method === "OPTIONS") { response.sendStatus(204); return; }
    next();
  });
  app.use("/api/chat", rateLimit({
    windowMs: 10 * 60 * 1000,
    limit: 20,
    standardHeaders: "draft-8",
    legacyHeaders: false,
    handler: (_request, response) => {
      console.warn("Chat request rejected: local rate limit.");
      response.status(429).json({ error: "RATE_LIMIT" });
    },
  }));
  app.post("/api/chat", express.json({ limit: "128kb" }), async (request, response) => {
    const parsed = chatSchema.safeParse(request.body);
    if (!parsed.success) {
      console.warn("Chat request rejected: invalid payload.");
      response.status(400).json({ error: "INVALID_REQUEST" });
      return;
    }
    const complete = completionFactory(parsed.data.apiKey);
    if (!complete) {
      console.warn("Chat unavailable: ANTHROPIC_API_KEY is not configured.");
      response.status(503).json({ error: "MISSING_KEY" });
      return;
    }
    try {
      const { language, philosopher, messages } = parsed.data;
      response.json(await chat(language, philosopher, messages, model, complete));
    } catch (error) {
      if (error instanceof ResponseError) {
        console.warn("Claude response rejected after retry.");
        response.status(502).json({
          error: "INVALID_RESPONSE", usage: error.usage, claudeRequests: error.claudeRequests,
        });
        return;
      }
      const status = error instanceof ProviderError ? error.status : undefined;
      console.error("Claude request failed.", { status: typeof status === "number" ? status : "unknown" });
      const code = status === 401 || status === 403 ? "PROVIDER_AUTH"
        : status === 429 ? "PROVIDER_RATE_LIMIT" : "PROVIDER_UNAVAILABLE";
      response.status(status === 429 ? 429 : 502).json({
        error: code,
        ...(error instanceof ProviderError ? { usage: error.usage, claudeRequests: error.claudeRequests } : {}),
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
