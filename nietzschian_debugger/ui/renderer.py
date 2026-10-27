"""Terminal output rendering using Rich."""

from __future__ import annotations

import random
import sys
from contextlib import contextmanager

from rich.console import Console
from rich.text import Text

console = Console()
# Rich routes stderr via a Console constructed with stderr=True — NOT via a
# stderr= kwarg on .print() (which raises TypeError and crashed every error path).
error_console = Console(stderr=True)

# While the oracle ponders, it does not say "Thinking…". A different word each
# time, in the Nietzschian register — the wait itself should be in character.
_THINKING_WORDS = (
    "Revaluing",
    "Hammering",
    "Gazing into the abyss",
    "Transvaluing",
    "Philosophising",
    "Sharpening the blade",
    "Tuning the fork",
    "Unmasking the idol",
    "Weighing your soul",
    "Summoning the goblin",
    "Consulting Zarathustra",
    "Dancing on the edge",
    "Laughing in the dark",
    "Hunting the hollow note",
    "Willing it eternally",
)


@contextmanager
def thinking(word: str | None = None):
    """Show a spinner with a random Nietzschian word while an LLM call runs.

    The spinner is best-effort: if the terminal can't host a live status (piped
    output, no TTY) it's simply skipped. Exceptions from the wrapped call always
    propagate — only the spinner itself is guarded.
    """
    # A live spinner only makes sense on a real terminal. Off a TTY (piped output,
    # tests, CI) skip it entirely — no animation, no background refresh thread.
    if not console.is_terminal:
        yield
        return
    label = word or random.choice(_THINKING_WORDS)
    status = None
    try:
        status = console.status(f"[dim]{label}…[/dim]", spinner="dots")
        status.__enter__()
    except Exception:
        status = None
    try:
        yield
    finally:
        if status is not None:
            try:
                status.__exit__(None, None, None)
            except Exception:
                pass


def stream_to_terminal(text: str) -> None:
    """Write streaming text to stdout."""
    sys.stdout.write(text)
    sys.stdout.flush()


def new_line() -> None:
    """Print a blank line."""
    print()


def display_message(message: str) -> None:
    """Display a plain message."""
    console.print(message)


def display_bold(message: str) -> None:
    """Display a bold message."""
    console.print(f"[bold]{message}[/bold]")


def display_dim(message: str) -> None:
    """Display a dimmed message."""
    console.print(f"[dim]{message}[/dim]")


def display_error(message: str) -> None:
    """Display an error message on stderr."""
    error_console.print(f"[bold red]Error:[/bold red] [red]{message}[/red]")


def display_warning(message: str) -> None:
    """Display a warning message on stderr."""
    error_console.print(f"[yellow]{message}[/yellow]")


def display_success(message: str) -> None:
    """Display a success message."""
    console.print(f"[green]{message}[/green]")


def display_quote(text: str, philosopher: str) -> None:
    """Display a philosophical quote."""
    console.print(f'\n[dim]"{text}"[/dim]')
    console.print(f"[dim] -- {philosopher}[/dim]")


def display_session_header(intensity: str) -> None:
    """Display the session header with intensity level."""
    label = intensity.capitalize()
    console.print(f"\n[bold cyan]Nietzschian Debugger[/bold cyan] [dim][{label} mode][/dim]\n")


def display_prompt() -> None:
    """Display the input prompt."""
    console.print("[bold]> [/bold]", end="")


def display_api_key_help() -> None:
    """Display help for setting up the API key."""
    console.print(
        "\n[bold red]Missing API Key[/bold red]\n\n"
        "Set your Anthropic API key to use the Nietzschian Debugger:\n\n"
        "  [dim]# Linux / macOS[/dim]\n"
        '  [bold]export ANTHROPIC_API_KEY="your-key-here"[/bold]\n\n'
        "  [dim]# Windows (PowerShell)[/dim]\n"
        '  [bold]$env:ANTHROPIC_API_KEY = "your-key-here"[/bold]\n\n'
        "  [dim]# Windows (CMD)[/dim]\n"
        "  [bold]set ANTHROPIC_API_KEY=your-key-here[/bold]\n\n"
        "Get a key at: [cyan]https://console.anthropic.com/[/cyan]\n"
    )
