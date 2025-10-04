"""Query history utilities for converSQL.

Provides a single helper to update (prepend) entries in the local in-memory
query history stored in Streamlit session state or any list-like container.

Design goals:
- Keep only the most recent `limit` entries (default 15)
- Distinguish entry types: "ai" | "manual"
- Provide stable ordering (newest first)
- Avoid mutation surprises: operate in-place but also return the list
- Minimal validation; caller is responsible for ensuring required keys

Each entry is a dict with keys (not enforced strictly):
  type: str ("ai" or "manual")
  question: Optional[str]
  sql: str
  provider: str (AI provider name or "manual")
  time: float (seconds taken)
  ts: float (epoch timestamp)

"""

from __future__ import annotations

from typing import Any, Dict, List

DEFAULT_HISTORY_LIMIT = 15


def update_local_history(
    history: List[Dict[str, Any]] | None,
    *,
    entry: Dict[str, Any],
    limit: int = DEFAULT_HISTORY_LIMIT,
) -> List[Dict[str, Any]]:
    """Insert an entry at the front of history, trimming to ``limit``.

    Args:
        history: Existing history list (may be None) that will be mutated.
        entry: The new entry to prepend.
        limit: Maximum length of the history to keep (default 15).

    Returns:
        The updated history list (same object if non-None; new list otherwise).
    """
    if limit <= 0:
        limit = DEFAULT_HISTORY_LIMIT

    if history is None:
        history = []

    # Prepend new entry
    history.insert(0, entry)

    # Trim in-place
    if len(history) > limit:
        del history[limit:]

    return history


__all__ = ["update_local_history", "DEFAULT_HISTORY_LIMIT"]
