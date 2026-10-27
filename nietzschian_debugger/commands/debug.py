"""Debug command - starts an interactive debugging session."""

from __future__ import annotations

import asyncio
import sys

import anthropic

from ..types import Intensity
from ..llm.client import get_client, MissingApiKeyError
from ..core.session import create_session, finalize_session
from ..core.session_loop import run_session_loop
from ..storage.session_store import save_session
from ..scoring.behavior_tagger import tag_session_behaviors
from ..scoring.skill_scorer import compute_skill_scores
from ..scoring.growth_profile import compute_growth_profile
from ..quotes.selector import select_closing_quote
from ..ui.growth_display import render_growth_score
from ..ui.renderer import display_error, display_warning, display_api_key_help


async def debug_command(
    problem_description: str,
    lens: "str | None" = None,
    use_diff: bool = False,
    diff_since: "str | None" = None,
) -> None:
    """Run a full debugging session. lens=None means adaptive; else that lens is forced."""
    # Validate API key (Anthropic path only; other providers validate their own
    # key lazily on the first call).
    from ..llm import providers

    if providers.active() is None:
        try:
            get_client()
        except MissingApiKeyError:
            display_api_key_help()
            sys.exit(1)

    # Validate problem description
    if not problem_description or not problem_description.strip():
        display_error("Please provide a problem description.")
        print('\nUsage: nietzschian debug "Your problem description here"')
        sys.exit(2)

    # Create session (store the home/forced lens for the record)
    session = create_session(problem_description.strip(), lens or "nietzsche")

    # Optionally feed the developer's uncommitted changes as context, so the tool
    # can interrogate what they actually changed -- not just what they described.
    preloaded_context = None
    if use_diff:
        from ..storage.git_context import get_git_diff

        diff = get_git_diff(diff_since)
        if diff:
            preloaded_context = {"git diff (your uncommitted changes)": diff}
        else:
            display_warning("No git changes found; continuing without --diff.")

    try:
        # Run interactive session
        result = await run_session_loop(session, preloaded_context, forced_lens=lens)

        # Finalize session
        behavior_tags = session.behavior_tags
        skill_scores = session.skill_scores

        try:
            behavior_tags = await tag_session_behaviors(session.transcript)
            skill_scores = compute_skill_scores(behavior_tags)
        except Exception:
            # Scoring is best-effort
            pass

        finalize_session(session, result.outcome, skill_scores, behavior_tags)

        # Save session
        try:
            await save_session(session)
        except Exception:
            # Persistence is best-effort
            pass

        # Display growth score
        growth_profile = await compute_growth_profile()
        closing_quote = select_closing_quote(result.outcome)
        display = render_growth_score(session, growth_profile, closing_quote)
        print(display)

        sys.exit(0)

    except anthropic.AuthenticationError:
        display_error("Invalid API key. Check your ANTHROPIC_API_KEY.")
        sys.exit(1)
    except anthropic.RateLimitError:
        display_error("Rate limit reached. Try again in a moment.")
        sys.exit(3)
    except anthropic.APIConnectionError:
        display_error("Cannot reach Claude API. Check your connection.")
        sys.exit(3)
    except anthropic.APIError as e:
        display_error(f"API error: {e.message}")
        sys.exit(3)
