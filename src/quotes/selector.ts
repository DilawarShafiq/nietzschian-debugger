import type { Quote, QuoteContext, SessionOutcome } from '../types.js';
import { QUOTES } from './corpus.js';

const AVOIDANCE_PATTERNS = [
  /\bi don'?t (?:want to|care|think)\b/i,
  /\bcan'?t you just\b/i,
  /\bjust tell me\b/i,
  /\bwhat'?s the (?:fix|answer|solution)\b/i,
  /\bi'?m not sure (?:why|how)\b/i,
  /\bthat'?s not (?:relevant|important)\b/i,
  /\bskip\b/i,
  /\bwhatever\b/i,
];

const OVERWHELM_PATTERNS = [
  /\bi don'?t know\b/i,
  /\bi'?m (?:lost|confused|stuck|overwhelmed)\b/i,
  /\bno idea\b/i,
  /\bthis is too\b/i,
  /\bi can'?t figure\b/i,
  /\bhelp\b/i,
  /\bi'?m not getting\b/i,
  /\bgive up\b/i,
];

const STRATEGY_PATTERNS = [
  /\bwhere (?:do i|should i) start\b/i,
  /\bso many (?:things|options|possibilities)\b/i,
  /\bmaybe (?:it'?s|i should)\b/i,
  /\bor maybe\b/i,
  /\bcould be (?:this|that|anything)\b/i,
  /\bnot sure which\b/i,
];

export function detectContext(response: string): QuoteContext | null {
  for (const pattern of AVOIDANCE_PATTERNS) {
    if (pattern.test(response)) return 'avoidance';
  }
  for (const pattern of OVERWHELM_PATTERNS) {
    if (pattern.test(response)) return 'overwhelm';
  }
  for (const pattern of STRATEGY_PATTERNS) {
    if (pattern.test(response)) return 'strategy';
  }
  return null;
}

export function selectQuote(response: string): Quote | null {
  const context = detectContext(response);
  if (!context) return null;

  const matching = QUOTES.filter((q) => q.context === context);
  if (matching.length === 0) return null;

  return matching[Math.floor(Math.random() * matching.length)];
}

export function selectClosingQuote(outcome: SessionOutcome): Quote {
  const context: QuoteContext = outcome === 'solved' ? 'victory' : 'perseverance';
  const matching = QUOTES.filter((q) => q.context === context);
  return matching[Math.floor(Math.random() * matching.length)];
}
