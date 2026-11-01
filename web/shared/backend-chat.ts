import { z } from "zod";
import { chatSchema } from "./chat.js";
import type { ChatError, ChatResponse } from "./prompts.js";

const count = z.number().int().nonnegative();
const usage = z.object({ input: count, output: count, cacheRead: count, cacheWrite: count });
const resultSchema = z.object({
  reply: z.string().min(1), safety: z.boolean(), usage,
  model: z.string(), provider: z.enum(["claude", "greenpt"]),
  providerRequests: count, estimatedInputTokens: count,
});
const errorSchema = z.object({
  error: z.enum([
    "INVALID_REQUEST", "MISSING_KEY", "PROVIDER_AUTH", "PROVIDER_RATE_LIMIT",
    "PROVIDER_UNAVAILABLE", "PROVIDER_NETWORK", "PROVIDER_FORBIDDEN",
    "INVALID_RESPONSE", "RATE_LIMIT", "FORBIDDEN", "BACKEND_AUTH", "BACKEND_UNAVAILABLE",
  ]),
  usage: usage.optional(), providerRequests: count.optional(),
});

export class BackendChatError extends Error {
  constructor(public failure: ChatError) { super(failure.error); }
}

export function backendOrigin(value: string): string {
  const url = new URL(value);
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if ((url.protocol !== "https:" && !(local && url.protocol === "http:"))
    || url.username || url.password || url.search || url.hash || url.pathname !== "/") {
    throw new Error("Backend must be an HTTPS origin (HTTP allowed only on localhost).");
  }

  return url.origin;
}

export async function validateBackend(origin: string, token: string, provider: "claude" | "greenpt"): Promise<string> {
    let response: Response;
    let body: unknown;
    try {
      response = await fetch(`${backendOrigin(origin)}/api/validate`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
        body: JSON.stringify({ provider }), signal: AbortSignal.timeout(20000),
      });
      body = await response.json();
    } catch (error) {
      if (error instanceof TypeError || error instanceof SyntaxError || error instanceof DOMException) {
        throw new BackendChatError({ error: "BACKEND_UNAVAILABLE" });
      }
      throw error;
    }
    if (!response.ok) {
      const failure = errorSchema.safeParse(body);
      throw new BackendChatError(failure.success ? failure.data : { error: "BACKEND_UNAVAILABLE" });
    }
    const result = z.object({ provider: z.literal(provider), model: z.string().min(1) }).safeParse(body);
    if (!result.success) throw new BackendChatError({ error: "BACKEND_UNAVAILABLE" });
    return result.data.model;
  }
export async function backendChat(
  origin: string, token: string, input: unknown, fetcher: typeof fetch = fetch,
): Promise<ChatResponse> {
  const parsed = chatSchema.parse(input);
  if (!token.trim()) throw new BackendChatError({ error: "BACKEND_AUTH" });
  const url = `${backendOrigin(origin)}/api/chat`;
  let response: Response;
  let body: unknown;
  try {
    response = await fetcher(url, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      signal: AbortSignal.timeout(100000),
      body: JSON.stringify(parsed),
    });
    body = await response.json();
  } catch (error) {
    if (error instanceof TypeError || error instanceof SyntaxError || error instanceof DOMException) {
      throw new BackendChatError({ error: "BACKEND_UNAVAILABLE" });
    }
    throw error;
  }
  if (!response.ok) {
    const failure = errorSchema.safeParse(body);
    throw new BackendChatError(failure.success ? failure.data : { error: "BACKEND_UNAVAILABLE" });
  }
  const result = resultSchema.safeParse(body);
  if (!result.success || result.data.provider !== parsed.provider) {
    throw new BackendChatError({ error: "BACKEND_UNAVAILABLE" });
  }
  return result.data;
}
