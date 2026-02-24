import { describe, it, expect } from 'vitest';
import { validateResponse, getFallbackQuestion } from '../../src/llm/validator.js';

describe('validateResponse', () => {
  it('passes a response that contains a question mark', () => {
    const result = validateResponse('Have you checked the logs?');
    expect(result.valid).toBe(true);
  });

  it('fails a response with no question mark', () => {
    const result = validateResponse('The problem is in your auth middleware.');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('no question');
  });

  it('fails when response matches "the fix is" pattern', () => {
    const result = validateResponse('The fix is to change the timeout. Do you see?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "you should change" pattern', () => {
    const result = validateResponse('You should change the port. What do you think?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "try doing" pattern', () => {
    const result = validateResponse('Try doing a restart. Would that help?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "here\'s the fix" pattern', () => {
    const result = validateResponse("Here's the fix — does it look right?");
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "the solution is" pattern', () => {
    const result = validateResponse('The solution is clear. Can you see it?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "just change" pattern', () => {
    const result = validateResponse('Just change the import path. Agreed?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "you need to change" pattern', () => {
    const result = validateResponse('You need to change line 42. Right?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "to fix this" pattern', () => {
    const result = validateResponse('To fix this, update config. Okay?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "try changing" pattern', () => {
    const result = validateResponse('Try changing the env variable. Sound good?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response matches "try replacing" pattern', () => {
    const result = validateResponse('Try replacing the function. Would that work?');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('answer pattern');
  });

  it('fails when response contains a code fix block', () => {
    const response = 'Look at this:\n```js\n// fix: change timeout\nsetTimeout(cb, 1000)\n```\nDoes this help?';
    const result = validateResponse(response);
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('code fix');
  });

  it('passes a pure question with no answer patterns', () => {
    const result = validateResponse(
      'What does the error message say when you run the test? Have you looked at the stack trace?',
    );
    expect(result.valid).toBe(true);
  });

  it('passes a question that mentions code without providing a fix', () => {
    const result = validateResponse(
      'I see you have a `setTimeout` on line 42. What value is the delay parameter set to?',
    );
    expect(result.valid).toBe(true);
  });

  it('passes a challenging question about code', () => {
    const result = validateResponse(
      "What evidence do you have that the database connection is the bottleneck? Have you actually measured it?",
    );
    expect(result.valid).toBe(true);
  });
});

describe('getFallbackQuestion', () => {
  it('returns a string for socrates intensity', () => {
    const q = getFallbackQuestion('socrates');
    expect(typeof q).toBe('string');
    expect(q.length).toBeGreaterThan(0);
    expect(q).toContain('?');
  });

  it('returns a string for nietzsche intensity', () => {
    const q = getFallbackQuestion('nietzsche');
    expect(typeof q).toBe('string');
    expect(q.length).toBeGreaterThan(0);
    expect(q).toContain('?');
  });

  it('returns a string for zarathustra intensity', () => {
    const q = getFallbackQuestion('zarathustra');
    expect(typeof q).toBe('string');
    expect(q.length).toBeGreaterThan(0);
    expect(q).toContain('?');
  });
});
