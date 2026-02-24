import { describe, it, expect } from 'vitest';
import { detectFilePaths, readCodeFile, formatCodeContext } from '../../src/storage/file-reader.js';
import { resolve } from 'node:path';

describe('detectFilePaths', () => {
  it('detects relative path with ./', () => {
    const paths = detectFilePaths('Look at ./src/auth.ts for the bug');
    expect(paths).toContain('./src/auth.ts');
  });

  it('detects relative path with ./ prefix', () => {
    const paths = detectFilePaths('Check ./src/models/user.ts');
    expect(paths).toContain('./src/models/user.ts');
  });

  it('detects paths in quotes with ./ prefix', () => {
    const paths = detectFilePaths('The file "./src/index.ts" has the issue');
    expect(paths).toContain('./src/index.ts');
  });

  it('detects paths in backticks', () => {
    const paths = detectFilePaths('Look at `./src/utils.ts`');
    expect(paths).toContain('./src/utils.ts');
  });

  it('detects multiple paths in one string', () => {
    const paths = detectFilePaths('Compare ./src/a.ts and ./src/b.ts');
    expect(paths.length).toBe(2);
    expect(paths).toContain('./src/a.ts');
    expect(paths).toContain('./src/b.ts');
  });

  it('deduplicates repeated paths', () => {
    const paths = detectFilePaths('./src/a.ts and again ./src/a.ts');
    expect(paths.length).toBe(1);
  });

  it('ignores URLs', () => {
    const paths = detectFilePaths('Visit http://example.com/page.html for docs');
    // Should not detect the URL domain as a file path
    const hasUrl = paths.some((p) => p.includes('example.com'));
    expect(hasUrl).toBe(false);
  });

  it('detects paths with various extensions', () => {
    const text = 'Files: ./app.js ./style.css ./data.json ./readme.md';
    const paths = detectFilePaths(text);
    expect(paths.length).toBeGreaterThanOrEqual(4);
  });

  it('returns empty for text with no paths', () => {
    const paths = detectFilePaths('This is just a normal sentence.');
    expect(paths.length).toBe(0);
  });
});

describe('readCodeFile', () => {
  it('reads a real file and returns numbered lines', async () => {
    const content = await readCodeFile('./package.json');
    expect(content).not.toBeNull();
    expect(content).toContain('1:');
    expect(content).toContain('nietzschian-debugger');
  });

  it('returns null for a non-existent file', async () => {
    const content = await readCodeFile('./nonexistent-file-xyz.ts');
    expect(content).toBeNull();
  });
});

describe('formatCodeContext', () => {
  it('returns empty string for no files', () => {
    const result = formatCodeContext(new Map());
    expect(result).toBe('');
  });

  it('formats single file with path header', () => {
    const files = new Map([['src/main.ts', '1: console.log("hello")']]);
    const result = formatCodeContext(files);
    expect(result).toContain('--- File: src/main.ts ---');
    expect(result).toContain('console.log');
  });

  it('formats multiple files separated by headers', () => {
    const files = new Map([
      ['src/a.ts', '1: a'],
      ['src/b.ts', '1: b'],
    ]);
    const result = formatCodeContext(files);
    expect(result).toContain('--- File: src/a.ts ---');
    expect(result).toContain('--- File: src/b.ts ---');
  });
});
