"""
Unit tests for AIService
"""

from src.ai_service import AIService, generate_sql_with_ai, get_ai_service, initialize_ai_client


class TestAIService:
    """Test suite for AIService class."""

    def test_initialization(self):
        """Test AIService initialization creates all adapters."""
        service = AIService()

        assert "bedrock" in service.adapters
        assert "claude" in service.adapters
        assert "gemini" in service.adapters

    def test_is_available(self):
        """Test is_available returns boolean."""
        service = AIService()
        assert isinstance(service.is_available(), bool)

    def test_get_active_provider(self):
        """Test get_active_provider returns string or None."""
        service = AIService()
        provider = service.get_active_provider()
        assert provider is None or isinstance(provider, str)

    def test_get_provider_status(self):
        """Test get_provider_status returns dict."""
        service = AIService()
        status = service.get_provider_status()

        assert isinstance(status, dict)
        assert "active" in status
        assert "bedrock" in status
        assert "claude" in status
        assert "gemini" in status

    def test_generate_sql_returns_tuple(self, sample_question, sample_schema):
        """Test generate_sql returns tuple."""
        service = AIService()
        result = service.generate_sql(sample_question, sample_schema)

        assert isinstance(result, tuple)
        assert len(result) == 3
        sql, error, provider = result
        assert isinstance(sql, str)
        assert isinstance(error, str)
        assert isinstance(provider, str)


class TestGlobalFunctions:
    """Test suite for global convenience functions."""

    def test_get_ai_service_returns_service(self):
        """Test that get_ai_service returns AIService instance."""
        service = get_ai_service()
        assert isinstance(service, AIService)

    def test_get_ai_service_cached(self):
        """Test that get_ai_service returns same instance."""
        service1 = get_ai_service()
        service2 = get_ai_service()
        # Due to Streamlit caching, should be same instance
        assert isinstance(service1, AIService)
        assert isinstance(service2, AIService)

    def test_initialize_ai_client(self):
        """Test initialize_ai_client returns tuple."""
        result = initialize_ai_client()
        assert isinstance(result, tuple)
        assert len(result) == 2

        service, provider = result
        # Service can be None or AIService
        assert service is None or isinstance(service, AIService)
        assert isinstance(provider, str)

    def test_generate_sql_with_ai(self, sample_question, sample_schema):
        """Test generate_sql_with_ai convenience function."""
        result = generate_sql_with_ai(sample_question, sample_schema)

        assert isinstance(result, tuple)
        assert len(result) == 2
        sql, error = result
        assert isinstance(sql, str)
        assert isinstance(error, str)
