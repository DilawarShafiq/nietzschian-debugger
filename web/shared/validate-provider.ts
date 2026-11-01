import { z } from "zod";
import { ProviderError } from "./chat.js";
import { DEFAULT_MODELS } from "./providers.js";
import type { Provider } from "./prompts.js";

export const validationSchema = z.strictObject({
  provider: z.enum(["claude", "greenpt"]),
  apiKey: z.string().trim().min(10).max(300).optional(),
});

export async function validateProvider(
  provider: Provider, key: string, model = DEFAULT_MODELS[provider],
  fetcher: typeof fetch = fetch, browser = false,
): Promise<string> {
  const usage = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };
  let response: Response;
  try {
    response = await fetcher(provider === "claude"
      ? `https://api.anthropic.com/v1/models/${encodeURIComponent(model)}`
      : "https://api.greenpt.ai/v1/models", {
      headers: provider === "claude" ? {
        "x-api-key": key, "anthropic-version": "2023-06-01",
        ...(browser ? { "anthropic-dangerous-direct-browser-access": "true" } : {}),
      } : { Authorization: `Bearer ${key}` },
      signal: AbortSignal.timeout(15000),
    });
  } catch (error) {
    if (error instanceof TypeError || error instanceof DOMException) {
      throw new ProviderError(undefined, usage, 0, true);
    }
    throw error;
  }
  if (!response.ok) throw new ProviderError(response.status, usage, 0);
  const body: unknown = await response.json();
  if (provider === "claude") {
    z.object({ id: z.string().min(1) }).parse(body);
  } else {
    const catalogue = z.object({ data: z.array(z.object({ id: z.string() })) }).parse(body);
    if (!catalogue.data.some(entry => entry.id === model)) throw new ProviderError(404, usage, 0);
  }
  return model;
}
