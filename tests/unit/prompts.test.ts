import { describe, it, expect } from 'vitest';
import { getSystemPrompt } from '../../src/llm/prompts.js';

describe('getSystemPrompt', () => {
  it('produces a prompt for socrates intensity', () => {
    const prompt = getSystemPrompt('socrates', 'My API is slow');
    expect(prompt).toContain('SOCRATES');
    expect(prompt).toContain('<persona>');
    expect(prompt).toContain('<behavioral_constraints>');
    expect(prompt).toContain('<intensity_rules>');
    expect(prompt).toContain('<session_context>');
    expect(prompt).toContain('My API is slow');
    expect(prompt).toContain('gentle');
  });

  it('produces a prompt for nietzsche intensity', () => {
    const prompt = getSystemPrompt('nietzsche', 'My API is slow');
    expect(prompt).toContain('NIETZSCHE');
    expect(prompt).toContain('<persona>');
    expect(prompt).toContain('<behavioral_constraints>');
    expect(prompt).toContain('<intensity_rules>');
    expect(prompt).toContain('confrontational');
  });

  it('produces a prompt for zarathustra intensity', () => {
    const prompt = getSystemPrompt('zarathustra', 'My API is slow');
    expect(prompt).toContain('ZARATHUSTRA');
    expect(prompt).toContain('<persona>');
    expect(prompt).toContain('<behavioral_constraints>');
    expect(prompt).toContain('<intensity_rules>');
    expect(prompt).toContain('brutal');
  });

  it('includes code context when provided', () => {
    const prompt = getSystemPrompt('nietzsche', 'Bug here', '1: const x = 1;\n2: const y = x + 1;');
    expect(prompt).toContain('<code_context>');
    expect(prompt).toContain('const x = 1');
  });

  it('omits code_context when not provided', () => {
    const prompt = getSystemPrompt('nietzsche', 'Bug here');
    expect(prompt).not.toContain('<code_context>');
  });

  it('includes rolling summary when provided', () => {
    const prompt = getSystemPrompt(
      'nietzsche',
      'Bug here',
      undefined,
      'Developer checked logs and found timeout error.',
    );
    expect(prompt).toContain('Developer checked logs');
  });

  it('includes turn number', () => {
    const prompt = getSystemPrompt('nietzsche', 'Bug here', undefined, undefined, 5);
    expect(prompt).toContain('Turn: 5');
  });

  it('defaults to turn 1 when not specified', () => {
    const prompt = getSystemPrompt('nietzsche', 'Bug here');
    expect(prompt).toContain('Turn: 1');
  });

  it('includes suggested quote when provided', () => {
    const prompt = getSystemPrompt(
      'nietzsche',
      'Bug here',
      undefined,
      undefined,
      1,
      'What does not kill me makes me stronger.',
    );
    expect(prompt).toContain('<suggested_quote>');
    expect(prompt).toContain('What does not kill me makes me stronger.');
  });

  it('omits suggested_quote tag when no quote provided', () => {
    const prompt = getSystemPrompt('nietzsche', 'Bug here');
    expect(prompt).not.toContain('<suggested_quote>');
  });

  it('contains behavioral constraints for all intensities', () => {
    for (const intensity of ['socrates', 'nietzsche', 'zarathustra'] as const) {
      const prompt = getSystemPrompt(intensity, 'test');
      expect(prompt).toContain('NEVER provide solutions');
      expect(prompt).toContain('Every response MUST contain at least one question');
    }
  });

  it('produces distinct prompts for each intensity', () => {
    const s = getSystemPrompt('socrates', 'test');
    const n = getSystemPrompt('nietzsche', 'test');
    const z = getSystemPrompt('zarathustra', 'test');

    // All three are distinct
    expect(s).not.toBe(n);
    expect(n).not.toBe(z);
    expect(s).not.toBe(z);
  });
});
