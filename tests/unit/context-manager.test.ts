import { describe, it, expect } from 'vitest';
import {
  estimateTokens,
  shouldSummarize,
  buildMessageArray,
} from '../../src/core/context-manager.js';
import type { Turn } from '../../src/types.js';

function makeTurn(n: number, question: string, response: string): Turn {
  return {
    turnNumber: n,
    question,
    response,
    model: 'claude-haiku-4-5-20251001',
    quoteUsed: null,
    behaviorTags: [],
    timestamp: new Date().toISOString(),
  };
}

describe('estimateTokens', () => {
  it('estimates ~1 token per 4 characters', () => {
    const system = 'a'.repeat(400); // 100 tokens
    const messages = [{ role: 'user' as const, content: 'b'.repeat(400) }]; // 100 tokens
    const estimate = estimateTokens(system, messages);
    expect(estimate).toBe(200);
  });

  it('handles empty messages', () => {
    const estimate = estimateTokens('system', []);
    expect(estimate).toBe(2); // ceil(6/4) = 2
  });

  it('sums tokens across multiple messages', () => {
    const messages = [
      { role: 'user' as const, content: 'a'.repeat(100) },
      { role: 'assistant' as const, content: 'b'.repeat(100) },
    ];
    const estimate = estimateTokens('', messages);
    expect(estimate).toBe(50); // 200 chars / 4
  });
});

describe('shouldSummarize', () => {
  it('returns false below threshold', () => {
    expect(shouldSummarize(100_000)).toBe(false);
  });

  it('returns true above threshold (160K)', () => {
    expect(shouldSummarize(170_000)).toBe(true);
  });

  it('returns false at exactly the threshold', () => {
    expect(shouldSummarize(160_000)).toBe(false);
  });

  it('returns true at threshold + 1', () => {
    expect(shouldSummarize(160_001)).toBe(true);
  });
});

describe('buildMessageArray', () => {
  it('builds messages from turns', () => {
    const turns = [
      makeTurn(1, 'What happened?', 'I got a 500 error'),
      makeTurn(2, 'Where did you see it?', 'In the API call'),
    ];
    const result = buildMessageArray(turns);
    expect(result.messages.length).toBe(4); // 2 turns × (question + response)
    expect(result.messages[0].role).toBe('assistant');
    expect(result.messages[0].content).toBe('What happened?');
    expect(result.messages[1].role).toBe('user');
    expect(result.messages[1].content).toBe('I got a 500 error');
  });

  it('handles empty turns', () => {
    const result = buildMessageArray([]);
    expect(result.messages.length).toBe(0);
  });

  it('preserves rolling summary in return value', () => {
    const result = buildMessageArray([], 'Previous summary text');
    expect(result.rollingSummary).toBe('Previous summary text');
  });

  it('handles turns with empty responses', () => {
    const turns = [makeTurn(1, 'Question?', '')];
    const result = buildMessageArray(turns);
    // Question is there, but empty response is skipped by the implementation
    expect(result.messages.length).toBe(1);
    expect(result.messages[0].role).toBe('assistant');
  });
});
