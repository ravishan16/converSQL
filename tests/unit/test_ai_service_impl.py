import unittest
from unittest.mock import patch

from src.services import ai_service
from tests.unit.mocks import MockAIEngine


class TestAIServiceImpl(unittest.TestCase):
    @patch("src.services.ai_service.registry")
    def test_get_ai_service(self, mock_registry):
        mock_engine = MockAIEngine()
        mock_registry.get_default.return_value = mock_engine
        service = ai_service.get_ai_service()
        self.assertIs(service, mock_engine)

    @patch("src.services.ai_service.get_ai_service")
    def test_generate_sql_with_ai(self, mock_get_ai_service):
        mock_engine = MockAIEngine()
        mock_get_ai_service.return_value = mock_engine
        sql, err = ai_service.generate_sql_with_ai("test_question", "test_schema")
        self.assertEqual(sql, "SELECT * FROM test_question;")
        self.assertEqual(err, "")

    @patch("src.services.ai_service.registry")
    def test_get_ai_service_status(self, mock_registry):
        mock_registry.get_available_engines.return_value = ["mock1", "mock2"]
        mock_registry._default_engine = "mock1"
        status = ai_service.get_ai_service_status()
        self.assertEqual(
            status, {"available": True, "active_provider": "mock1", "provider_status": {"mock1": True, "mock2": True}}
        )


if __name__ == "__main__":
    unittest.main()
