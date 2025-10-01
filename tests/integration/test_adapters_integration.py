"""
Integration tests for AI adapters
"""

import pytest

from src.ai_service import AIService


@pytest.mark.integration
class TestAdapterIntegration:
    """Integration tests for AI adapters."""

    @pytest.mark.skip(reason="Requires actual API credentials")
    @pytest.mark.requires_api
    def test_bedrock_real_api(self, sample_question, sample_schema):
        """Test Bedrock adapter with real API (requires AWS credentials)."""
        service = AIService()
        adapter = service.adapters.get("bedrock")

        if adapter and adapter.is_available():
            prompt = f"{sample_schema}\n\n{sample_question}"
            sql, error = adapter.generate_sql(prompt)
            assert isinstance(sql, str)
            assert isinstance(error, str)
            if sql:
                assert "SELECT" in sql.upper()
        else:
            pytest.skip("Bedrock adapter not available")

    @pytest.mark.skip(reason="Requires actual API credentials")
    @pytest.mark.requires_api
    def test_claude_real_api(self, sample_question, sample_schema):
        """Test Claude adapter with real API (requires API key)."""
        service = AIService()
        adapter = service.adapters.get("claude")

        if adapter and adapter.is_available():
            prompt = f"{sample_schema}\n\n{sample_question}"
            sql, error = adapter.generate_sql(prompt)
            assert isinstance(sql, str)
            assert isinstance(error, str)
            if sql:
                assert "SELECT" in sql.upper()
        else:
            pytest.skip("Claude adapter not available")

    @pytest.mark.skip(reason="Requires actual API credentials")
    @pytest.mark.requires_api
    def test_gemini_real_api(self, sample_question, sample_schema):
        """Test Gemini adapter with real API (requires API key)."""
        service = AIService()
        adapter = service.adapters.get("gemini")

        if adapter and adapter.is_available():
            prompt = f"{sample_schema}\n\n{sample_question}"
            sql, error = adapter.generate_sql(prompt)
            assert isinstance(sql, str)
            assert isinstance(error, str)
            if sql:
                assert "SELECT" in sql.upper()
        else:
            pytest.skip("Gemini adapter not available")

    def test_service_initialization(self):
        """Test AIService initializes without errors."""
        service = AIService()
        assert isinstance(service, AIService)
        assert hasattr(service, "adapters")
        assert len(service.adapters) > 0

    def test_adapter_fallback_behavior(self):
        """Test that service handles no available adapters gracefully."""
        service = AIService()

        # Get all available adapters
        available_adapters = [name for name, adapter in service.adapters.items() if adapter.is_available()]

        # Test should pass even if no adapters are available
        if available_adapters:
            adapter = service.get_active_adapter()
            assert adapter is not None
        else:
            adapter = service.get_active_adapter()
            assert adapter is None

    def test_generate_sql_with_no_providers(self, sample_question, sample_schema):
        """Test SQL generation when no providers are available."""
        service = AIService()

        # Generate SQL - should handle gracefully
        sql, error, provider = service.generate_sql(sample_question, sample_schema)

        assert isinstance(sql, str)
        assert isinstance(error, str)
        assert isinstance(provider, str)

        # If no providers available, should have error message
        if not service.is_available():
            assert len(error) > 0
            assert sql == ""
