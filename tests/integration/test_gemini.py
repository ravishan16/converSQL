import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv

from src.ai_engines.gemini_adapter import GeminiAdapter

load_dotenv()

adapter = GeminiAdapter()

print(f"Adapter: {adapter}")
print(f"Adapter is available: {adapter.is_available()}")

if adapter.is_available():
    sql, error = adapter.generate_sql("Show me loans in California with credit scores below 620")
    print(f"SQL: {sql}")
    print(f"Error: {error}")
