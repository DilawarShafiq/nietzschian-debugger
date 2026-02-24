import type { Turn, BehaviorTag } from '../types.js';
import { callLLM, getConversationModel } from '../llm/client.js';

const TAGGER_SYSTEM_PROMPT = `You are a debugging behavior analyst. Given a debug session transcript, tag each developer response with observable reasoning behaviors.

For each turn, output ONLY a JSON array of behavior tags. Each tag must be one of:
- "guessed-without-evidence" (developer made assumption without checking data)
- "checked-logs" (developer referenced logs, data, or evidence)
- "questioned-assumption" (developer challenged their own or others' assumptions)
- "assumed-without-checking" (developer accepted something without verification)
- "narrowed-scope" (developer effectively narrowed down the problem space)
- "went-broad-unnecessarily" (developer expanded scope without justification)
- "asked-for-answer" (developer asked the tool for a direct answer)

Respond with valid JSON only. Format:
[{"turnNumber": 1, "tags": ["tag1", "tag2"]}, ...]`;

export async function tagSessionBehaviors(transcript: Turn[]): Promise<BehaviorTag[]> {
  if (transcript.length === 0) return [];

  const formattedTranscript = transcript
    .map((t) => `Turn ${t.turnNumber}:\nQuestion: ${t.question}\nDeveloper: ${t.response}`)
    .join('\n\n');

  try {
    const response = await callLLM(
      TAGGER_SYSTEM_PROMPT,
      [{ role: 'user', content: formattedTranscript }],
      getConversationModel(),
    );

    const parsed = JSON.parse(response) as Array<{ turnNumber: number; tags: string[] }>;
    const behaviorTags: BehaviorTag[] = [];

    for (const entry of parsed) {
      for (const tag of entry.tags) {
        behaviorTags.push({
          turnNumber: entry.turnNumber,
          tag,
          dimension: tagToDimension(tag),
        });
      }
    }

    return behaviorTags;
  } catch {
    return [];
  }
}

function tagToDimension(tag: string): BehaviorTag['dimension'] {
  switch (tag) {
    case 'guessed-without-evidence':
    case 'checked-logs':
      return 'evidenceGathering';
    case 'questioned-assumption':
    case 'assumed-without-checking':
    case 'asked-for-answer':
      return 'assumptionChecking';
    case 'narrowed-scope':
    case 'went-broad-unnecessarily':
      return 'rootCauseSpeed';
    default:
      return 'evidenceGathering';
  }
}
