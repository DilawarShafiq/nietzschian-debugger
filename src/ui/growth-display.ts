import type { Session, SkillScores, GrowthProfile, Quote, Trend } from '../types.js';

const FILLED = '█';
const EMPTY = '░';
const BAR_LENGTH = 10;

const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';
const DIM = '\x1b[2m';
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const YELLOW = '\x1b[33m';

function renderBar(score: number): string {
  const clamped = Math.max(1, Math.min(10, Math.round(score)));
  return FILLED.repeat(clamped) + EMPTY.repeat(BAR_LENGTH - clamped);
}

function scoreLabel(score: number): string {
  if (score >= 8) return 'strong';
  if (score >= 5) return 'moderate';
  return 'weak';
}

function trendIndicator(trend: Trend, delta?: number): string {
  if (trend === 'improving') {
    const d = delta !== undefined ? ` (+${delta})` : '';
    return `${GREEN}improving${d}${RESET}`;
  }
  if (trend === 'declining') {
    const d = delta !== undefined ? ` (${delta})` : '';
    return `${RED}declining${d}${RESET}`;
  }
  return `${DIM}stable${RESET}`;
}

export function renderGrowthScore(
  session: Session,
  growthProfile?: GrowthProfile,
  closingQuote?: Quote,
): string {
  const lines: string[] = [];

  const outcomeLabel = session.outcome === 'solved' ? 'Solved' : 'Abandoned';
  lines.push(
    `\n${BOLD}Session Complete — ${session.questionsToRootCause} questions to root cause (${outcomeLabel})${RESET}`,
  );
  lines.push('');
  lines.push(`${BOLD}Your Debugging Profile:${RESET}`);

  const scores = session.skillScores;
  const dims: Array<{ name: string; key: keyof SkillScores; label: string }> = [
    { name: 'Assumption-checking', key: 'assumptionChecking', label: scoreLabel(scores.assumptionChecking) },
    { name: 'Evidence-gathering', key: 'evidenceGathering', label: scoreLabel(scores.evidenceGathering) },
    { name: 'Root cause speed', key: 'rootCauseSpeed', label: scoreLabel(scores.rootCauseSpeed) },
  ];

  for (let i = 0; i < dims.length; i++) {
    const dim = dims[i];
    const bar = renderBar(scores[dim.key]);
    const connector = i < dims.length - 1 ? '┣' : '┗';
    let line = `${connector} ${dim.name.padEnd(22)} ${bar}  ${dim.label}`;

    if (growthProfile) {
      const trend = growthProfile.recentTrend[dim.key];
      if (trend !== 'stable') {
        line += ` — ${trendIndicator(trend)}`;
      }
    }

    lines.push(line);
  }

  if (growthProfile && growthProfile.totalSessions > 1) {
    lines.push('');
    lines.push(
      `${DIM}${growthProfile.totalSessions} sessions total | ${growthProfile.solvedCount} solved | ${growthProfile.abandonedCount} abandoned${RESET}`,
    );
  }

  if (closingQuote) {
    lines.push('');
    lines.push(`${DIM}"${closingQuote.text}"${RESET}`);
    lines.push(`${DIM} — ${closingQuote.philosopher}${RESET}`);
  }

  lines.push('');
  return lines.join('\n');
}
