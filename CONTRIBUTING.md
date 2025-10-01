# Contributing to converSQL

Thank you for your interest in contributing to converSQL! We're building an open-source framework that makes data conversational, and we welcome contributions from developers, data engineers, analysts, and domain experts.

## 🌟 How You Can Contribute

There are many ways to contribute to converSQL:

- **🐛 Report bugs** — Help us identify and fix issues
- **💡 Suggest features** — Share ideas for new capabilities
- **📝 Improve documentation** — Make converSQL easier to understand and use
- **🔧 Add AI engine adapters** — Extend support to new AI providers
- **🎨 Enhance the UI** — Improve the user experience
- **🧪 Write tests** — Increase code coverage and reliability
- **🏗️ Add domain implementations** — Showcase converSQL in new industries

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/conversql.git
cd conversql

# Add upstream remote
git remote add upstream https://github.com/ravishan16/conversql.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Copy environment template
cp .env.example .env
# Edit .env with your development settings
```

### 3. Create a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create your feature branch
git checkout -b feature/your-feature-name
```

---

## 📋 Contribution Guidelines

### Code Standards

We follow Python best practices to maintain code quality:

**Style Guide:**
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise (ideally <50 lines)
- Use type hints where appropriate

**Formatting:**
```bash
# Format code with Black
black src/ app.py

# Check with flake8
flake8 src/ app.py --max-line-length=100
```

**Example:**
```python
def execute_sql_query(sql_query: str, parquet_files: List[str]) -> pd.DataFrame:
    """
    Execute SQL query using DuckDB on Parquet files.
    
    Args:
        sql_query: SQL query string to execute
        parquet_files: List of absolute paths to Parquet files
        
    Returns:
        DataFrame with query results
        
    Raises:
        Exception: If query execution fails
    """
    try:
        conn = duckdb.connect()
        
        for file_path in parquet_files:
            table_name = os.path.splitext(os.path.basename(file_path))[0]
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{file_path}'")
        
        result_df = conn.execute(sql_query).fetchdf()
        conn.close()
        
        return result_df
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
```

### Testing

All new features and bug fixes should include tests:

**Writing Tests:**
```python
# tests/test_core.py
import pytest
from src.core import execute_sql_query

def test_execute_simple_query(sample_parquet_files):
    """Test execution of a simple SELECT query."""
    sql = "SELECT COUNT(*) as count FROM data"
    result = execute_sql_query(sql, sample_parquet_files)
    
    assert len(result) == 1
    assert 'count' in result.columns
    assert result['count'][0] > 0

def test_execute_invalid_query(sample_parquet_files):
    """Test handling of invalid SQL."""
    sql = "SELECT * FROM nonexistent_table"
    
    with pytest.raises(Exception):
        execute_sql_query(sql, sample_parquet_files)
```

**Running Tests:**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_execute_simple_query
```

### Documentation

Good documentation makes converSQL accessible:

**Code Documentation:**
- Add docstrings to all public functions, classes, and modules
- Use Google-style or NumPy-style docstrings
- Include examples in docstrings where helpful

**Project Documentation:**
- Update relevant `.md` files in `docs/` for new features
- Add usage examples to README.md if applicable
- Create new documentation files for major features

**Example Docstring:**
```python
def generate_sql_with_ai(user_question: str, schema_context: str) -> Tuple[str, str]:
    """
    Generate SQL query from natural language using AI.
    
    This function sends the user's question along with database schema context
    to an AI provider (Bedrock, Claude, etc.) and returns the generated SQL query.
    
    Args:
        user_question: Natural language question from the user
        schema_context: Database schema information including table structures,
                       relationships, and ontological context
    
    Returns:
        Tuple of (sql_query, error_message). If successful, sql_query contains
        the generated SQL and error_message is empty. If failed, sql_query is
        empty and error_message contains the error details.
    
    Example:
        >>> schema = get_table_schemas(parquet_files)
        >>> sql, error = generate_sql_with_ai(
        ...     "Show top 10 states by loan volume",
        ...     schema
        ... )
        >>> print(sql)
        SELECT STATE, COUNT(*) as loan_count FROM data GROUP BY STATE ...
    """
    service = get_ai_service()
    sql_query, error_msg, provider = service.generate_sql(user_question, schema_context)
    return sql_query, error_msg
