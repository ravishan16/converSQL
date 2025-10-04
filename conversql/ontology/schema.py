"""Schema context builders.

Provides functions to build AI-facing schema strings from datasets and ontologies.
"""

from __future__ import annotations

from typing import List


def build_schema_context_from_parquet(files: List[str]) -> str:
    """Delegate to existing enhanced schema generation to avoid duplication."""
    try:
        from src.data_dictionary import generate_enhanced_schema_context

        return generate_enhanced_schema_context(files)
    except Exception:
        # Minimal fallback if legacy module is not present
        context_lines = ["-- Schema (fallback)"]
        for f in files:
            context_lines.append(f"-- Parquet table: {f}")
        return "\n".join(context_lines)


__all__ = ["build_schema_context_from_parquet"]
