"""Read the developer's recent git changes as debugging context.

So the tool can interrogate what you *actually* changed -- "you touched the auth
middleware and now call it 'unrelated'; convince me" -- instead of only what you
chose to describe.
"""

from __future__ import annotations

import subprocess
from typing import Optional

MAX_DIFF_CHARS = 8000


def get_git_diff(ref: Optional[str] = None) -> Optional[str]:
    """Return uncommitted changes (vs HEAD), or the diff against ``ref``.

    Returns None when git is unavailable, the command fails, or there is no diff.
    Capped at MAX_DIFF_CHARS so a huge diff can't blow the context window.
    """
    cmd = ["git", "diff", ref] if ref else ["git", "diff", "HEAD"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    diff = (result.stdout or "").strip()
    if not diff:
        return None
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n... (diff truncated)"
    return diff
