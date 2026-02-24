import { callLLM, getConversationModel } from './client.js';
import type { Intensity } from '../types.js';

const ANSWER_PATTERNS = [
  /\bthe fix is\b/i,
  /\byou should change\b/i,
  /\btry doing\b/i,
  /\btry changing\b/i,
  /\btry replacing\b/i,
  /\bhere'?s (?:the|a) (?:fix|solution|answer)\b/i,
  /\bto fix this\b/i,
  /\bthe solution is\b/i,
  /\bjust (?:change|replace|update|add|remove)\b/i,
  /\byou need to (?:change|replace|update|add|remove)\b/i,
];

const CODE_FIX_PATTERN = /```[\s\S]*?(?:\/\/\s*fix|\/\/\s*changed|\/\/\s*updated|→|=>.*fix)[\s\S]*?```/i;

export function validateResponse(response: string): { valid: boolean; reason?: string } {
  const hasQuestion = response.includes('?');
  if (!hasQuestion) {
    return { valid: false, reason: 'Response contains no question' };
  }

  for (const pattern of ANSWER_PATTERNS) {
    if (pattern.test(response)) {
      return { valid: false, reason: `Response matches answer pattern: ${pattern.source}` };
    }
  }

  if (CODE_FIX_PATTERN.test(response)) {
    return { valid: false, reason: 'Response contains a code fix block' };
  }

  return { valid: true };
}

export async function repromptIfInvalid(
  systemPrompt: string,
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  invalidResponse: string,
): Promise<string | null> {
  const repromptMessages = [
    ...messages,
    { role: 'assistant' as const, content: invalidResponse },
    {
      role: 'user' as const,
      content:
        'Your previous response contained a direct answer or solution. Rewrite it as a question that leads the developer to discover this themselves. You must ONLY ask questions — never provide fixes or answers.',
    },
  ];

  const newResponse = await callLLM(systemPrompt, repromptMessages, getConversationModel());
  const check = validateResponse(newResponse);
  return check.valid ? newResponse : null;
}

const FALLBACK_QUESTIONS: Record<Intensity, string[]> = {
  socrates: [
    'What do you think might be happening here? What have you observed so far?',
    'Have you considered looking at the error message more carefully? What does it tell you?',
    'What would you expect to see if everything was working correctly?',
  ],
  nietzsche: [
    'What evidence do you have for that assumption? Have you actually verified it?',
    'You seem to be guessing. What does the data actually show?',
    "What's the simplest thing you haven't checked yet?",
  ],
  zarathustra: [
    "You're avoiding the hard question. What are you afraid to find?",
    'Your hypothesis is untested. What would disprove it?',
    "Stop theorizing. What does the actual execution trace show you?",
  ],
};

export function getFallbackQuestion(intensity: Intensity): string {
  const questions = FALLBACK_QUESTIONS[intensity];
  return questions[Math.floor(Math.random() * questions.length)];
}
