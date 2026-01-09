from src.ai_service import registry
from src.ai_service.base import AIEngine
from src.ai_engines.gemini_adapter import GeminiAdapter


class GeminiAIEngine(AIEngine):
    def __init__(self):
        self.adapter = GeminiAdapter()

    def generate_sql(self, user_question: str, schema_context: str) -> tuple[str, str]:
        if not self.adapter.is_available():
            return "", "Gemini API key not configured"
        return self.adapter.generate_sql(user_question, schema_context)


def register_engine():
    if GeminiAdapter().is_available():
        registry.register("gemini", GeminiAIEngine())
