"""AI service and adapters facade.

Exports:
- AIService, get_ai_service, generate_sql_with_ai
- Adapters re-exported for convenience
"""

from typing import Tuple, Optional

try:
    # Reuse existing implementation for now; internal modules will migrate gradually
    from src.ai_service import AIService, get_ai_service, generate_sql_with_ai, initialize_ai_client
    from src.ai_engines import BedrockAdapter, ClaudeAdapter, GeminiAdapter
except Exception:  # pragma: no cover - fallback if used as stand-alone package later
    AIService = object  # type: ignore
    BedrockAdapter = object  # type: ignore
    ClaudeAdapter = object  # type: ignore
    GeminiAdapter = object  # type: ignore

__all__ = [
    "AIService",
    "get_ai_service",
    "generate_sql_with_ai",
    "initialize_ai_client",
    "BedrockAdapter",
    "ClaudeAdapter",
    "GeminiAdapter",
]
