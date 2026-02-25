"""Behavior tagging for debug session transcripts."""

from __future__ import annotations

import json
from typing import Literal

from ..types import BehaviorTag, Turn
from ..llm.client import call_llm, get_conversation_model

TAGGER_SYSTEM_PROMPT = """You are a debugging behavior analyst. Given a debug session transcript, tag each developer response with observable reasoning behaviors.

For each turn, output ONLY a JSON array of behavior tags. Each tag must be one of:
- "guessed-without-evidence" (developer made assumption without checking data)
- "checked-logs" (developer referenced logs, data, or evidence)
- "questioned-assumption" (developer challenged their own or others' assumptions)
- "assumed-without-checking" (developer accepted something without verification)
- "narrowed-scope" (developer effectively narrowed down the problem space)
- "went-broad-unnecessarily" (developer expanded scope without justification)
- "asked-for-answer" (developer asked the tool for a direct answer)

Respond with valid JSON only. Format:
[{"turnNumber": 1, "tags": ["tag1", "tag2"]}, ...]"""


def _tag_to_dimension(
    tag: str,
) -> Literal["assumptionChecking", "evidenceGathering", "rootCauseSpeed"]:
    """Map a behavior tag to its scoring dimension."""
    mapping: dict[str, Literal["assumptionChecking", "evidenceGathering", "rootCauseSpeed"]] = {
        "guessed-without-evidence": "evidenceGathering",
        "checked-logs": "evidenceGathering",
        "questioned-assumption": "assumptionChecking",
        "assumed-without-checking": "assumptionChecking",
        "asked-for-answer": "assumptionChecking",
        "narrowed-scope": "rootCauseSpeed",
        "went-broad-unnecessarily": "rootCauseSpeed",
    }
    return mapping.get(tag, "evidenceGathering")


async def tag_session_behaviors(transcript: list[Turn]) -> list[BehaviorTag]:
    """Tag behaviors in a session transcript using the LLM."""
    if not transcript:
        return []

    formatted_transcript = "\n\n".join(
        f"Turn {t.turn_number}:\nQuestion: {t.question}\nDeveloper: {t.response}"
        for t in transcript
    )

    try:
        response = call_llm(
            TAGGER_SYSTEM_PROMPT,
            [{"role": "user", "content": formatted_transcript}],
            get_conversation_model(),
        )

        parsed = json.loads(response)
        behavior_tags: list[BehaviorTag] = []

        for entry in parsed:
            for tag in entry["tags"]:
                behavior_tags.append(
                    BehaviorTag(
                        turn_number=entry["turnNumber"],
                        tag=tag,
                        dimension=_tag_to_dimension(tag),
                    )
                )

        return behavior_tags
    except Exception:
        return []
