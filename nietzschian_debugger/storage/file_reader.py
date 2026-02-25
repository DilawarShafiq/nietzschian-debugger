"""File reading and path detection for code context."""

from __future__ import annotations

import os
import re
from pathlib import Path

FILE_PATH_REGEX = re.compile(r"""(?:^|\s|["'`])([.~/][\w./-]+\.\w{1,10})(?=[\s"'`,:;)}\]]|$)""")

MAX_FILE_SIZE = 100_000  # ~100KB
MAX_LINES_FOR_CONTEXT = 500


def detect_file_paths(text: str) -> list[str]:
    """Detect file paths in text."""
    matches: list[str] = []
    for match in FILE_PATH_REGEX.finditer(text):
        path = match.group(1)
        if path and not path.startswith("http") and not path.startswith("//"):
            matches.append(path)
    return list(dict.fromkeys(matches))  # deduplicate while preserving order


async def read_code_file(file_path: str) -> str | None:
    """Read a code file, returning numbered lines or None if not accessible."""
    try:
        resolved = Path(file_path).resolve()
        if not resolved.is_file():
            return None

        file_size = resolved.stat().st_size
        if file_size > MAX_FILE_SIZE:
            content = resolved.read_text(encoding="utf-8")
            return _truncate_to_relevant_section(content)

        content = resolved.read_text(encoding="utf-8")
        return _add_line_numbers(content)
    except Exception:
        return None


def _add_line_numbers(content: str) -> str:
    """Add line numbers to content."""
    lines = content.split("\n")
    return "\n".join(f"{i + 1}: {line}" for i, line in enumerate(lines))


def _truncate_to_relevant_section(content: str) -> str:
    """Truncate large files, keeping head and tail sections."""
    lines = content.split("\n")
    if len(lines) <= MAX_LINES_FOR_CONTEXT:
        return _add_line_numbers(content)

    # Take first 100 lines (imports/setup) + last 400 lines (most recent code)
    head = lines[:100]
    tail = lines[-400:]
    truncated_lines = head + [f"\n... ({len(lines) - 500} lines omitted) ...\n"] + tail
    truncated = "\n".join(truncated_lines)
    return _add_line_numbers(truncated)


def format_code_context(files: dict[str, str]) -> str:
    """Format code files into a context string for the LLM."""
    if not files:
        return ""

    sections: list[str] = []
    for path, content in files.items():
        sections.append(f"--- File: {path} ---\n{content}")
    return "\n\n".join(sections)
