"""
Base AI Engine Adapter Interface
Defines the contract for all AI engine adapters in converSQL.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class AIEngineAdapter(ABC):
    """
    Abstract base class for AI engine adapters.

    All AI providers (Bedrock, Claude, Gemini, Ollama, etc.) must implement
    this interface to integrate with converSQL's AI service layer.

    The adapter pattern allows converSQL to support multiple AI providers
    with a unified interface, making it easy to add new engines or switch
    between providers based on availability and user preference.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI engine adapter.

        Args:
            config: Optional configuration dictionary containing provider-specific
                   settings (API keys, model IDs, region, endpoint, etc.)
        """
        self.config = config or {}
        self._initialize()

    @abstractmethod
    def _initialize(self) -> None:
        """
        Initialize the AI provider client/connection.

        This method should:
        - Set up API clients or connections
        - Validate credentials
        - Configure provider-specific settings
        - Handle initialization errors gracefully

        Implementation should not raise exceptions; instead, set internal
        state that can be checked via is_available().
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI engine is available and properly configured.

        Returns:
            bool: True if the engine is ready to generate SQL, False otherwise

        This method should check:
        - API credentials are present
        - Network connectivity (if applicable)
        - Provider service is accessible
        - All required configuration is present
        """
        pass

    @abstractmethod
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """
        Generate SQL query from natural language prompt.

        Args:
            prompt: Complete prompt including schema context, business rules,
                   ontological information, and user question

        Returns:
            Tuple[str, str]: (sql_query, error_message)
            - On success: (generated_sql, "")
            - On failure: ("", error_description)

        The generated SQL should:
        - Be syntactically valid
        - Reference only tables/columns in the provided schema
        - Follow best practices for query optimization
        - Include helpful comments when appropriate

        Error messages should be user-friendly and actionable.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the display name of this AI engine.

        Returns:
            str: Human-readable name (e.g., "Claude API", "AWS Bedrock", "Gemini")
        """
        pass

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """
        Get the unique identifier for this provider.

        Returns:
            str: Lowercase identifier (e.g., "claude", "bedrock", "gemini")
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the active model configuration.

        Returns:
            Dict with model information:
            - model_id: Model identifier
            - version: Model version
            - capabilities: List of capabilities
            - max_tokens: Maximum token limit
            - etc.

        Default implementation returns empty dict; override for model-specific info.
        """
        return {}

    def validate_response(self, sql: str) -> Tuple[bool, str]:
        """
        Validate the generated SQL response.

        Args:
            sql: Generated SQL query string

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
            - On valid: (True, "")
            - On invalid: (False, error_description)

        Default implementation performs basic validation.
        Override for provider-specific validation logic.
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query generated"

        sql_lower = sql.lower().strip()

        # Check for common SQL keywords
        sql_keywords = ["select", "insert", "update", "delete", "create", "drop", "with"]
        has_sql_keyword = any(sql_lower.startswith(keyword) for keyword in sql_keywords)

        if not has_sql_keyword:
            return False, "Generated text does not appear to be valid SQL"

        # Warn about dangerous operations (but don't block)
        dangerous_keywords = ["drop", "delete", "truncate", "alter"]
        if any(keyword in sql_lower for keyword in dangerous_keywords):
            return True, "Warning: Query contains potentially destructive operations"

        return True, ""

    def clean_sql_response(self, response: str) -> str:
        """
        Clean and extract SQL from AI response.

        Args:
            response: Raw response text from AI provider

        Returns:
            str: Cleaned SQL query

        Handles common patterns:
        - Removes markdown code blocks (```sql ... ```)
        - Strips leading/trailing whitespace
        - Removes explanatory text before/after SQL
        - Extracts SQL from mixed content
        """
        sql = response.strip()

        # Remove markdown code blocks
        if "```" in sql:
            # Extract content between ```sql and ``` or ``` and ```
            parts = sql.split("```")
            for i, part in enumerate(parts):
                part = part.strip()
                if part.startswith("sql"):
                    sql = part[3:].strip()
                    break
                elif i > 0 and (part.upper().startswith("SELECT") or part.upper().startswith("WITH")):
                    sql = part.strip()
                    break

        # Remove common AI response patterns
        prefixes_to_remove = [
            "here's the sql query:",
            "here is the sql query:",
            "sql query:",
            "query:",
        ]

        sql_lower = sql.lower()
        for prefix in prefixes_to_remove:
            if sql_lower.startswith(prefix):
                sql = sql[len(prefix) :].strip()
                break

        return sql

    def __repr__(self) -> str:
        """String representation of the adapter."""
        return f"<{self.__class__.__name__} provider={self.provider_id} available={self.is_available()}>"
