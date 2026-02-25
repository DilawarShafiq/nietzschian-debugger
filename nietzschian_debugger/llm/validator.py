"""Response validation for the Nietzschian Debugger.

Ensures LLM responses contain questions and do not provide direct answers.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Optional

from ..types import Intensity
from .client import call_llm, get_conversation_model

ANSWER_PATTERNS = [
    re.compile(r"\bthe fix is\b", re.IGNORECASE),
    re.compile(r"\byou should change\b", re.IGNORECASE),
    re.compile(r"\btry doing\b", re.IGNORECASE),
    re.compile(r"\btry changing\b", re.IGNORECASE),
    re.compile(r"\btry replacing\b", re.IGNORECASE),
    re.compile(r"\bhere'?s (?:the|a) (?:fix|solution|answer)\b", re.IGNORECASE),
    re.compile(r"\bto fix this\b", re.IGNORECASE),
    re.compile(r"\bthe solution is\b", re.IGNORECASE),
    re.compile(r"\bjust (?:change|replace|update|add|remove)\b", re.IGNORECASE),
    re.compile(r"\byou need to (?:change|replace|update|add|remove)\b", re.IGNORECASE),
]

CODE_FIX_PATTERN = re.compile(
    r"```[\s\S]*?(?://\s*fix|//\s*changed|//\s*updated|\u2192|=>.*fix)[\s\S]*?```",
    re.IGNORECASE,
)


@dataclass
class ValidationResult:
    valid: bool
    reason: Optional[str] = None


def validate_response(response: str) -> ValidationResult:
    """Validate that a response contains a question and no direct answers."""
    has_question = "?" in response
    if not has_question:
        return ValidationResult(valid=False, reason="Response contains no question")

    for pattern in ANSWER_PATTERNS:
        if pattern.search(response):
            return ValidationResult(
                valid=False,
                reason=f"Response matches answer pattern: {pattern.pattern}",
            )

    if CODE_FIX_PATTERN.search(response):
        return ValidationResult(valid=False, reason="Response contains a code fix block")

    return ValidationResult(valid=True)


def reprompt_if_invalid(
    system_prompt: str,
    messages: list[dict[str, str]],
    invalid_response: str,
) -> Optional[str]:
    """Re-prompt the LLM if the previous response was invalid."""
    reprompt_messages = [
        *messages,
        {"role": "assistant", "content": invalid_response},
        {
            "role": "user",
            "content": (
                "Your previous response contained a direct answer or solution. "
                "Rewrite it as a question that leads the developer to discover this "
                "themselves. You must ONLY ask questions — never provide fixes or answers."
            ),
        },
    ]

    new_response = call_llm(system_prompt, reprompt_messages, get_conversation_model())
    check = validate_response(new_response)
    return new_response if check.valid else None


FALLBACK_QUESTIONS: dict[Intensity, list[str]] = {
    "socrates": [
        "What do you think might be happening here? What have you observed so far?",
        "Have you considered looking at the error message more carefully? What does it tell you?",
        "What would you expect to see if everything was working correctly?",
    ],
    "nietzsche": [
        "What evidence do you have for that assumption? Have you actually verified it?",
        "You seem to be guessing. What does the data actually show?",
        "What's the simplest thing you haven't checked yet?",
    ],
    "zarathustra": [
        "You're avoiding the hard question. What are you afraid to find?",
        "Your hypothesis is untested. What would disprove it?",
        "Stop theorizing. What does the actual execution trace show you?",
    ],
}


def get_fallback_question(intensity: Intensity) -> str:
    """Return a random fallback question for the given intensity."""
    questions = FALLBACK_QUESTIONS[intensity]
    return random.choice(questions)
