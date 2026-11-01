import { z } from "zod";
import {
  estimateInputTokens, systemPrompt,
  type ChatMessage, type ChatResponse, type Language, type Philosopher, type TokenUsage,
} from "../shared/prompts.js";

export const chatSchema = z.strictObject({
  language: z.enum(["nl", "en"]),
  philosopher: z.enum(["socrates", "nietzsche", "zarathustra"]),
  fictionalCase: z.literal(true),
  apiKey: z.string().trim().min(10).max(300).optional(),
  messages: z.array(z.strictObject({
    role: z.enum(["user", "assistant"]),
    content: z.string().trim().min(1).max(4000),
  })).min(1).max(31),
}).superRefine((value, context) => {
  if (value.messages.some((message, index) => message.role !== (index % 2 === 0 ? "user" : "assistant"))
    || value.messages.at(-1)?.role !== "user") {
    context.addIssue({ code: "custom", message: "Messages must alternate, starting and ending with user." });
  }
  if (value.messages.reduce((sum, message) => sum + message.content.length, 0) > 24000) {
    context.addIssue({ code: "custom", message: "Conversation is too long." });
  }
});

export type Completion = { text: string; usage: TokenUsage };
export type Complete = (system: string, messages: ChatMessage[]) => Promise<Completion>;

export class ResponseError extends Error {
  constructor(public usage: TokenUsage, public claudeRequests: number) {
    super("Claude response failed reflection constraints.");
  }
}

export class ProviderError extends Error {
  constructor(public status: number | undefined, public usage: TokenUsage, public claudeRequests: number) {
    super("Claude request failed.");
  }
}

export function isReflectiveResponse(text: string): boolean {
  return text.split("?").length === 2
    && !/\b(you should|you must|the diagnosis is|prescribe|start treatment|u moet|je moet|de diagnose is|schrijf .{0,30}voor|start .{0,20}behandeling)\b/i.test(text);
}

export async function chat(
  language: Language,
  philosopher: Philosopher,
  messages: ChatMessage[],
  model: string,
  complete: Complete,
): Promise<ChatResponse> {
  const system = systemPrompt(language, philosopher);
  const usage: TokenUsage = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };
  let claudeRequests = 0;
  let attemptMessages = messages;

  for (let attempt = 0; attempt < 2; attempt++) {
    claudeRequests++;
    let result: Completion;
    try {
      result = await complete(system, attemptMessages);
    } catch (error) {
      const status = error instanceof Error && "status" in error && typeof error.status === "number"
        ? error.status : undefined;
      throw new ProviderError(status, usage, claudeRequests);
    }
    for (const key of ["input", "output", "cacheRead", "cacheWrite"] as const) usage[key] += result.usage[key];
    const text = result.text.trim();
    const safety = text.startsWith("[SAFETY]");
    const reply = safety ? text.slice("[SAFETY]".length).trim() : text;
    if (reply && (safety || isReflectiveResponse(reply))) {
      return {
        reply, safety, usage, model, claudeRequests,
        estimatedInputTokens: estimateInputTokens(language, philosopher, messages),
      };
    }
    attemptMessages = [
      ...messages,
      { role: "assistant", content: text || "(empty response)" },
      {
        role: "user",
        content: language === "nl"
          ? "Herschrijf als precies één open reflectievraag zonder diagnose, antwoord of behandeladvies. Behoud de veiligheidsuitzondering alleen bij acute onveiligheid."
          : "Rewrite as exactly one open reflection question without a diagnosis, answer, or treatment advice. Preserve the safety exception only for acute danger.",
      },
    ];
  }
  throw new ResponseError(usage, claudeRequests);
}
