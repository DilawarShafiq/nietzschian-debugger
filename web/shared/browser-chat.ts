import { z } from "zod";
import { chat, chatSchema, ProviderError, ResponseError } from "./chat.js";
import { completion, DEFAULT_MODELS } from "./providers.js";
import type { ChatError, ChatResponse } from "./prompts.js";

export function browserChatError(error: unknown): ChatError {
  if (error instanceof ResponseError) {
    return { error: "INVALID_RESPONSE", usage: error.usage, providerRequests: error.providerRequests };
  }
  if (error instanceof ProviderError) {
    return {
      error: error.networkFailure ? "PROVIDER_NETWORK"
        : error.status === 403 ? "PROVIDER_FORBIDDEN"
        : error.status === 401 ? "PROVIDER_AUTH"
        : error.status === 429 ? "PROVIDER_RATE_LIMIT" : "PROVIDER_UNAVAILABLE",
      usage: error.usage, providerRequests: error.providerRequests,
    };
  }
  if (error instanceof z.ZodError) return { error: "INVALID_REQUEST" };
  if (error instanceof Error && error.message === "MISSING_KEY") return { error: "MISSING_KEY" };
  return { error: "PROVIDER_UNAVAILABLE" };
}

export async function browserChat(input: unknown, fetcher: typeof fetch = fetch): Promise<ChatResponse> {
  const parsed = chatSchema.parse(input);
  const { apiKey, provider, language, philosopher, messages } = parsed;
  if (!apiKey) throw new Error("MISSING_KEY");
  const model = DEFAULT_MODELS[provider];
  const complete = completion(provider, apiKey, model, fetcher, { browser: true });
  return { ...await chat(language, philosopher, messages, model, complete), provider };
}
