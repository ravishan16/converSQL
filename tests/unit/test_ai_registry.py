import unittest

from src.ai_service import registry
from tests.unit.mocks import MockAIEngine


class TestAIRegistry(unittest.TestCase):

    def setUp(self):
        # Clear the registry before each test
        registry._registry = {}
        registry._default_engine = None

    def test_register_and_get(self):
        mock_engine = MockAIEngine()
        registry.register("mock", mock_engine)
        retrieved_engine = registry.get("mock")
        self.assertIs(retrieved_engine, mock_engine)

    def test_register_default(self):
        mock_engine = MockAIEngine()
        registry.register("mock", mock_engine, is_default=True)
        default_engine = registry.get_default()
        self.assertIs(default_engine, mock_engine)

    def test_get_non_existent(self):
        retrieved_engine = registry.get("non_existent")
        self.assertIsNone(retrieved_engine)

    def test_get_default_none(self):
        default_engine = registry.get_default()
        self.assertIsNone(default_engine)

    def test_get_available_engines(self):
        registry.register("mock1", MockAIEngine())
        registry.register("mock2", MockAIEngine())
        available_engines = registry.get_available_engines()
        self.assertCountEqual(available_engines, ["mock1", "mock2"])


if __name__ == "__main__":
    unittest.main()