```

---

## 🔧 Adding New AI Engine Adapters

One of the best ways to contribute is by adding support for new AI providers. See our detailed guide:

📄 **[AI Engine Development Guide](docs/AI_ENGINES.md)**

### Quick Overview

1. **Implement the adapter interface**:
```python
class GeminiAdapter(AIEngineAdapter):
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini client."""
        # Setup code here
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.client is not None
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """Generate SQL using Gemini."""
        # Implementation here
```

2. **Register in AI service**:
```python
# src/ai_service.py
class AIService:
    def __init__(self):
        self.bedrock = BedrockClient()
        self.claude = ClaudeClient()
        self.gemini = GeminiAdapter()  # Add new adapter
        self._determine_active_provider()
```

3. **Add configuration**:
```python
# .env
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-pro
```

4. **Test thoroughly**:
```python
def test_gemini_adapter():
    adapter = GeminiAdapter()
    assert adapter.is_available()
    
    sql, error = adapter.generate_sql("SELECT * FROM data LIMIT 10")
    assert sql
    assert not error
```

---

## 🎯 Development Workflow

### Making Changes

1. **Write code** following our style guidelines
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Run tests** to ensure everything works
5. **Format code** with Black
6. **Commit changes** with clear messages

### Commit Messages

Write clear, descriptive commit messages:

**Good:**
```
Add Gemini AI adapter support

- Implement GeminiAdapter class with API integration
- Add configuration for Gemini API key and model
- Include error handling and fallback logic
- Add unit tests for Gemini adapter
- Update documentation with Gemini setup instructions
```

**Bad:**
```
fixed stuff
updated files
changes
```

**Format:**
```
<type>: <short summary>

<detailed description>

<references to issues if applicable>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pull Request Process

1. **Ensure all tests pass**:
```bash
pytest
```

2. **Update documentation** if you've added features

3. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

4. **Create Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference any related issues (`Fixes #123`)
   - Describe what changed and why
   - Include screenshots for UI changes
   - List any breaking changes

5. **Address review feedback**:
   - Respond to comments
   - Make requested changes
   - Push updates to your branch

### Pull Request Template

When creating a PR, use this template:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes:
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] All existing tests pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added that prove fix/feature works
- [ ] Dependent changes merged

## Related Issues
Fixes #(issue number)

## Screenshots (if applicable)
Add screenshots for UI changes.
```

---

## 🐛 Reporting Bugs

### Before Reporting

1. **Check existing issues** — Your bug may already be reported
2. **Try the latest version** — The bug might be fixed
3. **Gather information** — Logs, error messages, steps to reproduce

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Enter '....'
4. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., macOS 13.0]
- Python version: [e.g., 3.11.5]
- converSQL version: [e.g., 1.0.0]
- AI Provider: [e.g., Claude API]

**Additional context**
Any other relevant information.

**Logs**
```
Paste relevant log output here
```
```

---

## 💡 Suggesting Features

We love new ideas! When suggesting features:

1. **Check existing issues** — Your idea might already be proposed
2. **Describe the use case** — Help us understand the problem you're solving
3. **Propose a solution** — Share your thoughts on implementation
4. **Consider alternatives** — What other approaches might work?

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Use cases**
How would this feature be used? Who benefits?

**Additional context**
Add any other context or screenshots.
```

---

## 📚 Documentation Contributions

Documentation is crucial for adoption. Ways to contribute:

- **Fix typos and unclear explanations**
- **Add examples and tutorials**
- **Improve setup guides**
- **Create video walkthroughs**
- **Translate documentation** (future)

---

## 🏗️ Domain-Specific Implementations

Help showcase converSQL in new domains:

1. **Choose a domain** (healthcare, e-commerce, finance, etc.)
2. **Find an open dataset** or create a sample dataset
3. **Define ontology** for that domain
4. **Create data pipeline** to transform data
5. **Build example queries** demonstrating value
6. **Document the implementation**

Example domains we'd love to see:
- Healthcare: Patient outcomes, clinical trials
- E-commerce: Customer behavior, inventory
- Finance: Transaction analytics, fraud detection
- Education: Student performance, enrollment
- Transportation: Fleet management, routing
- Energy: Usage patterns, optimization

---

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be respectful** — Treat everyone with respect
- **Be collaborative** — Work together toward common goals
- **Be patient** — Help others learn and grow
- **Be constructive** — Provide helpful feedback
- **Be inclusive** — Welcome diverse perspectives

### Getting Help

If you need help:

- **Check documentation** in the `docs/` folder
- **Search issues** for similar questions
- **Ask in discussions** on GitHub
- **Be specific** about your problem and what you've tried

---

## 📬 Communication

- **GitHub Issues** — Bug reports and feature requests
- **GitHub Discussions** — Questions, ideas, and general discussion
- **Pull Requests** — Code contributions
- **Email** — For security issues or private matters

---

## 🎉 Recognition

Contributors are recognized in several ways:

- Listed in README.md contributors section
- Mentioned in release notes for significant contributions
- Invited to join core contributor team (for consistent contributors)

---

## 📄 License

By contributing to converSQL, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Thank You!

Every contribution, no matter how small, makes converSQL better. Whether you're fixing a typo, adding a feature, or helping others in discussions — **thank you** for being part of the converSQL community!

**Questions?** Open an issue or start a discussion. We're here to help!

---

**Happy Contributing! 🚀**

*Making data conversational, together.*
