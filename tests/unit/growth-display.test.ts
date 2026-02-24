import { describe, it, expect } from 'vitest';
import { renderGrowthScore } from '../../src/ui/growth-display.js';
import type { Session, GrowthProfile, Quote } from '../../src/types.js';

function makeSession(overrides: Partial<Session> = {}): Session {
  return {
    schemaVersion: 1,
    id: 'test-id',
    timestamp: new Date().toISOString(),
    endTimestamp: new Date().toISOString(),
    problemDescription: 'test',
    intensity: 'nietzsche',
    outcome: 'solved',
    questionsToRootCause: 5,
    codeFiles: [],
    transcript: [],
    skillScores: { assumptionChecking: 7, evidenceGathering: 6, rootCauseSpeed: 8 },
    behaviorTags: [],
    ...overrides,
  };
}

describe('renderGrowthScore', () => {
  it('renders session outcome and question count', () => {
    const session = makeSession({ outcome: 'solved', questionsToRootCause: 5 });
    const output = renderGrowthScore(session);
    expect(output).toContain('5 questions to root cause');
    expect(output).toContain('Solved');
  });

  it('renders abandoned outcome', () => {
    const session = makeSession({ outcome: 'abandoned' });
    const output = renderGrowthScore(session);
    expect(output).toContain('Abandoned');
  });

  it('renders skill dimension labels', () => {
    const session = makeSession();
    const output = renderGrowthScore(session);
    expect(output).toContain('Assumption-checking');
    expect(output).toContain('Evidence-gathering');
    expect(output).toContain('Root cause speed');
  });

  it('renders Unicode bar charts', () => {
    const session = makeSession();
    const output = renderGrowthScore(session);
    expect(output).toContain('█');
    expect(output).toContain('░');
  });

  it('renders score descriptors', () => {
    const session = makeSession({
      skillScores: { assumptionChecking: 9, evidenceGathering: 5, rootCauseSpeed: 2 },
    });
    const output = renderGrowthScore(session);
    expect(output).toContain('strong');
    expect(output).toContain('moderate');
    expect(output).toContain('weak');
  });

  it('includes trend information when growth profile provided', () => {
    const session = makeSession();
    const profile: GrowthProfile = {
      totalSessions: 10,
      solvedCount: 7,
      abandonedCount: 3,
      averageScores: { assumptionChecking: 6, evidenceGathering: 7, rootCauseSpeed: 5 },
      recentTrend: {
        assumptionChecking: 'improving',
        evidenceGathering: 'declining',
        rootCauseSpeed: 'stable',
      },
    };
    const output = renderGrowthScore(session, profile);
    expect(output).toContain('improving');
    expect(output).toContain('declining');
    expect(output).toContain('10 sessions total');
    expect(output).toContain('7 solved');
    expect(output).toContain('3 abandoned');
  });

  it('includes closing quote when provided', () => {
    const session = makeSession();
    const quote: Quote = {
      text: 'What does not kill me makes me stronger.',
      philosopher: 'Friedrich Nietzsche',
      context: 'victory',
      source: 'Twilight of the Idols',
    };
    const output = renderGrowthScore(session, undefined, quote);
    expect(output).toContain('What does not kill me makes me stronger.');
    expect(output).toContain('Friedrich Nietzsche');
  });

  it('renders without growth profile or quote', () => {
    const session = makeSession();
    const output = renderGrowthScore(session);
    expect(output).toContain('Debugging Profile');
    expect(output).not.toContain('sessions total');
  });
});
