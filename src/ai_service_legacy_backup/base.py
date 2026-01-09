from typing import Protocol, Tuple


class AIEngine(Protocol):
    """Protocol for AI engine adapters."""

    def generate_sql(self, user_question: str, schema_context: str) -> Tuple[str, str]:
        """
        Generate SQL query from a user question and schema context.

        Args:
            user_question: The natural language question from the user.
            schema_context: The database schema context.

        Returns:
            A tuple containing the generated SQL query and any error message.
        """
        ...
