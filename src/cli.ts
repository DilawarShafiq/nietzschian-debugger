#!/usr/bin/env node

import { Command } from 'commander';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { debugCommand } from './commands/debug.js';
import type { Intensity } from './types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let version = '0.1.0';
try {
  const pkg = JSON.parse(readFileSync(join(__dirname, '..', 'package.json'), 'utf-8'));
  version = pkg.version;
} catch {
  // Fallback version
}

const program = new Command();

program
  .name('nietzschian')
  .description('The anti-AI debugger. What doesn\'t kill your code makes it stronger.')
  .version(version);

program
  .command('debug')
  .description('Start an interactive debugging session')
  .argument('<problem>', 'Description of the bug or problem to debug')
  .option(
    '-i, --intensity <level>',
    'Questioning intensity: socrates, nietzsche, zarathustra',
    'nietzsche',
  )
  .action(async (problem: string, options: { intensity: string }) => {
    const validIntensities = ['socrates', 'nietzsche', 'zarathustra'];
    if (!validIntensities.includes(options.intensity)) {
      console.error(
        `Invalid intensity: "${options.intensity}". Choose from: ${validIntensities.join(', ')}`,
      );
      process.exit(2);
    }

    await debugCommand(problem, options.intensity as Intensity);
  });

program.parse();
