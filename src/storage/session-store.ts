import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import type { Session } from '../types.js';
import { SCHEMA_VERSION } from '../types.js';

const SESSIONS_DIR = '.nietzschian/sessions';

function getSessionsPath(): string {
  return join(process.cwd(), SESSIONS_DIR);
}

export async function ensureSessionsDir(): Promise<void> {
  const dir = getSessionsPath();
  await mkdir(dir, { recursive: true });
}

export async function saveSession(session: Session): Promise<string> {
  await ensureSessionsDir();
  const filePath = join(getSessionsPath(), `${session.id}.json`);
  await writeFile(filePath, JSON.stringify(session, null, 2), 'utf-8');
  return filePath;
}

export async function loadSession(id: string): Promise<Session | null> {
  try {
    const filePath = join(getSessionsPath(), `${id}.json`);
    const content = await readFile(filePath, 'utf-8');
    const data = JSON.parse(content) as Session;
    return migrateSession(data);
  } catch {
    return null;
  }
}

export async function listSessions(): Promise<Session[]> {
  try {
    const dir = getSessionsPath();
    const files = await readdir(dir);
    const jsonFiles = files.filter((f) => f.endsWith('.json'));
    const sessions: Session[] = [];

    for (const file of jsonFiles) {
      try {
        const content = await readFile(join(dir, file), 'utf-8');
        const data = JSON.parse(content) as Session;
        sessions.push(migrateSession(data));
      } catch {
        // Skip corrupted files
      }
    }

    sessions.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
    return sessions;
  } catch {
    return [];
  }
}

function migrateSession(data: Partial<Session> & { id: string }): Session {
  const version = data.schemaVersion ?? 0;

  if (version < SCHEMA_VERSION) {
    return {
      schemaVersion: SCHEMA_VERSION,
      id: data.id,
      timestamp: data.timestamp ?? new Date().toISOString(),
      endTimestamp: data.endTimestamp ?? new Date().toISOString(),
      problemDescription: data.problemDescription ?? '',
      intensity: data.intensity ?? 'nietzsche',
      outcome: data.outcome ?? 'abandoned',
      questionsToRootCause: data.questionsToRootCause ?? 0,
      codeFiles: data.codeFiles ?? [],
      transcript: data.transcript ?? [],
      skillScores: data.skillScores ?? { assumptionChecking: 5, evidenceGathering: 5, rootCauseSpeed: 5 },
      behaviorTags: data.behaviorTags ?? [],
    };
  }

  return data as Session;
}
