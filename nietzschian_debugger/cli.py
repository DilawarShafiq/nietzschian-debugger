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
    """The anti-AI debugger. What doesn't kill your code makes it stronger."""
    pass


@cli.command()
@click.argument("problem")
@click.option(
    "-i",
    "--intensity",
    type=click.Choice(VALID_INTENSITIES, case_sensitive=False),
    default="nietzsche",
    help="Questioning intensity: socrates, nietzsche, zarathustra",
)
def debug(problem: str, intensity: str) -> None:
    """Start an interactive debugging session.

    PROBLEM is the description of the bug or problem to debug.
    """
    asyncio.run(debug_command(problem, intensity))  # type: ignore[arg-type]


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
