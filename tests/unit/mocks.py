from src.ai_service.base import AIEngine


class MockAIEngine(AIEngine):
    def generate_sql(self, user_question: str, schema_context: str) -> tuple[str, str]:
        return f"SELECT * FROM {user_question};", ""
