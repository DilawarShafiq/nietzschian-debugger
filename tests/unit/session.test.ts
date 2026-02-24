import { describe, it, expect } from 'vitest';
import { createSession, addTurn, finalizeSession, addCodeFile } from '../../src/core/session.js';

describe('createSession', () => {
  it('creates a session with correct defaults', () => {
    const session = createSession('My API is slow', 'nietzsche');
    expect(session.problemDescription).toBe('My API is slow');
    expect(session.intensity).toBe('nietzsche');
    expect(session.outcome).toBe('abandoned');
    expect(session.schemaVersion).toBe(1);
    expect(session.id).toBeTruthy();
    expect(session.timestamp).toBeTruthy();
    expect(session.transcript).toEqual([]);
    expect(session.codeFiles).toEqual([]);
    expect(session.skillScores.assumptionChecking).toBe(5);
    expect(session.skillScores.evidenceGathering).toBe(5);
    expect(session.skillScores.rootCauseSpeed).toBe(5);
  });

  it('creates unique IDs for each session', () => {
    const s1 = createSession('Problem 1', 'socrates');
    const s2 = createSession('Problem 2', 'zarathustra');
    expect(s1.id).not.toBe(s2.id);
  });
});

describe('addTurn', () => {
  it('adds a turn to the transcript', () => {
    const session = createSession('Test', 'nietzsche');
    const turn = addTurn(session, 'What happened?', 'I got a 500 error', 'claude-haiku-4-5-20251001');
    expect(session.transcript.length).toBe(1);
    expect(turn.turnNumber).toBe(1);
    expect(turn.question).toBe('What happened?');
    expect(turn.response).toBe('I got a 500 error');
    expect(turn.model).toBe('claude-haiku-4-5-20251001');
    expect(turn.timestamp).toBeTruthy();
  });

  it('increments turn numbers', () => {
    const session = createSession('Test', 'nietzsche');
    addTurn(session, 'Q1?', 'R1', 'model');
    addTurn(session, 'Q2?', 'R2', 'model');
    addTurn(session, 'Q3?', 'R3', 'model');
    expect(session.transcript[0].turnNumber).toBe(1);
    expect(session.transcript[1].turnNumber).toBe(2);
    expect(session.transcript[2].turnNumber).toBe(3);
  });

  it('updates questionsToRootCause', () => {
    const session = createSession('Test', 'nietzsche');
    addTurn(session, 'Q?', 'R', 'model');
    expect(session.questionsToRootCause).toBe(1);
    addTurn(session, 'Q2?', 'R2', 'model');
    expect(session.questionsToRootCause).toBe(2);
  });
});

describe('finalizeSession', () => {
  it('sets outcome and end timestamp', () => {
    const session = createSession('Test', 'nietzsche');
    finalizeSession(session, 'solved');
    expect(session.outcome).toBe('solved');
    expect(session.endTimestamp).toBeTruthy();
  });

  it('updates skill scores when provided', () => {
    const session = createSession('Test', 'nietzsche');
    finalizeSession(session, 'solved', { assumptionChecking: 8, evidenceGathering: 7, rootCauseSpeed: 9 });
    expect(session.skillScores.assumptionChecking).toBe(8);
  });
});

describe('addCodeFile', () => {
  it('adds a file to the session', () => {
    const session = createSession('Test', 'nietzsche');
    addCodeFile(session, './src/auth.ts');
    expect(session.codeFiles).toContain('./src/auth.ts');
  });

  it('does not duplicate files', () => {
    const session = createSession('Test', 'nietzsche');
    addCodeFile(session, './src/auth.ts');
    addCodeFile(session, './src/auth.ts');
    expect(session.codeFiles.length).toBe(1);
  });
});
