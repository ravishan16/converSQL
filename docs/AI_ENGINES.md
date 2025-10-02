# AI Engine Development Guide

<p align="center">
    <img src="../assets/conversql_logo.svg" alt="converSQL logo" width="320" />
</p>

## Overview

converSQL uses a modular **adapter pattern** for AI engine integration, making it easy to add support for new AI providers. This guide walks you through creating a new AI engine adapter from scratch.

---

## Architecture

### The Adapter Pattern

converSQL separates AI provider logic into independent adapters:

```
┌─────────────────────────────────────────────────────┐
│              AIService (Orchestrator)                │
│  - Manages multiple adapters                         │
│  - Determines active provider                        │
│  - Handles fallback and caching                      │
└───────────┬─────────────────────────────────────────┘
            │
            ├─────────────┬──────────────┬─────────────┐
            │             │              │             │
    ┌───────▼──────┐  ┌──▼───────┐  ┌──▼───────┐  ┌──▼───────┐
    │   Bedrock    │  │  Claude  │  │  Gemini  │  │  Ollama  │
    │   Adapter    │  │  Adapter │  │  Adapter │  │  Adapter │
    └──────────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Key Benefits

- **Modularity**: Each adapter is self-contained
- **Extensibility**: Add new providers without changing core logic
- **Flexibility**: Easy to switch between providers
- **Testing**: Mock adapters for testing without API calls
- **Community**: Contributors can add providers independently

---

## Quick Start: Adding a New Engine

### Step 1: Understand the Interface

Every AI engine adapter must implement these methods:

```python
class AIEngineAdapter:
    """Base interface for AI engine adapters."""
    
    def __init__(self):
        """Initialize the adapter and its client."""
        pass
    
    def _initialize(self):
        """
        Set up the AI client with API keys, configuration, etc.
        Should set self.client to the initialized client or None if unavailable.
        """
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """
        Check if this AI engine is available and configured.
        
        Returns:
            True if the engine can be used, False otherwise
        """
        raise NotImplementedError
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """
        Generate SQL from a prompt.
        
        Args:
            prompt: Complete prompt including user question, schema, and instructions
        
        Returns:
            Tuple of (sql_query, error_message)
            - If successful: (generated_sql, "")
            - If failed: ("", error_description)
        """
        raise NotImplementedError
```

### Step 2: Create Your Adapter

Let's implement a Gemini adapter as an example:

```python
# src/ai_engines/gemini_adapter.py

import os
from typing import Tuple

