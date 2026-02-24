import { readFile, stat } from 'node:fs/promises';
import { resolve } from 'node:path';

const FILE_PATH_REGEX = /(?:^|\s|["'`])([.~/][\w./-]+\.\w{1,10})(?=[\s"'`,:;)}\]]|$)/g;

const MAX_FILE_SIZE = 100_000; // ~100KB, well under context limits
const MAX_LINES_FOR_CONTEXT = 500;

export function detectFilePaths(text: string): string[] {
  const matches: string[] = [];
  let match: RegExpExecArray | null;
  const regex = new RegExp(FILE_PATH_REGEX.source, FILE_PATH_REGEX.flags);

  while ((match = regex.exec(text)) !== null) {
    const path = match[1];
    if (path && !path.startsWith('http') && !path.startsWith('//')) {
      matches.push(path);
    }
  }

  return [...new Set(matches)];
}

export async function readCodeFile(filePath: string): Promise<string | null> {
  try {
    const resolved = resolve(filePath);
    const stats = await stat(resolved);

    if (!stats.isFile()) return null;
    if (stats.size > MAX_FILE_SIZE) {
      return truncateToRelevantSection(await readFile(resolved, 'utf-8'));
    }

    const content = await readFile(resolved, 'utf-8');
    return addLineNumbers(content);
  } catch {
    return null;
  }
}

function addLineNumbers(content: string): string {
  return content
    .split('\n')
    .map((line, i) => `${i + 1}: ${line}`)
    .join('\n');
}

function truncateToRelevantSection(content: string): string {
  const lines = content.split('\n');
  if (lines.length <= MAX_LINES_FOR_CONTEXT) {
    return addLineNumbers(content);
  }

  // Take first 100 lines (imports/setup) + last 400 lines (most recent code)
  const head = lines.slice(0, 100);
  const tail = lines.slice(-400);
  const truncated = [...head, `\n... (${lines.length - 500} lines omitted) ...\n`, ...tail].join('\n');
  return addLineNumbers(truncated);
}

export function formatCodeContext(files: Map<string, string>): string {
  if (files.size === 0) return '';

  const sections: string[] = [];
  for (const [path, content] of files) {
    sections.push(`--- File: ${path} ---\n${content}`);
  }
  return sections.join('\n\n');
}
