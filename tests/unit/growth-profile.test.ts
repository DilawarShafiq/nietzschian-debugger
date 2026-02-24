import { describe, it, expect } from 'vitest';
import { computeFromSessions } from '../../src/scoring/growth-profile.js';
import type { Session } from '../../src/types.js';

function makeSession(overrides: Partial<Session> = {}): Session {
  return {
    schemaVersion: 1,
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    endTimestamp: new Date().toISOString(),
    problemDescription: 'test',
    intensity: 'nietzsche',
    outcome: 'solved',
    questionsToRootCause: 5,
    codeFiles: [],
    transcript: [],
    skillScores: { assumptionChecking: 5, evidenceGathering: 5, rootCauseSpeed: 5 },
    behaviorTags: [],
    ...overrides,
  };
}

describe('computeFromSessions', () => {
  it('returns correct counts for solved vs abandoned', () => {
    const sessions = [
      makeSession({ outcome: 'solved' }),
      makeSession({ outcome: 'solved' }),
      makeSession({ outcome: 'abandoned' }),
    ];
    const profile = computeFromSessions(sessions);
    expect(profile.totalSessions).toBe(3);
    expect(profile.solvedCount).toBe(2);
    expect(profile.abandonedCount).toBe(1);
  });

  it('computes average scores across sessions', () => {
    const sessions = [
      makeSession({ skillScores: { assumptionChecking: 8, evidenceGathering: 6, rootCauseSpeed: 4 } }),
      makeSession({ skillScores: { assumptionChecking: 4, evidenceGathering: 8, rootCauseSpeed: 6 } }),
    ];
    const profile = computeFromSessions(sessions);
    expect(profile.averageScores.assumptionChecking).toBe(6);
    expect(profile.averageScores.evidenceGathering).toBe(7);
    expect(profile.averageScores.rootCauseSpeed).toBe(5);
  });

  it('returns stable trends with fewer than 2 sessions', () => {
    const sessions = [makeSession()];
    const profile = computeFromSessions(sessions);
    expect(profile.recentTrend.assumptionChecking).toBe('stable');
    expect(profile.recentTrend.evidenceGathering).toBe('stable');
    expect(profile.recentTrend.rootCauseSpeed).toBe('stable');
  });

  it('returns stable trends when no previous group exists', () => {
    // 3 sessions — all "recent", no "previous" group
    const sessions = Array.from({ length: 3 }, () => makeSession());
    const profile = computeFromSessions(sessions);
    expect(profile.recentTrend.assumptionChecking).toBe('stable');
  });

  it('detects improving trend', () => {
    // 5 old sessions with low scores, 5 new sessions with high scores
    const old = Array.from({ length: 5 }, () =>
      makeSession({
        skillScores: { assumptionChecking: 3, evidenceGathering: 3, rootCauseSpeed: 3 },
      }),
    );
    const recent = Array.from({ length: 5 }, () =>
      makeSession({
        skillScores: { assumptionChecking: 8, evidenceGathering: 8, rootCauseSpeed: 8 },
      }),
    );
    const profile = computeFromSessions([...old, ...recent]);
    expect(profile.recentTrend.assumptionChecking).toBe('improving');
    expect(profile.recentTrend.evidenceGathering).toBe('improving');
    expect(profile.recentTrend.rootCauseSpeed).toBe('improving');
  });

  it('detects declining trend', () => {
    const old = Array.from({ length: 5 }, () =>
      makeSession({
        skillScores: { assumptionChecking: 8, evidenceGathering: 8, rootCauseSpeed: 8 },
      }),
    );
    const recent = Array.from({ length: 5 }, () =>
      makeSession({
        skillScores: { assumptionChecking: 3, evidenceGathering: 3, rootCauseSpeed: 3 },
      }),
    );
    const profile = computeFromSessions([...old, ...recent]);
    expect(profile.recentTrend.assumptionChecking).toBe('declining');
    expect(profile.recentTrend.evidenceGathering).toBe('declining');
    expect(profile.recentTrend.rootCauseSpeed).toBe('declining');
  });

  it('detects stable when delta is within threshold', () => {
    const old = Array.from({ length: 5 }, () =>
      makeSession({
        skillScores: { assumptionChecking: 5, evidenceGathering: 5, rootCauseSpeed: 5 },
      }),
    );
    const recent = Array.from({ length: 5 }, () =>
      makeSession({
        skillScores: { assumptionChecking: 6, evidenceGathering: 5, rootCauseSpeed: 4 },
      }),
    );
    const profile = computeFromSessions([...old, ...recent]);
    // delta of 1 — should be stable (threshold is > 1)
    expect(profile.recentTrend.assumptionChecking).toBe('stable');
    expect(profile.recentTrend.evidenceGathering).toBe('stable');
    expect(profile.recentTrend.rootCauseSpeed).toBe('stable');
  });
});
