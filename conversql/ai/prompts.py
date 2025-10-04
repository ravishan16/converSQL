"""Prompt builders for AI SQL generation.

Thin wrapper over existing prompt logic to centralize access for new package layout.
"""

from typing import Any

try:
    from src.prompts import build_sql_generation_prompt as _legacy_build
except Exception:
    _legacy_build = None  # type: ignore


def build_sql_generation_prompt(user_question: str, schema_context: str) -> str:
    """Build the SQL generation prompt.

    Falls back to a minimal prompt if legacy module is not available.
    """
    if _legacy_build is not None:
        return _legacy_build(user_question, schema_context)
    return f"Write DuckDB SQL for: {user_question}\n\nSchema:\n{schema_context}"


__all__ = ["build_sql_generation_prompt"]
