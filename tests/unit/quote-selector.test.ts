import { describe, it, expect } from 'vitest';
import { detectContext, selectQuote, selectClosingQuote } from '../../src/quotes/selector.js';

describe('detectContext', () => {
  it('detects avoidance from "just tell me"', () => {
    expect(detectContext('just tell me the answer')).toBe('avoidance');
  });

  it('detects avoidance from "can\'t you just"', () => {
    expect(detectContext("can't you just fix it")).toBe('avoidance');
  });

  it('detects avoidance from "what\'s the fix"', () => {
    expect(detectContext("what's the fix")).toBe('avoidance');
  });

  it('detects avoidance from "skip"', () => {
    expect(detectContext('skip this question')).toBe('avoidance');
  });

  it('detects avoidance from "whatever"', () => {
    expect(detectContext('whatever, move on')).toBe('avoidance');
  });

  it('detects overwhelm from "I don\'t know"', () => {
    expect(detectContext("I don't know")).toBe('overwhelm');
  });

  it('detects overwhelm from "I\'m lost"', () => {
    expect(detectContext("I'm lost")).toBe('overwhelm');
  });

  it('detects overwhelm from "I\'m stuck"', () => {
    expect(detectContext("I'm stuck on this")).toBe('overwhelm');
  });

  it('detects overwhelm from "no idea"', () => {
    expect(detectContext('I have no idea')).toBe('overwhelm');
  });

  it('detects overwhelm from "I can\'t figure"', () => {
    expect(detectContext("I can't figure this out")).toBe('overwhelm');
  });

  it('detects overwhelm from "help"', () => {
    expect(detectContext('help me understand')).toBe('overwhelm');
  });

  it('detects overwhelm from "give up"', () => {
    expect(detectContext('I want to give up')).toBe('overwhelm');
  });

  it('detects strategy from "where do I start"', () => {
    expect(detectContext('where do i start')).toBe('strategy');
  });

  it('detects strategy from "so many options"', () => {
    expect(detectContext('There are so many options')).toBe('strategy');
  });

  it('detects strategy from "or maybe"', () => {
    expect(detectContext('or maybe it is the database')).toBe('strategy');
  });

  it('detects strategy from "could be anything"', () => {
    expect(detectContext('could be anything at this point')).toBe('strategy');
  });

  it('returns null for a technical response', () => {
    expect(detectContext('I checked the logs and found a timeout at line 42')).toBeNull();
  });

  it('returns null for an empty string', () => {
    expect(detectContext('')).toBeNull();
  });
});

describe('selectQuote', () => {
  it('returns a quote for avoidance context', () => {
    const quote = selectQuote('just tell me the answer');
    expect(quote).not.toBeNull();
    expect(quote!.context).toBe('avoidance');
    expect(quote!.philosopher).toBe('Friedrich Nietzsche');
  });

  it('returns a quote for overwhelm context', () => {
    const quote = selectQuote("I don't know what to do");
    expect(quote).not.toBeNull();
    expect(quote!.context).toBe('overwhelm');
    expect(quote!.philosopher).toBe('Seneca');
  });

  it('returns a quote for strategy context', () => {
    const quote = selectQuote('where should i start debugging');
    expect(quote).not.toBeNull();
    expect(quote!.context).toBe('strategy');
    expect(quote!.philosopher).toBe('Sun Tzu');
  });

  it('returns null when no context matches', () => {
    const quote = selectQuote('I checked the logs and found a 500 error on line 42');
    expect(quote).toBeNull();
  });
});

describe('selectClosingQuote', () => {
  it('returns a victory quote for solved sessions', () => {
    const quote = selectClosingQuote('solved');
    expect(quote).toBeDefined();
    expect(quote.context).toBe('victory');
  });

  it('returns a perseverance quote for abandoned sessions', () => {
    const quote = selectClosingQuote('abandoned');
    expect(quote).toBeDefined();
    expect(quote.context).toBe('perseverance');
  });
});
