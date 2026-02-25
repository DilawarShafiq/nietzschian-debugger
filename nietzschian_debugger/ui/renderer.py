"""Terminal output rendering using Rich."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.text import Text

console = Console()


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
    """Display an error message."""
    console.print(f"[bold red]Error:[/bold red] [red]{message}[/red]", stderr=True)


def display_warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"[yellow]{message}[/yellow]", stderr=True)


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
        "  [bold]export ANTHROPIC_API_KEY=your-key-here[/bold]\n\n"
        "Get a key at: [cyan]https://console.anthropic.com/[/cyan]\n"
    )
