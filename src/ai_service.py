#!/usr/bin/env python3
"""
AI Service Module
Manages AI providers using the adapter pattern for SQL generation.
"""

import hashlib
import os
from typing import Any, Dict, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv

# Import new adapters
from src.ai_engines import BedrockAdapter, ClaudeAdapter, GeminiAdapter
try:
    # Prefer new unified prompt builder
    from conversql.ai.prompts import build_sql_generation_prompt  # type: ignore
except Exception:  # fallback to legacy
    from src.prompts import build_sql_generation_prompt  # type: ignore

# Load environment variables
load_dotenv()

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "claude").lower()
ENABLE_PROMPT_CACHE = os.getenv("ENABLE_PROMPT_CACHE", "true").lower() == "true"
PROMPT_CACHE_TTL = int(os.getenv("PROMPT_CACHE_TTL", "3600"))
CACHE_VERSION = 1  # bump to invalidate cached AI service instances


class AIServiceError(Exception):
    """Custom exception for AI service errors."""

    pass


class AIService:
    """Main AI service that manages multiple AI providers using adapter pattern."""

    def __init__(self):
        """Initialize AI service with all available adapters."""
        # Initialize all adapters
        self.adapters = {
            "bedrock": BedrockAdapter(),
            "claude": ClaudeAdapter(),
            "gemini": GeminiAdapter(),
        }

        self.active_provider = None
        self._determine_active_provider()

    def _determine_active_provider(self):
        """Determine which AI provider to use based on configuration and availability."""
        # First, try the configured provider
        if AI_PROVIDER in self.adapters and self.adapters[AI_PROVIDER].is_available():
            self.active_provider = AI_PROVIDER
            return

        # Fallback to first available provider
        for provider_id, adapter in self.adapters.items():
            if adapter.is_available():
                self.active_provider = provider_id
                print(f"ℹ️  Using {adapter.name} (fallback from {AI_PROVIDER})")
                return

        # No providers available
        self.active_provider = None

    def is_available(self) -> bool:
        """Check if any AI provider is available."""
        return self.active_provider is not None

    def get_active_provider(self) -> Optional[str]:
        """Get the currently active provider ID."""
        return self.active_provider

    def get_active_adapter(self):
        """Get the active adapter instance."""
        if self.active_provider:
            return self.adapters.get(self.active_provider)
        return None

    def get_available_providers(self) -> Dict[str, str]:
        """Get list of available providers with their display names."""
        available = {}
        for provider_id, adapter in self.adapters.items():
            if adapter.is_available():
                available[provider_id] = adapter.name
        return available

    def set_active_provider(self, provider_id: str) -> bool:
        """Manually set the active provider if available.

        Args:
            provider_id: The provider ID to set as active

        Returns:
            bool: True if provider was set successfully, False otherwise
        """
        if provider_id in self.adapters and self.adapters[provider_id].is_available():
            self.active_provider = provider_id
            return True
        return False

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {
            "active": self.active_provider,
        }

        for provider_id, adapter in self.adapters.items():
            status[provider_id] = adapter.is_available()

        return status

    def _create_prompt_hash(self, user_question: str, schema_context: str) -> str:
        """Create hash for prompt caching."""
        combined = f"{user_question}|{schema_context}|{self.active_provider}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _build_sql_prompt(self, user_question: str, schema_context: str) -> str:
        """Build the SQL generation prompt."""
        return build_sql_generation_prompt(user_question, schema_context)

    @st.cache_data(ttl=PROMPT_CACHE_TTL)
    def _cached_generate_sql(_self, user_question: str, schema_context: str, provider: str) -> Tuple[str, str]:
        """Cached SQL generation to reduce API calls."""
        # Cache decorator handles the caching
        # The actual generation happens in generate_sql
        return "", ""

    def generate_sql(self, user_question: str, schema_context: str) -> Tuple[str, str, str]:
        """
        Generate SQL query using available AI provider.

        Args:
            user_question: Natural language question
            schema_context: Database schema context

        Returns:
            Tuple[str, str, str]: (sql_query, error_message, provider_used)
        """
        if not self.is_available():
            error_msg = """🚫 **AI SQL Generation Unavailable**

No AI providers are configured or available. This could be due to:
- Missing API keys (Claude API key, AWS credentials, or Google API key)
- Network connectivity issues
- Service configuration problems

**You can still use the application by:**
- Writing SQL queries manually in the Advanced tab
- Using the sample queries provided
- Referring to the database schema for guidance

**To configure an AI provider:**
- Claude: Set CLAUDE_API_KEY in .env
- Bedrock: Configure AWS credentials
- Gemini: Set GOOGLE_API_KEY in .env"""
            return "", error_msg, "none"

        # Check cache if enabled
        if ENABLE_PROMPT_CACHE:
            try:
                cached_result = self._cached_generate_sql(user_question, schema_context, self.active_provider)
                if cached_result[0]:  # If cached result exists
                    return (
                        cached_result[0],
                        cached_result[1],
                        f"{self.active_provider} (cached)",
                    )
            except Exception:
                pass  # Cache miss or error, continue with API call

        # Build prompt
        prompt = self._build_sql_prompt(user_question, schema_context)

        # Get active adapter
        adapter = self.get_active_adapter()
        if not adapter:
            return "", "No AI adapter available", "none"

        # Generate SQL using adapter
        sql_query, error_msg = adapter.generate_sql(prompt)

        # Cache the result if successful and caching is enabled
        if ENABLE_PROMPT_CACHE and sql_query and not error_msg:
            try:
                # Update cache by calling the cached function
                self._cached_generate_sql(user_question, schema_context, self.active_provider)
            except Exception:
                pass  # Cache update failed, but we have the result

        return sql_query, error_msg, self.active_provider


# Global AI service instance (cached)
@st.cache_resource
def get_ai_service(cache_version: int = CACHE_VERSION) -> AIService:
    """Get or create global AI service instance (cached)."""
    return AIService()


# Convenience functions for backward compatibility
def initialize_ai_client() -> Tuple[Optional[AIService], str]:
    """Initialize AI client - backward compatibility."""
    service = get_ai_service()
    if service.is_available():
        provider = service.get_active_provider() or "none"
        return service, provider
    return None, "none"


def generate_sql_with_ai(user_question: str, schema_context: str) -> Tuple[str, str]:
    """Generate SQL with AI - backward compatibility."""
    service = get_ai_service()
    sql_query, error_msg, provider = service.generate_sql(user_question, schema_context)
    return sql_query, error_msg
