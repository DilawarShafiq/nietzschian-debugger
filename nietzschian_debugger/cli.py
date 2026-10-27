"""CLI entry point for the Nietzschian Debugger."""

from __future__ import annotations

import asyncio
import sys

import click

from . import __version__
from .commands.debug import debug_command

VALID_INTENSITIES = ("socrates", "nietzsche", "zarathustra")


@click.group()
@click.version_option(version=__version__, prog_name="nietzschian")
def cli() -> None:
    """It won't fix your bug. It'll fix you. What doesn't kill your code makes it stronger."""
    pass


@cli.command()
@click.argument("problem")
@click.option(
    "-i",
    "--intensity",
    "--lens",
    "lens",
    type=click.Choice(VALID_INTENSITIES, case_sensitive=False),
    default=None,
    help="Force one lens (socrates/nietzsche/zarathustra). Default: adaptive — it reads your state and shifts between them.",
)
@click.option(
    "--diff",
    "use_diff",
    is_flag=True,
    help="Feed your uncommitted git changes as context -- it interrogates what you actually changed.",
)
@click.option(
    "--since",
    "diff_since",
    default=None,
    help="With --diff, diff against this ref (commit/branch) instead of HEAD.",
)
@click.option(
    "--model",
    "model_spec",
    default=None,
    help="LLM to use (default: Claude). e.g. openai:gpt-4o-mini, ollama:llama3, gemini:gemini-1.5-flash.",
)
def debug(problem: str, lens: str, use_diff: bool, diff_since: str, model_spec: str) -> None:
    """Start an interactive debugging session.

    PROBLEM is the description of the bug or problem to debug.
    """
    from .llm import providers

    providers.configure(model_spec)
    asyncio.run(debug_command(problem, lens, use_diff, diff_since))  # type: ignore[arg-type]


@cli.command()
def demo() -> None:
    """Watch a scripted session with no API key -- then run it on your own bug."""
    from .commands.demo import run_demo

    run_demo()


@cli.command()
@click.option("--id", "session_id", default=None, help="Session id to share (default: the most recent).")
@click.option("-o", "--out", "out_path", default=None, help="Write the markdown to a file instead of stdout.")
def share(session_id: str, out_path: str) -> None:
    """Export a finished session as shareable markdown."""
    from .commands.share import share_session

    asyncio.run(share_session(session_id, out_path))


def main() -> None:
    """Main entry point."""
    # Windows consoles often default to cp1252, which cannot encode the
    # box-drawing characters in the growth profile (┣ ┗) or em-dashes in
    # questions — it crashes with UnicodeEncodeError at the "you solved it"
    # screen. Force UTF-8 so output renders on every terminal.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass
    cli()


if __name__ == "__main__":
    main()
