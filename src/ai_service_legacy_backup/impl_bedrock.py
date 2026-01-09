from src.ai_service import registry
from src.ai_service.base import AIEngine
from src.ai_engines.bedrock_adapter import BedrockAdapter


class BedrockAIEngine(AIEngine):
    def __init__(self):
        self.adapter = BedrockAdapter()

    def generate_sql(self, user_question: str, schema_context: str) -> tuple[str, str]:
        if not self.adapter.is_available():
            return "", "Bedrock not configured"
        return self.adapter.generate_sql(user_question, schema_context)


if BedrockAdapter().is_available():
    registry.register("bedrock", BedrockAIEngine())
