import type { Turn } from '../types.js';
import { callLLM, getConversationModel, countTokens } from '../llm/client.js';

const TOKEN_THRESHOLD_RATIO = 0.8;
const MAX_CONTEXT_TOKENS = 200_000;
const TOKEN_THRESHOLD = MAX_CONTEXT_TOKENS * TOKEN_THRESHOLD_RATIO; // 160K
const CHARS_PER_TOKEN = 4;
const PRESERVE_RECENT_TURNS = 8;

const SUMMARY_SYSTEM_PROMPT = `You are a precise conversation summarizer. Compress the following debug session turns into a single paragraph that preserves:
- The developer's key hypotheses (stated and rejected)
- Observable behaviors (guessing without evidence, checking assumptions, etc.)
- The current state of understanding at the end of these turns
- Any files or code elements mentioned

Do not editorialize. Do not add new information. Output only the summary paragraph.`;

export interface MessageArray {
  messages: Array<{ role: 'user' | 'assistant'; content: string }>;
  rollingSummary?: string;
}

export function buildMessageArray(
  turns: Turn[],
  rollingSummary?: string,
): MessageArray {
  const messages: Array<{ role: 'user' | 'assistant'; content: string }> = [];

  if (rollingSummary) {
    // Summary is implicitly available via system prompt, not as a message
  }

  for (const turn of turns) {
    if (turn.question) {
      messages.push({ role: 'assistant', content: turn.question });
    }
    if (turn.response) {
      messages.push({ role: 'user', content: turn.response });
    }
  }

  return { messages, rollingSummary };
}

export function estimateTokens(systemPrompt: string, messages: Array<{ role: 'user' | 'assistant'; content: string }>): number {
  let totalChars = systemPrompt.length;
  for (const msg of messages) {
    totalChars += msg.content.length;
  }
  return Math.ceil(totalChars / CHARS_PER_TOKEN);
}

export function shouldSummarize(estimatedTokens: number): boolean {
  return estimatedTokens > TOKEN_THRESHOLD;
}

export async function summarizeOldTurns(
  turns: Turn[],
  existingSummary?: string,
): Promise<{ summary: string; recentTurns: Turn[] }> {
  if (turns.length <= PRESERVE_RECENT_TURNS) {
    return { summary: existingSummary ?? '', recentTurns: turns };
  }

  const oldTurns = turns.slice(0, -PRESERVE_RECENT_TURNS);
  const recentTurns = turns.slice(-PRESERVE_RECENT_TURNS);

  const turnsText = oldTurns
    .map((t) => `Turn ${t.turnNumber}:\nQuestion: ${t.question}\nDeveloper: ${t.response}`)
    .join('\n\n');

  const toSummarize = existingSummary
    ? `Previous summary: ${existingSummary}\n\nNew turns to incorporate:\n${turnsText}`
    : turnsText;

  const summary = await callLLM(
    SUMMARY_SYSTEM_PROMPT,
    [{ role: 'user', content: toSummarize }],
    getConversationModel(),
  );

  return { summary, recentTurns };
}

export async function checkAndSummarize(
  systemPrompt: string,
  turns: Turn[],
  existingSummary?: string,
): Promise<{ turns: Turn[]; summary?: string }> {
  const msgArray = buildMessageArray(turns, existingSummary);
  const estimated = estimateTokens(systemPrompt, msgArray.messages);

  if (!shouldSummarize(estimated)) {
    return { turns, summary: existingSummary };
  }

  // Verify with exact count
  try {
    const exact = await countTokens(systemPrompt, msgArray.messages, getConversationModel());
    if (exact <= TOKEN_THRESHOLD) {
      return { turns, summary: existingSummary };
    }
  } catch {
    // If count_tokens fails, proceed with summarization based on estimate
  }

  const result = await summarizeOldTurns(turns, existingSummary);
  return { turns: result.recentTurns, summary: result.summary };
}
