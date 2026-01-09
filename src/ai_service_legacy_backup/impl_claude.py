from src.ai_service import registry
from src.ai_service.base import AIEngine
from src.ai_engines.claude_adapter import ClaudeAdapter


class ClaudeAIEngine(AIEngine):
    def __init__(self):
        self.adapter = ClaudeAdapter()

    def generate_sql(self, user_question: str, schema_context: str) -> tuple[str, str]:
        if not self.adapter.is_available():
            return "", "Claude API key not configured"
        return self.adapter.generate_sql(user_question, schema_context)


def register_engine():
    if ClaudeAdapter().is_available():
        registry.register("claude", ClaudeAIEngine(), is_default=True)
