import { randomUUID } from 'node:crypto';
import type { Session, Intensity, SessionOutcome, Turn, SkillScores, BehaviorTag, Quote } from '../types.js';
import { SCHEMA_VERSION } from '../types.js';

export function createSession(problemDescription: string, intensity: Intensity): Session {
  return {
    schemaVersion: SCHEMA_VERSION,
    id: randomUUID(),
    timestamp: new Date().toISOString(),
    endTimestamp: '',
    problemDescription,
    intensity,
    outcome: 'abandoned',
    questionsToRootCause: 0,
    codeFiles: [],
    transcript: [],
    skillScores: { assumptionChecking: 5, evidenceGathering: 5, rootCauseSpeed: 5 },
    behaviorTags: [],
  };
}

export function addTurn(
  session: Session,
  question: string,
  response: string,
  model: string,
  behaviorTags: string[] = [],
  quoteUsed: Quote | null = null,
): Turn {
  const turn: Turn = {
    turnNumber: session.transcript.length + 1,
    question,
    response,
    model,
    quoteUsed,
    behaviorTags,
    timestamp: new Date().toISOString(),
  };
  session.transcript.push(turn);
  session.questionsToRootCause = session.transcript.length;
  return turn;
}

export function finalizeSession(
  session: Session,
  outcome: SessionOutcome,
  skillScores?: SkillScores,
  behaviorTags?: BehaviorTag[],
): void {
  session.endTimestamp = new Date().toISOString();
  session.outcome = outcome;
  if (skillScores) session.skillScores = skillScores;
  if (behaviorTags) session.behaviorTags = behaviorTags;
}

export function addCodeFile(session: Session, filePath: string): void {
  if (!session.codeFiles.includes(filePath)) {
    session.codeFiles.push(filePath);
  }
}