class GeminiAdapter:
    """Gemini AI adapter for SQL generation."""
    
    def __init__(self):
        self.client = None
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini client."""
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("⚠️ GEMINI_API_KEY not found in environment")
            return
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name)
            
            # Test with a simple request
            response = self.client.generate_content("test")
            print(f"✅ Gemini adapter initialized ({self.model_name})")
            
        except ImportError:
            print("⚠️ google-generativeai package not installed")
            print("   Run: pip install google-generativeai")
            self.client = None
        except Exception as e:
            print(f"⚠️ Gemini initialization failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.client is not None
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """Generate SQL using Gemini."""
        if not self.client:
            return "", "Gemini client not available"
        
        try:
            response = self.client.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean up response (remove markdown formatting if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            return sql_query, ""
            
        except Exception as e:
            error_msg = f"Gemini error: {str(e)}"
            return "", error_msg
```

### Step 3: Register the Adapter

Add your adapter to the AIService class in `src/ai_service.py`:

```python
# Import your new adapter
from src.ai_engines.gemini_adapter import GeminiAdapter

class AIService:
    """Main AI service that manages multiple providers."""
    
    def __init__(self):
        self.bedrock = BedrockClient()
        self.claude = ClaudeClient()
        self.gemini = GeminiAdapter()  # Add your adapter
        self.active_provider = None
        self._determine_active_provider()
    
    def _determine_active_provider(self):
        """Determine which AI provider to use."""
        ai_provider = os.getenv('AI_PROVIDER', 'bedrock').lower()
        
        # Check preferred provider first
        if ai_provider == 'gemini' and self.gemini.is_available():
            self.active_provider = 'gemini'
        elif ai_provider == 'claude' and self.claude.is_available():
            self.active_provider = 'claude'
        elif ai_provider == 'bedrock' and self.bedrock.is_available():
            self.active_provider = 'bedrock'
        # Fallback to any available provider
        elif self.gemini.is_available():
            self.active_provider = 'gemini'
        elif self.claude.is_available():
            self.active_provider = 'claude'
        elif self.bedrock.is_available():
            self.active_provider = 'bedrock'
        else:
            self.active_provider = None
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {
            'bedrock': self.bedrock.is_available(),
            'claude': self.claude.is_available(),
            'gemini': self.gemini.is_available(),  # Add your adapter
            'active': self.active_provider
        }
    
    def generate_sql(self, user_question: str, schema_context: str) -> Tuple[str, str, str]:
        """Generate SQL using active provider."""
        if not self.is_available():
            return "", "No AI providers available", "none"
        
        prompt = self._build_sql_prompt(user_question, schema_context)
        
        # Route to appropriate adapter
        if self.active_provider == 'gemini':
            sql_query, error_msg = self.gemini.generate_sql(prompt)
        elif self.active_provider == 'claude':
            sql_query, error_msg = self.claude.generate_sql(prompt)
        elif self.active_provider == 'bedrock':
            sql_query, error_msg = self.bedrock.generate_sql(prompt)
        else:
            return "", "No active provider", "none"
        
        return sql_query, error_msg, self.active_provider
```

### Step 4: Add Configuration

Update `.env.example` and documentation:

```bash
# AI Provider Configuration
AI_PROVIDER=gemini  # Options: bedrock, claude, gemini, ollama

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro  # or gemini-pro-vision, gemini-ultra
```

### Step 5: Add Dependencies

Update `requirements.txt`:

```
# Gemini AI support
google-generativeai>=0.3.0
```

### Step 6: Test Your Adapter

Create tests in `tests/test_gemini_adapter.py`:

```python
import pytest
from unittest.mock import Mock, patch
from src.ai_engines.gemini_adapter import GeminiAdapter

def test_gemini_initialization():
    """Test Gemini adapter initialization."""
    adapter = GeminiAdapter()
    # With mock API key, should initialize
    assert adapter is not None

def test_gemini_availability():
    """Test checking if Gemini is available."""
    adapter = GeminiAdapter()
    # This will depend on environment configuration
    is_available = adapter.is_available()
    assert isinstance(is_available, bool)

@patch('google.generativeai.GenerativeModel')
def test_gemini_sql_generation(mock_model):
    """Test SQL generation with Gemini."""
    # Mock the Gemini response
    mock_response = Mock()
    mock_response.text = "SELECT * FROM data LIMIT 10"
    mock_model.return_value.generate_content.return_value = mock_response
    
    adapter = GeminiAdapter()
    adapter.client = mock_model.return_value
    
    prompt = "Test prompt"
    sql, error = adapter.generate_sql(prompt)
    
    assert sql == "SELECT * FROM data LIMIT 10"
    assert error == ""

def test_gemini_error_handling():
    """Test error handling in Gemini adapter."""
    adapter = GeminiAdapter()
    adapter.client = None  # Simulate unavailable client
    
    sql, error = adapter.generate_sql("test")
    
    assert sql == ""
    assert "not available" in error.lower()
```

Run tests:

```bash
pytest tests/test_gemini_adapter.py -v
```

---

## Complete Example: Ollama Adapter

Ollama is a popular self-hosted LLM platform. Here's a complete implementation:

### Implementation

```python
# src/ai_engines/ollama_adapter.py

import os
import requests
from typing import Tuple

class OllamaAdapter:
    """Ollama adapter for local/self-hosted AI models."""
    
    def __init__(self):
        self.client = None
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama2')
        self._initialize()
    
    def _initialize(self):
        """Initialize Ollama connection."""
        try:
            # Test connection to Ollama server
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name in model_names:
                    self.client = True  # Mark as available
                    print(f"✅ Ollama adapter initialized ({self.model_name})")
                else:
                    print(f"⚠️ Model '{self.model_name}' not found in Ollama")
                    print(f"   Available models: {', '.join(model_names)}")
                    self.client = None
            else:
                print(f"⚠️ Ollama server returned status {response.status_code}")
                self.client = None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not connect to Ollama at {self.base_url}")
            print(f"   Make sure Ollama is running: ollama serve")
            self.client = None
        except Exception as e:
            print(f"⚠️ Ollama initialization failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        return self.client is not None
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """Generate SQL using Ollama."""
        if not self.client:
            return "", "Ollama not available"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Lower temperature for more consistent SQL
                        "top_p": 0.9,
                    }
                },
                timeout=60  # Longer timeout for local processing
            )
            
            if response.status_code == 200:
                result = response.json()
                sql_query = result['response'].strip()
                
                # Clean up markdown formatting
                if sql_query.startswith("```sql"):
                    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                
                return sql_query, ""
            else:
                return "", f"Ollama returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "", "Ollama request timed out (model may be too slow)"
        except Exception as e:
            return "", f"Ollama error: {str(e)}"
```

### Configuration

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434  # Default local URL
OLLAMA_MODEL=llama2  # Options: llama2, codellama, mistral, etc.
```

### Setup Instructions

Document setup in `docs/OLLAMA_SETUP.md`:

```markdown
# Ollama Setup Guide

## Installation

1. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Pull a model**:
   ```bash
   ollama pull llama2
   # Or for code-focused model:
   ollama pull codellama
   ```

3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

## Configuration

Add to your `.env`:
```bash
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

## Testing

Test your setup:
```bash
curl http://localhost:11434/api/tags
```

Should return list of installed models.
```

---

## Best Practices

### Error Handling

Always handle errors gracefully:

```python
def generate_sql(self, prompt: str) -> Tuple[str, str]:
    """Generate SQL with comprehensive error handling."""
    if not self.client:
        return "", "Client not initialized"
    
    try:
        # API call logic
        response = self.client.generate(prompt)
        return response.text, ""
        
    except TimeoutError:
        return "", "Request timed out - try again or check connectivity"
    except AuthenticationError:
        return "", "Authentication failed - check API key"
    except RateLimitError:
        return "", "Rate limit exceeded - try again later"
    except APIError as e:
        return "", f"API error: {str(e)}"
    except Exception as e:
        return "", f"Unexpected error: {str(e)}"
```

### Configuration Validation

Validate configuration on initialization:

```python
def _initialize(self):
    """Initialize with validation."""
    api_key = os.getenv('NEW_ENGINE_API_KEY')
    
    # Check required configuration
    if not api_key:
        print("❌ NEW_ENGINE_API_KEY not set")
        print("   Add to .env: NEW_ENGINE_API_KEY=your_key")
        return
    
    if len(api_key) < 20:
        print("⚠️ NEW_ENGINE_API_KEY appears invalid (too short)")
        return
    
    # Validate other settings
    model = os.getenv('NEW_ENGINE_MODEL', 'default-model')
    valid_models = ['model-a', 'model-b', 'model-c']
    
    if model not in valid_models:
        print(f"⚠️ Invalid model: {model}")
        print(f"   Valid options: {', '.join(valid_models)}")
        return
    
    # Continue with initialization...
```

### Prompt Optimization

Different engines may need different prompt formats:

```python
def generate_sql(self, prompt: str) -> Tuple[str, str]:
    """Generate SQL with engine-specific prompt optimization."""
    
    # Some engines work better with specific formatting
    if self.engine_type == 'code-focused':
        # Add code-specific instructions
        prompt = f"```sql\n{prompt}\n```"
    elif self.engine_type == 'chat-based':
        # Format as conversation
        prompt = f"User: {prompt}\n\nAssistant:"
    
    # Make API call
    response = self.client.generate(prompt)
    
    # Clean up response based on engine behavior
    sql = self._clean_response(response.text)
    
    return sql, ""

def _clean_response(self, response: str) -> str:
    """Clean engine-specific artifacts from response."""
    # Remove markdown code blocks
    if "```sql" in response:
        response = response.split("```sql")[1].split("```")[0]
    
    # Remove chat-style prefixes
    if response.startswith("Assistant:"):
        response = response.replace("Assistant:", "").strip()
    
    return response.strip()
```

---

## Testing Strategies

### Unit Tests

Test adapter logic without API calls:

```python
@patch('your_engine.Client')
def test_adapter_logic(mock_client):
    """Test adapter with mocked API."""
    mock_client.return_value.generate.return_value = "SELECT * FROM data"
    
    adapter = YourAdapter()
    adapter.client = mock_client.return_value
    
    sql, error = adapter.generate_sql("test prompt")
    
    assert sql == "SELECT * FROM data"
    assert error == ""
    mock_client.return_value.generate.assert_called_once()
```

### Integration Tests

Test with real API (mark as slow):

```python
@pytest.mark.slow
@pytest.mark.integration
def test_real_api_call():
    """Test with real API (requires valid credentials)."""
    adapter = YourAdapter()
    
    if not adapter.is_available():
        pytest.skip("API not configured")
    
    prompt = "SELECT COUNT(*) FROM test_table"
    sql, error = adapter.generate_sql(prompt)
    
    assert sql
    assert not error
    assert "SELECT" in sql.upper()
```

### Mock Server for Testing

Create a mock API server for testing:

```python
import pytest
from flask import Flask, request, jsonify
import threading

@pytest.fixture
def mock_api_server():
    """Start a mock API server for testing."""
    app = Flask(__name__)
    
    @app.route('/api/generate', methods=['POST'])
    def generate():
        data = request.json
        return jsonify({
            "response": "SELECT * FROM data LIMIT 10",
            "model": data.get('model', 'test-model')
        })
    
    server = threading.Thread(target=lambda: app.run(port=5555))
    server.daemon = True
    server.start()
    
    yield "http://localhost:5555"
    
    # Server stops when test ends

def test_with_mock_server(mock_api_server):
    """Test adapter with mock server."""
    os.environ['ENGINE_BASE_URL'] = mock_api_server
    
    adapter = YourAdapter()
    sql, error = adapter.generate_sql("test")
    
    assert sql == "SELECT * FROM data LIMIT 10"
```

---

## Documentation

### Setup Guide

Create `docs/YOUR_ENGINE_SETUP.md`:

```markdown
# [Your Engine] Setup Guide

## Overview
Brief description of the AI engine and why users might choose it.

## Prerequisites
- Requirements (API keys, installations, etc.)
- Cost considerations
- Account setup

## Installation

### 1. Get API Credentials
Steps to obtain API key...

### 2. Install Dependencies
```bash
pip install your-engine-library
```

### 3. Configure converSQL
Add to `.env`:
```bash
AI_PROVIDER=your_engine
YOUR_ENGINE_API_KEY=xxx
YOUR_ENGINE_MODEL=model-name
```

## Testing
How to test the setup...

## Troubleshooting
Common issues and solutions...
```

### Update Main Documentation

Add to `README.md`:
- List your engine as supported
- Add badge if applicable
- Link to setup guide

Update `docs/AI_ENGINES.md`:
- Add your engine to the list
- Provide implementation example
- Note any special considerations

---

## Performance Considerations

### Caching

Implement caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def _cached_generate(prompt_hash: str, schema_hash: str) -> Tuple[str, str]:
    """Cache SQL generation results."""
    # This will be called by generate_sql
    pass

def generate_sql(self, prompt: str) -> Tuple[str, str]:
    """Generate SQL with caching."""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    
    # Check cache
    try:
        return self._cached_generate(prompt_hash, schema_hash)
    except:
        pass
    
    # Generate if not cached
    return self._make_api_call(prompt)
```

### Rate Limiting

Implement rate limiting to avoid API throttling:

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old calls outside the period
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # Wait if at limit
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.calls.append(now)

class YourAdapter:
    def __init__(self):
        self.rate_limiter = RateLimiter(max_calls=10, period=60)  # 10 calls per minute
        self._initialize()
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """Generate SQL with rate limiting."""
        self.rate_limiter.wait_if_needed()
        
        # Make API call
        return self._make_api_call(prompt)
```

### Async Support (Advanced)

For high-throughput scenarios:

```python
import asyncio
from typing import Tuple

class AsyncAdapter:
    async def generate_sql_async(self, prompt: str) -> Tuple[str, str]:
        """Async SQL generation."""
        if not self.client:
            return "", "Client not available"
        
        try:
            response = await self.client.generate_async(prompt)
            return response.text, ""
        except Exception as e:
            return "", str(e)

# Usage
async def process_multiple_queries(queries):
    adapter = AsyncAdapter()
    tasks = [adapter.generate_sql_async(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Community Checklist

Before submitting your AI engine contribution:

- [ ] **Implementation**
  - [ ] Adapter class follows interface
  - [ ] Error handling implemented
  - [ ] Configuration validation
  - [ ] Initialization feedback (console messages)

- [ ] **Testing**
  - [ ] Unit tests written
  - [ ] Integration tests (optional)
  - [ ] Manual testing completed
  - [ ] Edge cases handled

- [ ] **Documentation**
  - [ ] Setup guide created
  - [ ] Configuration documented
  - [ ] README updated
  - [ ] AI_ENGINES.md updated
  - [ ] Code comments added

- [ ] **Dependencies**
  - [ ] Added to requirements.txt
  - [ ] Version pinned appropriately
  - [ ] No conflicts with existing packages

- [ ] **Configuration**
  - [ ] .env.example updated
  - [ ] Default values sensible
  - [ ] Environment variables documented

- [ ] **Code Quality**
  - [ ] Follows project style guidelines
  - [ ] Type hints added
  - [ ] Docstrings complete
  - [ ] No hardcoded secrets

---

## Getting Help

- **Review existing adapters**: `src/ai_service.py`
- **Check documentation**: `docs/`
- **Ask in discussions**: GitHub Discussions
- **Open an issue**: Use "AI Engine Contribution" template

---

## Examples of Good Contributions

Look at these PRs for inspiration:
- (Future: Link to actual PRs once we have community contributions)

---

## Thank You!

Every new AI engine makes converSQL more flexible and accessible. Your contribution helps the entire community!

**Questions?** Open an issue or discussion on GitHub.

---

**Happy Coding! 🚀**

*Making converSQL support every AI engine, together.*
