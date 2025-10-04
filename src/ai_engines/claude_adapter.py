"""
Claude API AI Engine Adapter
Implements converSQL adapter interface for Anthropic Claude API.
"""

import os
from typing import Any, Dict, Optional, Tuple

from .base import AIEngineAdapter


class ClaudeAdapter(AIEngineAdapter):
    """
    Anthropic Claude API engine adapter.

    Supports direct API access to Claude models via Anthropic API.
    Requires CLAUDE_API_KEY environment variable.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Claude adapter.

        Args:
            config: Configuration dict with keys:
                - api_key: Claude API key (default from env)
                - model: Model name (default from env)
                - max_tokens: Maximum response tokens
        """
        self.client: Optional[Any] = None
        self.api_key: Optional[str] = None
        self.model: Optional[str] = None
        self.max_tokens: Optional[int] = None
        super().__init__(config)

    def _initialize(self) -> None:
        """Initialize Claude API client."""
        # Get configuration
        self.api_key = self.config.get("api_key", os.getenv("CLAUDE_API_KEY"))
        self.model = self.config.get("model", os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"))
        self.max_tokens = self.config.get("max_tokens", 4000)

        if not self.api_key:
            return

        try:
            import anthropic

            # Initialize Claude client
            self.client = anthropic.Anthropic(api_key=self.api_key)

            # Optional: Test connection with minimal request
            # If test fails, still keep client - it might work for actual requests
            try:
                self.client.messages.create(
                    model=self.model, max_tokens=10, messages=[{"role": "user", "content": "test"}]
                )
            except Exception:
                # Keep client - API key might be valid but test failed
                pass

        except ImportError:
            print("⚠️ anthropic package not installed. Run: pip install anthropic")
            self.client = None
        except Exception as e:
            print(f"⚠️ Claude initialization failed: {e}")
            print("   Check CLAUDE_API_KEY environment variable")
            self.client = None

    def is_available(self) -> bool:
        """Check if Claude API client is initialized and ready."""
        return self.client is not None and self.api_key is not None and self.model is not None

    def _generate_sql_impl(self, prompt: str) -> Tuple[str, str]:
        """
        Generate SQL using Claude API.

        Args:
            prompt: Complete prompt with schema and question

        Returns:
            Tuple[str, str]: (sql_query, error_message)
        """
        if not self.is_available():
            return "", "Claude API not available. Check CLAUDE_API_KEY configuration."

        try:
            # Call Claude API
            client = self.client
            model = self.model
            max_tokens = self.max_tokens
            if client is None or model is None or max_tokens is None:
                return "", "Claude API not available. Check CLAUDE_API_KEY configuration."

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.0,  # Deterministic for SQL generation
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract SQL from response
            if response.content and len(response.content) > 0:
                raw_sql = response.content[0].text
                sql_query = self.clean_sql_response(raw_sql)

                # Validate response
                is_valid, validation_msg = self.validate_response(sql_query)
                if not is_valid:
                    return "", f"Invalid SQL generated: {validation_msg}"

                return sql_query, ""
            else:
                return "", "Claude returned empty response"

        except Exception as e:
            error_msg = f"Claude API error: {str(e)}"

            # Provide helpful error messages for common issues
            error_lower = str(e).lower()
            if "api_key" in error_lower or "authentication" in error_lower:
                error_msg += "\nCheck CLAUDE_API_KEY environment variable"
            elif "rate" in error_lower or "quota" in error_lower:
                error_msg += "\nAPI rate limit or quota exceeded"
            elif "model" in error_lower:
                error_msg += f"\nModel {model} may not be available or accessible"

            return "", error_msg

    @property
    def name(self) -> str:
        """Display name for this engine."""
        return "Claude API"

    @property
    def provider_id(self) -> str:
        """Unique provider identifier."""
        return "claude"

    def get_model_info(self) -> Dict[str, Any]:
        """Get Claude model configuration details."""
        return {
            "provider": "Anthropic Claude",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": 0.0,
            "api_version": "messages-2023-12-15",
            "capabilities": [
                "SQL generation",
                "Natural language understanding",
                "Schema comprehension",
                "Business domain reasoning",
            ],
        }
