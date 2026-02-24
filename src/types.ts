export type Intensity = 'socrates' | 'nietzsche' | 'zarathustra';
export type SessionOutcome = 'solved' | 'abandoned';
export type QuoteContext = 'avoidance' | 'overwhelm' | 'strategy' | 'victory' | 'defeat' | 'perseverance';

export interface Quote {
  text: string;
  philosopher: string;
  context: QuoteContext;
  source: string;
}

export interface BehaviorTag {
  turnNumber: number;
  tag: string;
  dimension: 'assumptionChecking' | 'evidenceGathering' | 'rootCauseSpeed';
}

export interface Turn {
  turnNumber: number;
  question: string;
  response: string;
  model: string;
  quoteUsed: Quote | null;
  behaviorTags: string[];
  timestamp: string;
}

export interface SkillScores {
  assumptionChecking: number;
  evidenceGathering: number;
  rootCauseSpeed: number;
}

export interface Session {
  schemaVersion: number;
  id: string;
  timestamp: string;
  endTimestamp: string;
  problemDescription: string;
  intensity: Intensity;
  outcome: SessionOutcome;
  questionsToRootCause: number;
  codeFiles: string[];
  transcript: Turn[];
  skillScores: SkillScores;
  behaviorTags: BehaviorTag[];
}

export interface GrowthProfile {
  totalSessions: number;
  solvedCount: number;
  abandonedCount: number;
  averageScores: SkillScores;
  recentTrend: TrendMap;
}

export type Trend = 'improving' | 'declining' | 'stable';

export interface TrendMap {
  assumptionChecking: Trend;
  evidenceGathering: Trend;
  rootCauseSpeed: Trend;
}

export const SCHEMA_VERSION = 1;
