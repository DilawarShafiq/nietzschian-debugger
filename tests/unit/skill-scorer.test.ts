import { describe, it, expect } from 'vitest';
import { computeSkillScores } from '../../src/scoring/skill-scorer.js';
import type { BehaviorTag } from '../../src/types.js';

describe('computeSkillScores', () => {
  it('returns baseline scores of 5 with empty tags', () => {
    const scores = computeSkillScores([]);
    expect(scores.assumptionChecking).toBe(5);
    expect(scores.evidenceGathering).toBe(5);
    expect(scores.rootCauseSpeed).toBe(5);
  });

  it('increases evidenceGathering with checked-logs tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'checked-logs', dimension: 'evidenceGathering' },
      { turnNumber: 2, tag: 'checked-logs', dimension: 'evidenceGathering' },
      { turnNumber: 3, tag: 'checked-logs', dimension: 'evidenceGathering' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.evidenceGathering).toBe(8);
  });

  it('decreases evidenceGathering with guessed-without-evidence tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'guessed-without-evidence', dimension: 'evidenceGathering' },
      { turnNumber: 2, tag: 'guessed-without-evidence', dimension: 'evidenceGathering' },
      { turnNumber: 3, tag: 'guessed-without-evidence', dimension: 'evidenceGathering' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.evidenceGathering).toBe(2);
  });

  it('increases assumptionChecking with questioned-assumption tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'questioned-assumption', dimension: 'assumptionChecking' },
      { turnNumber: 2, tag: 'questioned-assumption', dimension: 'assumptionChecking' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.assumptionChecking).toBe(7);
  });

  it('decreases assumptionChecking with assumed-without-checking tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'assumed-without-checking', dimension: 'assumptionChecking' },
      { turnNumber: 2, tag: 'assumed-without-checking', dimension: 'assumptionChecking' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.assumptionChecking).toBe(3);
  });

  it('increases rootCauseSpeed with narrowed-scope tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'narrowed-scope', dimension: 'rootCauseSpeed' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.rootCauseSpeed).toBe(6);
  });

  it('decreases rootCauseSpeed with went-broad-unnecessarily tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'went-broad-unnecessarily', dimension: 'rootCauseSpeed' },
      { turnNumber: 2, tag: 'went-broad-unnecessarily', dimension: 'rootCauseSpeed' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.rootCauseSpeed).toBe(3);
  });

  it('handles mixed positive and negative tags', () => {
    const tags: BehaviorTag[] = [
      { turnNumber: 1, tag: 'checked-logs', dimension: 'evidenceGathering' },
      { turnNumber: 2, tag: 'guessed-without-evidence', dimension: 'evidenceGathering' },
      { turnNumber: 3, tag: 'questioned-assumption', dimension: 'assumptionChecking' },
      { turnNumber: 4, tag: 'narrowed-scope', dimension: 'rootCauseSpeed' },
    ];
    const scores = computeSkillScores(tags);
    expect(scores.evidenceGathering).toBe(5); // +1 -1 = 0 from baseline
    expect(scores.assumptionChecking).toBe(6); // +1
    expect(scores.rootCauseSpeed).toBe(6); // +1
  });

  it('clamps scores at minimum 1', () => {
    const tags: BehaviorTag[] = Array.from({ length: 10 }, (_, i) => ({
      turnNumber: i + 1,
      tag: 'guessed-without-evidence',
      dimension: 'evidenceGathering' as const,
    }));
    const scores = computeSkillScores(tags);
    expect(scores.evidenceGathering).toBe(1);
  });

  it('clamps scores at maximum 10', () => {
    const tags: BehaviorTag[] = Array.from({ length: 10 }, (_, i) => ({
      turnNumber: i + 1,
      tag: 'checked-logs',
      dimension: 'evidenceGathering' as const,
    }));
    const scores = computeSkillScores(tags);
    expect(scores.evidenceGathering).toBe(10);
  });
});
