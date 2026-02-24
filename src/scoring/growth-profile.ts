import type { Session, GrowthProfile, SkillScores, Trend, TrendMap } from '../types.js';
import { listSessions } from '../storage/session-store.js';

export async function computeGrowthProfile(): Promise<GrowthProfile | undefined> {
  const sessions = await listSessions();
  if (sessions.length === 0) return undefined;
  return computeFromSessions(sessions);
}

export function computeFromSessions(sessions: Session[]): GrowthProfile {
  const totalSessions = sessions.length;
  const solvedCount = sessions.filter((s) => s.outcome === 'solved').length;
  const abandonedCount = totalSessions - solvedCount;

  const averageScores = computeAverageScores(sessions);
  const recentTrend = computeTrends(sessions);

  return { totalSessions, solvedCount, abandonedCount, averageScores, recentTrend };
}

function computeAverageScores(sessions: Session[]): SkillScores {
  if (sessions.length === 0) {
    return { assumptionChecking: 5, evidenceGathering: 5, rootCauseSpeed: 5 };
  }

  const sums = { assumptionChecking: 0, evidenceGathering: 0, rootCauseSpeed: 0 };

  for (const s of sessions) {
    sums.assumptionChecking += s.skillScores.assumptionChecking;
    sums.evidenceGathering += s.skillScores.evidenceGathering;
    sums.rootCauseSpeed += s.skillScores.rootCauseSpeed;
  }

  const n = sessions.length;
  return {
    assumptionChecking: Math.round(sums.assumptionChecking / n),
    evidenceGathering: Math.round(sums.evidenceGathering / n),
    rootCauseSpeed: Math.round(sums.rootCauseSpeed / n),
  };
}

function computeTrends(sessions: Session[]): TrendMap {
  if (sessions.length < 2) {
    return { assumptionChecking: 'stable', evidenceGathering: 'stable', rootCauseSpeed: 'stable' };
  }

  const recent = sessions.slice(-5);
  const previous = sessions.slice(-10, -5);

  if (previous.length === 0) {
    return { assumptionChecking: 'stable', evidenceGathering: 'stable', rootCauseSpeed: 'stable' };
  }

  const recentAvg = computeAverageScores(recent);
  const previousAvg = computeAverageScores(previous);

  return {
    assumptionChecking: computeTrend(recentAvg.assumptionChecking, previousAvg.assumptionChecking),
    evidenceGathering: computeTrend(recentAvg.evidenceGathering, previousAvg.evidenceGathering),
    rootCauseSpeed: computeTrend(recentAvg.rootCauseSpeed, previousAvg.rootCauseSpeed),
  };
}

function computeTrend(recent: number, previous: number): Trend {
  const delta = recent - previous;
  if (delta > 1) return 'improving';
  if (delta < -1) return 'declining';
  return 'stable';
}
