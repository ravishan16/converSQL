"""
Pytest fixtures and configuration for tests
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "AI_PROVIDER": "claude",
        "CLAUDE_API_KEY": "test-key",
        "CLAUDE_MODEL": "claude-3-5-sonnet-20241022",
        "AWS_DEFAULT_REGION": "us-west-2",
        "BEDROCK_MODEL_ID": "anthropic.claude-3-5-haiku-20241022-v1:0",
        "GOOGLE_API_KEY": "test-google-key",
        "GEMINI_MODEL": "gemini-1.5-pro",
        "PROCESSED_DATA_DIR": "data/processed/",
        "ENABLE_PROMPT_CACHE": "false",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def sample_schema():
    """Sample database schema for testing."""
    return """
    TABLE: data
    Columns:
    - LOAN_ID (VARCHAR): Unique loan identifier
    - STATE (VARCHAR): State code
    - CSCORE_B (INTEGER): Credit score
    - OLTV (FLOAT): Original loan-to-value ratio
    - DTI (FLOAT): Debt-to-income ratio
    - ORIG_UPB (FLOAT): Original unpaid principal balance
    - CURR_UPB (FLOAT): Current unpaid principal balance
    """


@pytest.fixture
def sample_question():
    """Sample user question for testing."""
    return "Show me loans in California with credit scores below 620"


@pytest.fixture
def sample_sql():
    """Sample SQL query for testing."""
    return """
    SELECT LOAN_ID, STATE, CSCORE_B, OLTV, DTI
    FROM data
    WHERE STATE = 'CA'
      AND CSCORE_B < 620
    LIMIT 20
    """


@pytest.fixture
def mock_boto3_client():
    """Mock boto3 client for Bedrock testing."""
    mock_client = MagicMock()
    mock_response = {"body": MagicMock(), "ResponseMetadata": {"HTTPStatusCode": 200}}
    mock_response["body"].read.return_value = b'{"content": [{"text": "SELECT * FROM data LIMIT 10"}]}'
    mock_client.invoke_model.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for Claude testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="SELECT * FROM data LIMIT 10")]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_gemini_model():
    """Mock Gemini model for testing."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "SELECT * FROM data LIMIT 10"
    mock_model.generate_content.return_value = mock_response
    return mock_model
