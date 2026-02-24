import Anthropic from '@anthropic-ai/sdk';

const HAIKU_MODEL = 'claude-haiku-4-5-20251001';
const SONNET_MODEL = 'claude-sonnet-4-6';

let client: Anthropic | null = null;
const analyzedFiles = new Set<string>();

export function getClient(): Anthropic {
  if (!client) {
    const apiKey = process.env['ANTHROPIC_API_KEY'];
    if (!apiKey) {
      throw new MissingApiKeyError();
    }
    client = new Anthropic({ apiKey, maxRetries: 2 });
  }
  return client;
}

export class MissingApiKeyError extends Error {
  constructor() {
    super('ANTHROPIC_API_KEY environment variable is not set.');
    this.name = 'MissingApiKeyError';
  }
}

export function getModelForFile(filePath: string): string {
  if (analyzedFiles.has(filePath)) {
    return HAIKU_MODEL;
  }
  analyzedFiles.add(filePath);
  return SONNET_MODEL;
}

export function getConversationModel(): string {
  return HAIKU_MODEL;
}

export interface StreamCallbacks {
  onText: (text: string) => void;
  onComplete: (fullText: string) => void;
  onError: (error: Error) => void;
}

export async function streamQuestion(
  systemPrompt: string,
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  model: string,
  callbacks: StreamCallbacks,
): Promise<string> {
  const anthropic = getClient();
  let fullText = '';

  try {
    const stream = anthropic.messages.stream({
      model,
      max_tokens: 1024,
      system: systemPrompt,
      messages,
    });

    stream.on('text', (text) => {
      fullText += text;
      callbacks.onText(text);
    });

    await stream.finalMessage();
    callbacks.onComplete(fullText);
    return fullText;
  } catch (error) {
    callbacks.onError(error instanceof Error ? error : new Error(String(error)));
    throw error;
  }
}

export async function countTokens(
  systemPrompt: string,
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  model: string,
): Promise<number> {
  const anthropic = getClient();
  const result = await anthropic.messages.countTokens({
    model,
    system: systemPrompt,
    messages,
  });
  return result.input_tokens;
}

export async function callLLM(
  systemPrompt: string,
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  model: string,
): Promise<string> {
  const anthropic = getClient();
  const response = await anthropic.messages.create({
    model,
    max_tokens: 1024,
    system: systemPrompt,
    messages,
  });
  const block = response.content[0];
  if (block.type === 'text') {
    return block.text;
  }
  return '';
}

export function resetAnalyzedFiles(): void {
  analyzedFiles.clear();
}
