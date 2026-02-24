import type { BehaviorTag, SkillScores } from '../types.js';

const POSITIVE_TAGS: Record<string, string> = {
  'checked-logs': 'evidenceGathering',
  'questioned-assumption': 'assumptionChecking',
  'narrowed-scope': 'rootCauseSpeed',
};

const NEGATIVE_TAGS: Record<string, string> = {
  'guessed-without-evidence': 'evidenceGathering',
  'assumed-without-checking': 'assumptionChecking',
  'asked-for-answer': 'assumptionChecking',
  'went-broad-unnecessarily': 'rootCauseSpeed',
};

const BASE_SCORE = 5;
const POSITIVE_WEIGHT = 1.0;
const NEGATIVE_WEIGHT = 1.0;

export function computeSkillScores(behaviorTags: BehaviorTag[]): SkillScores {
  const scores = {
    assumptionChecking: BASE_SCORE,
    evidenceGathering: BASE_SCORE,
    rootCauseSpeed: BASE_SCORE,
  };

  for (const bt of behaviorTags) {
    const dim = bt.dimension;
    if (bt.tag in POSITIVE_TAGS) {
      scores[dim] += POSITIVE_WEIGHT;
    } else if (bt.tag in NEGATIVE_TAGS) {
      scores[dim] -= NEGATIVE_WEIGHT;
    }
  }

  scores.assumptionChecking = clamp(scores.assumptionChecking);
  scores.evidenceGathering = clamp(scores.evidenceGathering);
  scores.rootCauseSpeed = clamp(scores.rootCauseSpeed);

  return scores;
}

function clamp(value: number): number {
  return Math.max(1, Math.min(10, Math.round(value)));
}
