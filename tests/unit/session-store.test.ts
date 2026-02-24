import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { saveSession, loadSession, listSessions } from '../../src/storage/session-store.js';
import { createSession, finalizeSession } from '../../src/core/session.js';
import { rm, mkdir, readdir } from 'node:fs/promises';
import { join } from 'node:path';

const TEST_SESSIONS_DIR = join(process.cwd(), '.nietzschian/sessions');

describe('session-store', () => {
  beforeEach(async () => {
    // Clean up sessions directory before each test
    try {
      await rm(TEST_SESSIONS_DIR, { recursive: true, force: true });
    } catch {
      // Directory might not exist
    }
  });

  afterEach(async () => {
    try {
      await rm(TEST_SESSIONS_DIR, { recursive: true, force: true });
    } catch {
      // Cleanup best-effort
    }
  });

  it('saves a session and creates the sessions directory', async () => {
    const session = createSession('Test problem', 'nietzsche');
    finalizeSession(session, 'solved');

    const filePath = await saveSession(session);
    expect(filePath).toContain(session.id);

    const files = await readdir(TEST_SESSIONS_DIR);
    expect(files).toContain(`${session.id}.json`);
  });

  it('loads a saved session back identically', async () => {
    const session = createSession('Load test', 'zarathustra');
    finalizeSession(session, 'abandoned');

    await saveSession(session);
    const loaded = await loadSession(session.id);

    expect(loaded).not.toBeNull();
    expect(loaded!.id).toBe(session.id);
    expect(loaded!.problemDescription).toBe('Load test');
    expect(loaded!.intensity).toBe('zarathustra');
    expect(loaded!.outcome).toBe('abandoned');
    expect(loaded!.schemaVersion).toBe(session.schemaVersion);
  });

  it('returns null for a non-existent session', async () => {
    await mkdir(TEST_SESSIONS_DIR, { recursive: true });
    const loaded = await loadSession('non-existent-id');
    expect(loaded).toBeNull();
  });

  it('lists sessions sorted by timestamp', async () => {
    const s1 = createSession('First', 'socrates');
    const s2 = createSession('Second', 'nietzsche');
    const s3 = createSession('Third', 'zarathustra');

    // Force distinct timestamps
    s1.timestamp = '2024-01-01T00:00:00.000Z';
    s2.timestamp = '2024-01-02T00:00:00.000Z';
    s3.timestamp = '2024-01-03T00:00:00.000Z';

    await saveSession(s1);
    await saveSession(s2);
    await saveSession(s3);

    const sessions = await listSessions();
    expect(sessions.length).toBe(3);
    expect(sessions[0].problemDescription).toBe('First');
    expect(sessions[1].problemDescription).toBe('Second');
    expect(sessions[2].problemDescription).toBe('Third');
  });

  it('auto-creates directory when missing', async () => {
    const session = createSession('Auto-create dir', 'nietzsche');
    // Directory doesn't exist yet — saveSession should create it
    await saveSession(session);

    const files = await readdir(TEST_SESSIONS_DIR);
    expect(files.length).toBeGreaterThan(0);
  });

  it('handles corrupted JSON gracefully in listSessions', async () => {
    const session = createSession('Valid session', 'nietzsche');
    await saveSession(session);

    // Write a corrupted file
    const { writeFile } = await import('node:fs/promises');
    await writeFile(join(TEST_SESSIONS_DIR, 'corrupted.json'), 'not valid json{{{', 'utf-8');

    const sessions = await listSessions();
    // Should return the valid session, skipping corrupted
    expect(sessions.length).toBe(1);
    expect(sessions[0].id).toBe(session.id);
  });

  it('returns empty array when no sessions exist', async () => {
    const sessions = await listSessions();
    expect(sessions).toEqual([]);
  });
});
