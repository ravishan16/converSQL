"""
Unit tests for adapter implementations
Tests the actual behavior without complex mocking
"""

import pytest

from src.ai_engines.base import AIEngineAdapter
from src.ai_engines.bedrock_adapter import BedrockAdapter
from src.ai_engines.claude_adapter import ClaudeAdapter
from src.ai_engines.gemini_adapter import GeminiAdapter


class TestBaseAdapter:
    """Test suite for AIEngineAdapter base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that AIEngineAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AIEngineAdapter()

    def test_adapters_have_required_properties(self):
        """Test that all adapters implement required properties."""
        adapters = [BedrockAdapter(), ClaudeAdapter(), GeminiAdapter()]

        for adapter in adapters:
            assert hasattr(adapter, "name")
            assert hasattr(adapter, "provider_id")
            assert hasattr(adapter, "is_available")
            assert hasattr(adapter, "generate_sql")
            assert isinstance(adapter.name, str)
            assert isinstance(adapter.provider_id, str)
            assert isinstance(adapter.is_available(), bool)


class TestBedrockAdapter:
    """Test suite for BedrockAdapter."""

    def test_initialization(self):
        """Test BedrockAdapter initialization."""
        adapter = BedrockAdapter()
        assert adapter is not None
        assert adapter.name == "Amazon Bedrock"
        assert adapter.provider_id == "bedrock"

    def test_is_available_returns_bool(self):
        """Test is_available returns boolean."""
        adapter = BedrockAdapter()
        assert isinstance(adapter.is_available(), bool)

    def test_generate_sql_returns_tuple(self):
        """Test generate_sql returns tuple when not available."""
        adapter = BedrockAdapter()
        # If not configured, should return error tuple
        if not adapter.is_available():
            sql, error = adapter.generate_sql("test prompt")
            assert isinstance(sql, str)
            assert isinstance(error, str)
            assert sql == ""
            assert len(error) > 0

    def test_get_model_info(self):
        """Test get_model_info returns dict."""
        adapter = BedrockAdapter()
        info = adapter.get_model_info()
        assert isinstance(info, dict)
        assert "provider" in info


class TestClaudeAdapter:
    """Test suite for ClaudeAdapter."""

    def test_initialization(self):
        """Test ClaudeAdapter initialization."""
        adapter = ClaudeAdapter()
        assert adapter is not None
        assert adapter.name == "Claude API"
        assert adapter.provider_id == "claude"

    def test_is_available_returns_bool(self):
        """Test is_available returns boolean."""
        adapter = ClaudeAdapter()
        assert isinstance(adapter.is_available(), bool)

    def test_generate_sql_returns_tuple(self):
        """Test generate_sql returns tuple when not available."""
        adapter = ClaudeAdapter()
        # If not configured, should return error tuple
        if not adapter.is_available():
            sql, error = adapter.generate_sql("test prompt")
            assert isinstance(sql, str)
            assert isinstance(error, str)
            assert sql == ""
            assert len(error) > 0

    def test_get_model_info(self):
        """Test get_model_info returns dict."""
        adapter = ClaudeAdapter()
        info = adapter.get_model_info()
        assert isinstance(info, dict)
        assert "provider" in info


class TestGeminiAdapter:
    """Test suite for GeminiAdapter."""

    def test_initialization(self):
        """Test GeminiAdapter initialization."""
        adapter = GeminiAdapter()
        assert adapter is not None
        assert adapter.name == "Google Gemini"
        assert adapter.provider_id == "gemini"

    def test_is_available_returns_bool(self):
        """Test is_available returns boolean."""
        adapter = GeminiAdapter()
        assert isinstance(adapter.is_available(), bool)

    def test_generate_sql_returns_tuple(self):
        """Test generate_sql returns tuple when not available."""
        adapter = GeminiAdapter()
        # If not configured, should return error tuple
        if not adapter.is_available():
            sql, error = adapter.generate_sql("test prompt")
            assert isinstance(sql, str)
            assert isinstance(error, str)
            assert sql == ""
            assert len(error) > 0

    def test_get_model_info(self):
        """Test get_model_info returns dict."""
        adapter = GeminiAdapter()
        info = adapter.get_model_info()
        assert isinstance(info, dict)
        assert "provider" in info


class TestAdapterValidation:
    """Test adapter validation methods."""

    def test_validate_response(self):
        """Test validate_response method."""
        adapter = BedrockAdapter()

        # Valid SQL
        is_valid, msg = adapter.validate_response("SELECT * FROM table")
        assert is_valid is True

        # Empty SQL
        is_valid, msg = adapter.validate_response("")
        assert is_valid is False
        assert "empty" in msg.lower()

        # Not SQL
        is_valid, msg = adapter.validate_response("This is not SQL")
        assert is_valid is False

    def test_clean_sql_response(self):
        """Test clean_sql_response method."""
        adapter = BedrockAdapter()

        # Clean SQL with markdown
        sql = adapter.clean_sql_response("```sql\nSELECT * FROM table\n```")
        assert sql == "SELECT * FROM table"

        # SQL with prefix
        sql = adapter.clean_sql_response("Here's the SQL query: SELECT * FROM table")
        assert sql == "SELECT * FROM table"

        # Plain SQL
        sql = adapter.clean_sql_response("SELECT * FROM table")
        assert sql == "SELECT * FROM table"
