import Anthropic from '@anthropic-ai/sdk';
import type { Intensity } from '../types.js';
import { getClient, MissingApiKeyError } from '../llm/client.js';
import { createSession, finalizeSession } from '../core/session.js';
import { runSessionLoop } from '../core/session-loop.js';
import { saveSession } from '../storage/session-store.js';
import { tagSessionBehaviors } from '../scoring/behavior-tagger.js';
import { computeSkillScores } from '../scoring/skill-scorer.js';
import { computeGrowthProfile } from '../scoring/growth-profile.js';
import { selectClosingQuote } from '../quotes/selector.js';
import { renderGrowthScore } from '../ui/growth-display.js';
import { displayError, displayApiKeyHelp } from '../ui/renderer.js';

export async function debugCommand(
  problemDescription: string,
  intensity: Intensity,
): Promise<void> {
  // Validate API key
  try {
    getClient();
  } catch (error) {
    if (error instanceof MissingApiKeyError) {
      displayApiKeyHelp();
      process.exit(1);
    }
    throw error;
  }

  // Validate problem description
  if (!problemDescription || !problemDescription.trim()) {
    displayError('Please provide a problem description.');
    console.log('\nUsage: nietzschian debug "Your problem description here"');
    process.exit(2);
  }

  // Create session
  const session = createSession(problemDescription.trim(), intensity);

  try {
    // Run interactive session
    const result = await runSessionLoop(session);

    // Finalize session
    let behaviorTags = session.behaviorTags;
    let skillScores = session.skillScores;

    try {
      behaviorTags = await tagSessionBehaviors(session.transcript);
      skillScores = computeSkillScores(behaviorTags);
    } catch {
      // Scoring is best-effort — don't crash if it fails
    }

    finalizeSession(session, result.outcome, skillScores, behaviorTags);

    // Save session
    try {
      await saveSession(session);
    } catch {
      // Persistence is best-effort
    }

    // Display growth score
    const growthProfile = await computeGrowthProfile();
    const closingQuote = selectClosingQuote(result.outcome);
    const display = renderGrowthScore(session, growthProfile, closingQuote);
    console.log(display);

    process.exit(0);
  } catch (error) {
    if (error instanceof Anthropic.AuthenticationError) {
      displayError('Invalid API key. Check your ANTHROPIC_API_KEY.');
      process.exit(1);
    }
    if (error instanceof Anthropic.RateLimitError) {
      displayError('Rate limit reached. Try again in a moment.');
      process.exit(3);
    }
    if (error instanceof Anthropic.APIConnectionError) {
      displayError('Cannot reach Claude API. Check your connection.');
      process.exit(3);
    }
    if (error instanceof Anthropic.APIError) {
      displayError(`API error: ${error.message}`);
      process.exit(3);
    }

    throw error;
  }
}
