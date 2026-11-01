import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import { z } from "zod";
import type { ChatMessage, Provider, TokenUsage } from "./prompts.js";
import { ProviderNetworkError, type Complete } from "./chat.js";

export const GREENPT_BASE_URL = "https://api.greenpt.ai/v1";
export const DEFAULT_MODELS: Record<Provider, string> = {
  claude: "claude-haiku-4-5-20251001",
  greenpt: "mistral-small-3.2-24b-instruct-2506",
};
export const PROVIDER_ENDPOINTS: Record<Provider, string> = {
  claude: "https://api.anthropic.com/v1/messages",
  greenpt: `${GREENPT_BASE_URL}/chat/completions`,
};
const tokenCount = z.number().int().nonnegative();
const greenUsageSchema = z.object({
  prompt_tokens: tokenCount,
  completion_tokens: tokenCount,
  prompt_tokens_details: z.object({ cached_tokens: tokenCount.optional() }).optional(),
});

export function greenUsage(value: unknown): TokenUsage {
  const usage = greenUsageSchema.parse(value);
  const cacheRead = usage.prompt_tokens_details?.cached_tokens || 0;
  if (cacheRead > usage.prompt_tokens) throw new Error("Invalid provider cache usage.");
  return {
    input: usage.prompt_tokens - cacheRead,
    output: usage.completion_tokens,
    cacheRead,
    cacheWrite: 0,
  };
}

export function greenMessages(system: string, messages: ChatMessage[]) {
  return [{ role: "system" as const, content: system }, ...messages];
}

function withNetworkErrors(complete: Complete): Complete {
  return async (system, messages) => {
    try {
      return await complete(system, messages);
    } catch (error) {
      if (error instanceof Anthropic.APIConnectionError || error instanceof OpenAI.APIConnectionError) {
        throw new ProviderNetworkError();
      }
      throw error;
    }
  };
}

export function completion(
  provider: Provider, key: string, model: string, fetcher: typeof fetch = fetch,
  { browser = false }: { browser?: boolean } = {},
): Complete {
  if (provider === "greenpt") {
    const client = new OpenAI({
      apiKey: key, baseURL: GREENPT_BASE_URL, maxRetries: 0, timeout: 45000,
      fetch: fetcher, dangerouslyAllowBrowser: browser,
    });
    return withNetworkErrors(async (system, messages) => {
      const result = await client.chat.completions.create({
        model, messages: greenMessages(system, messages), max_tokens: 512, stream: false,
      });
      const choice = result.choices[0];
      return {
        text: choice?.finish_reason === "stop" ? choice.message.content || "" : "",
        usage: greenUsage(result.usage),
      };
    });
  }
  const client = new Anthropic({
    apiKey: key, maxRetries: 0, timeout: 45000,
    fetch: fetcher, dangerouslyAllowBrowser: browser,
  });
  return withNetworkErrors(async (system, messages) => {
    const result = await client.messages.create({ model, system, messages, max_tokens: 512 });
    return {
      text: result.stop_reason === "max_tokens" ? "" :
        result.content.filter((block) => block.type === "text").map((block) => block.text).join("\n"),
      usage: {
        input: result.usage.input_tokens, output: result.usage.output_tokens,
        cacheRead: result.usage.cache_read_input_tokens || 0,
        cacheWrite: result.usage.cache_creation_input_tokens || 0,
      },
    };
  });
}
