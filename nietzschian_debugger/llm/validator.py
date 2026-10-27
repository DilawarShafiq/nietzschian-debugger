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

    # Exactly ONE question — "a single blade they cannot step around." A menu of
    # questions lets the developer flee to the easy one. More than one '?' → reject.
    if response.count("?") > 1:
        return ValidationResult(
            valid=False, reason="Response contains more than one question"
        )

    for pattern in ANSWER_PATTERNS:
        if pattern.search(response):
            return ValidationResult(
                valid=False,
                reason=f"Response matches answer pattern: {pattern.pattern}",
            )

    if CODE_FIX_PATTERN.search(response):
        return ValidationResult(valid=False, reason="Response contains a code fix block")

    return ValidationResult(valid=True)


# The cheap regex above misses leaks phrased without its banned phrases. A model-
# judge catches those, but costs a call — so only run it on turns that read like a
# diagnosis (assert a cause or a fix). Questions rarely trip these markers.
DIAGNOSIS_SMELL = re.compile(
    r"\b(because|the reason|that'?s why|caused by|due to|"
    r"the (?:bug|issue|problem|cause|fix) is|it'?s (?:probably|likely|actually|because)|"
    r"you (?:have|forgot|need to|should|missed|didn'?t)|simply|"
    r"all you (?:have|need)|just (?:add|remove|change|set|use|replace))\b",
    re.IGNORECASE,
)


def smells_like_diagnosis(response: str) -> bool:
    """Whether a response is assertive enough to be worth a model-judge leak check."""
    return bool(DIAGNOSIS_SMELL.search(response))


def judge_leaks_answer(response: str, problem_description: str) -> bool:
    """Ask a cheap model whether the response hands over the cause or the fix.

    Second pass for responses that pass the regex but read like a diagnosis.
    Returns True if the answer is given away. On any error, returns False so a
    failed judge call never blocks the session (the cheap pass already ran).
    """
    judge_system = (
        "You grade responses from a Socratic debugging tool that must NEVER reveal "
        "the cause or the fix — it may ONLY ask questions that make the developer "
        "find it themselves. Be strict."
    )
    judge_user = (
        f"The developer's bug:\n{problem_description}\n\n"
        f'The tool\'s response:\n"""\n{response}\n"""\n\n'
        "Does this response reveal the likely cause or the fix — either stated "
        "outright, or embedded in a leading question that effectively hands it over? "
        "Answer with exactly one word: YES or NO."
    )
    try:
        verdict = call_llm(
            judge_system,
            [{"role": "user", "content": judge_user}],
            get_conversation_model(),
        )
    except Exception:
        return False
    return verdict.strip().upper().startswith("YES")


def reprompt_if_invalid(
    system_prompt: str,
    messages: list[dict[str, str]],
    invalid_response: str,
    reason: Optional[str] = None,
) -> Optional[str]:
    """Re-prompt the LLM once, with an instruction tailored to the failure."""
    reason = reason or ""
    if "more than one question" in reason:
        instruction = (
            "You asked more than one question. Ask EXACTLY ONE -- a single question "
            "the developer cannot step around. Keep the sharpest one; cut the rest."
        )
    elif "no question" in reason:
        instruction = (
            "Your response asked nothing. End with exactly one pointed question that "
            "forces the developer to go and look."
        )
    else:
        instruction = (
            "Your previous response gave away the answer or the fix. Rewrite it as "
            "exactly one question that leads the developer to discover it themselves. "
            "Never state the cause or the fix."
        )

    reprompt_messages = [
        *messages,
        {"role": "assistant", "content": invalid_response},
        {"role": "user", "content": instruction},
    ]

    new_response = call_llm(system_prompt, reprompt_messages, get_conversation_model())
    check = validate_response(new_response)
    return new_response if check.valid else None


FALLBACK_QUESTIONS: dict[Intensity, list[str]] = {
    "socrates": [
        "What have you actually observed so far, step by step?",
        "What does the error message itself tell you, read slowly?",
        "What would you expect to see if everything were working correctly?",
    ],
    "nietzsche": [
        "You called it that like it absolves you — delete the comfortable word, now what actually happens?",
        "Where did that belief come from: did you earn it today, or inherit it from the last time it merely failed to break?",
        "Which file are you so sure is fine that you have not yet opened it?",
    ],
    "zarathustra": [
        "What are you afraid you will find if you actually look?",
        "What single observation would prove your current hypothesis wrong?",
        "What does the real execution trace show — not your theory of it?",
    ],
}


def get_fallback_question(intensity: Intensity) -> str:
    """Return a random fallback question for the given intensity."""
    questions = FALLBACK_QUESTIONS[intensity]
    return random.choice(questions)
