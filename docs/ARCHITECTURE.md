# converSQL Architecture

## Overview

converSQL follows a **clean, layered architecture** designed for modularity, extensibility, and maintainability. This document provides a deep dive into the system design, component interactions, and architectural decisions.

---

## Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                         │
│  • Streamlit UI                                              │
│  • Interactive Components                                    │
│  • Visualization                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Application Layer                          │
│  • Query Builder Logic                                       │
│  • User Session Management                                   │
│  • Authentication                                            │
│  • Caching                                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   AI Engine Layer                            │
│  • Adapter Pattern                                           │
│  • Multiple AI Providers (Bedrock, Claude, Gemini, Ollama)  │
│  • Prompt Engineering                                        │
│  • Response Parsing                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Intelligence Layer                         │
│  • Ontological Data Dictionary                               │
│  • Schema Context Generation                                 │
│  • Business Rules Engine                                     │
│  • Semantic Relationships                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Data Access Layer                          │
│  • DuckDB Query Engine                                       │
│  • Parquet File Management                                   │
│  • SQL Execution                                             │
│  • Result Formatting                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Storage Layer                              │
│  • Parquet Files (local or R2)                              │
│  • Cloudflare D1 (logging)                                  │
│  • Session State                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Application Entry Point (`app.py`)

**Responsibility**: Main Streamlit application and UI orchestration

**Key Functions**:
- Initialize session state and caching
- Render UI components (tabs, forms, visualizations)
- Handle user interactions
- Coordinate between authentication, AI service, and data layers

**Design Patterns**:
- **Singleton Pattern**: AI service and authentication service cached as singletons
- **Facade Pattern**: Wraps complex subsystems with simple interfaces
- **Observer Pattern**: Streamlit's reactive model for state changes

**Code Structure**:
```python
# Initialization
initialize_app_data()  # Load data, AI, schema

# Authentication wrapper
simple_auth_wrapper(main)()  # Protects main app

# Main UI
def main():
    # Tabs: Query Builder, Ontology Explorer, Advanced
    tab1, tab2, tab3 = st.tabs([...])
    
    with tab1:  # Query Builder
        # Natural language input
        # AI SQL generation
        # Query execution
        # Results display
```

### 2. Core Module (`src/core.py`)

**Responsibility**: Business logic and data operations

**Key Functions**:
```python
def scan_parquet_files() -> List[str]
    """Discover available Parquet files."""

def get_table_schemas(parquet_files: List[str]) -> str
    """Generate schema context with ontology."""

def execute_sql_query(sql_query: str, parquet_files: List[str]) -> pd.DataFrame
    """Execute SQL using DuckDB."""

def get_analyst_questions() -> Dict[str, str]
    """Provide pre-built analytical questions."""
```

**Caching Strategy**:
- `@st.cache_data(ttl=3600)` for expensive operations
- File scans cached to reduce I/O
- Schema generation cached to reduce processing

**Design Decisions**:
- **Separation of Concerns**: Data operations separate from UI
- **Dependency Injection**: Pass parquet_files explicitly
- **Fail-Safe Defaults**: Graceful degradation if data unavailable

### 3. AI Service Module (`src/ai_service.py`)

**Responsibility**: AI provider management and SQL generation

**Architecture**:
```
AIService (Orchestrator)
├── BedrockClient (AWS Bedrock)
├── ClaudeClient (Anthropic API)
├── GeminiAdapter (Google Gemini) [Future]
└── OllamaAdapter (Local/Self-hosted) [Future]
```

**Key Classes**:

```python
class AIService:
    def __init__(self):
        self.bedrock = BedrockClient()
        self.claude = ClaudeClient()
        self._determine_active_provider()
    
    def generate_sql(self, question: str, schema: str) -> Tuple[str, str, str]:
        """Route to active provider, return (sql, error, provider)."""
```

**Provider Selection Logic**:
1. Check `AI_PROVIDER` environment variable
2. Verify provider is available (API key, connectivity)
3. Fallback to next available provider
4. Return error if none available

**Prompt Engineering**:
- Context-rich prompts with ontology
- Domain-specific instructions (mortgage analytics)
- Business rule integration
- Output format specification

**Caching**:
- `@st.cache_data` with prompt hashing
- Configurable TTL (default 1 hour)
- Cache invalidation on schema changes

### 4. Data Dictionary Module (`src/data_dictionary.py`)

**Responsibility**: Ontological data modeling

**Structure**:
```python
LOAN_ONTOLOGY = {
    "DOMAIN_NAME": {
        "domain_description": "...",
        "primary_key": "...",
        "fields": {
            "FIELD_NAME": FieldMetadata(
                description="...",
                domain="...",
                data_type="...",
                business_context="...",
                risk_impact="...",
                values={...},
                relationships=[...]
            )
        }
    }
}
```

**Key Functions**:
```python
def generate_enhanced_schema_context(parquet_files: List[str]) -> str
    """Generate schema with ontological enrichment."""

def get_field_metadata(field_name: str) -> FieldMetadata
    """Retrieve metadata for a specific field."""
```

**Design Benefits**:
- **Semantic Understanding**: AI understands business context
- **Relationship Mapping**: Cross-field dependencies documented
- **Business Rules**: Encoded once, used everywhere
- **Extensibility**: Easy to add new domains

### 5. Authentication Module (`src/simple_auth.py`)

**Responsibility**: User authentication and logging

**Components**:
```python
class AuthService:
    def is_enabled(self) -> bool
        """Check if auth is configured."""
    
    def is_authenticated(self) -> bool
        """Check user authentication status."""
    
    def handle_oauth_callback(self)
        """Process Google OAuth callback."""
    
    def log_query(self, question, sql, provider, time)
        """Log query to Cloudflare D1."""
```

**Flow**:
1. User accesses app
2. Check authentication status
3. If not authenticated → OAuth redirect
4. Handle OAuth callback
5. Store user session
6. Log queries to D1

**Security**:
- Google OAuth 2.0
- Session state in Streamlit
- No local password storage
- HTTPS required in production

---

## Data Flow

### Query Generation Flow

```
User Question
    │
    ▼
┌─────────────────────┐
│ Streamlit UI        │
│ (app.py)            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Core Module         │
│ (src/core.py)       │
│ - Load schema       │
│ - Get ontology      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AI Service          │
│ (src/ai_service.py) │
│ - Build prompt      │
│ - Call AI provider  │
│ - Parse response    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ DuckDB Engine       │
│ (src/core.py)       │
│ - Execute SQL       │
│ - Return results    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Streamlit UI        │
│ - Format results    │
│ - Display table     │
│ - Show metrics      │
└─────────────────────┘
```

### Data Pipeline Flow

```
Raw Data (Fannie Mae)
    │
    ▼
┌─────────────────────┐
│ Ingestion           │
│ (scripts/sync_data) │
│ - Download from R2  │
│ - Validate format   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Transformation      │
│ (notebooks/)        │
│ - Parse CSV/pipe    │
│ - Apply schema      │
│ - Cast types        │
│ - Validate data     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Parquet Storage     │
│ (data/processed/)   │
│ - Write Parquet     │
│ - SNAPPY compress   │
│ - Add metadata      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Query Engine        │
│ (DuckDB)            │
│ - Load Parquet      │
│ - Execute queries   │
│ - Return results    │
└─────────────────────┘
```

---

## Design Patterns

### 1. Adapter Pattern (AI Engines)

**Problem**: Multiple AI providers with different APIs

**Solution**: Unified interface with provider-specific adapters

```python
class AIEngineAdapter:
    def is_available(self) -> bool: ...
    def generate_sql(self, prompt: str) -> Tuple[str, str]: ...

class BedrockClient(AIEngineAdapter): ...
class ClaudeClient(AIEngineAdapter): ...
class GeminiAdapter(AIEngineAdapter): ...
```

**Benefits**:
- Add new providers without changing core logic
- Easy to test with mock adapters
- Clear separation of concerns

### 2. Facade Pattern (Core Module)

**Problem**: Complex subsystems (file I/O, DuckDB, caching)

**Solution**: Simple unified interface

```python
# Complex operations hidden behind simple functions
def execute_sql_query(sql: str, files: List[str]) -> pd.DataFrame:
    # Handles: connection, table registration, execution, cleanup
```

**Benefits**:
- Simple API for UI layer
- Easy to refactor internals
- Reduced coupling

### 3. Strategy Pattern (Ontology)

**Problem**: Different domains need different business rules

**Solution**: Ontology-driven strategy selection

```python
# AI service selects strategies based on ontology
if domain == "CREDIT_RISK":
    # Apply credit risk rules
elif domain == "GEOGRAPHIC":
    # Apply geographic rules
```

**Benefits**:
- Domain-specific intelligence
- Easy to extend to new domains
- Centralized business logic

### 4. Singleton Pattern (Services)

**Problem**: Expensive initialization (AI clients, auth)

**Solution**: Cached singleton instances

```python
@st.cache_resource
def get_ai_service() -> AIService:
    return AIService()  # Created once, reused
```

**Benefits**:
- Avoid repeated API connections
- Faster subsequent requests
- Lower resource usage

---

## Configuration Management

### Environment Variables

```bash
# Core Configuration
PROCESSED_DATA_DIR=data/processed/
DEMO_MODE=false

# AI Provider Selection
AI_PROVIDER=claude  # bedrock, claude, gemini, ollama

# Claude API
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# AWS Bedrock
AWS_DEFAULT_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-haiku-20241022-v1:0

# Authentication
ENABLE_AUTH=true
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Cloudflare
R2_ACCOUNT_ID=...
R2_BUCKET_NAME=...
D1_DATABASE_ID=...

# Performance
CACHE_TTL=3600
ENABLE_PROMPT_CACHE=true
```

### Configuration Priority

1. Environment variables (`.env`)
2. Default values in code
3. Fallback to safe defaults

---

## Performance Optimizations

### 1. Caching Strategy

**Data Caching**:
```python
@st.cache_data(ttl=3600)
def scan_parquet_files(): ...

@st.cache_data(ttl=3600)
def get_table_schemas(): ...
```

**Resource Caching**:
```python
@st.cache_resource
def load_ai_client(): ...

@st.cache_resource
def get_auth_service(): ...
```

### 2. Lazy Loading

- Parquet files loaded only when queried
- Schema generated on first request
- AI client initialized on first use

### 3. DuckDB Optimizations

- **Columnar reads**: Only requested columns loaded
- **Predicate pushdown**: Filters applied at file level
- **Statistics**: Parquet metadata for query planning
- **Zero-copy**: Direct Parquet file access

### 4. UI Optimizations

- **Component keys**: Prevent unnecessary re-renders
- **Session state**: Preserve expensive computations
- **Incremental updates**: Only re-render changed components

---

## Security Considerations

### 1. Authentication

- Google OAuth 2.0 (industry standard)
- No password storage
- Session-based authentication
- HTTPS required

### 2. Data Access

- No user-uploaded SQL (prevents injection)
- AI-generated queries only
- Parameterized queries where applicable
- Read-only database access

### 3. API Keys

- Environment variables only
- Never committed to git
- Rotated regularly
- Separate keys per environment

### 4. Logging

- Query logging to D1
- No sensitive data in logs
- User actions tracked for audit

---

## Scalability

### Current Capacity

- **Data**: 10M+ rows performant
- **Users**: Single-instance, supports 10-50 concurrent
- **Queries**: Sub-second response for most queries

### Scaling Strategies

**Vertical Scaling** (current):
- More memory for larger datasets
- Faster CPU for query execution
- SSD for faster I/O

**Horizontal Scaling** (future):
- Multiple Streamlit instances behind load balancer
- Shared R2 storage
- Distributed query engine (Spark)

**Data Scaling**:
- Partition Parquet files by time/geography
- Incremental updates instead of full reloads
- Archive old data to cold storage

---

## Testing Strategy

### Unit Tests
```python
# Test individual functions
def test_execute_sql_query():
    result = execute_sql_query("SELECT COUNT(*) FROM data", files)
    assert len(result) > 0
```

### Integration Tests
```python
# Test component interactions
def test_ai_to_database_flow():
    sql, error = generate_sql_with_ai(question, schema)
    result = execute_sql_query(sql, files)
    assert not result.empty
```

### End-to-End Tests
```python
# Test complete user flows
def test_query_generation_flow():
    # User enters question
    # AI generates SQL
    # Query executes
    # Results displayed
```

---

## Deployment Architecture

### Local Development
```
Developer Machine
├── Python 3.11+
├── Streamlit
├── DuckDB
├── Parquet files (local)
└── Environment variables (.env)
```

### Production (Streamlit Cloud)
```
Streamlit Cloud
├── App container
├── Environment secrets
├── Cloudflare R2 (data storage)
├── Cloudflare D1 (logging)
└── Google OAuth (authentication)
```

### Production (Self-Hosted)
```
Server/Container
├── Docker container
├── Reverse proxy (nginx)
├── HTTPS certificate
├── Environment variables
└── Volume mounts (data)
```

---

## Error Handling

### Graceful Degradation

1. **AI unavailable** → Show manual SQL option
2. **Data missing** → Show helpful setup instructions
3. **Auth unavailable** → Demo mode (if enabled)
4. **Query errors** → Show error, suggest corrections

### Error Boundaries

```python
try:
    result = execute_sql_query(sql, files)
except Exception as e:
    logger.error(f"Query failed: {e}")
    st.error("Query execution failed. Please check SQL syntax.")
    return pd.DataFrame()  # Empty result
```

---

## Monitoring & Observability

### Logging

- Application logs (stdout)
- Query logs (D1 database)
- Error logs (stderr)
- Performance metrics (execution times)

### Metrics

- Query success/failure rates
- Response times (AI, database)
- User activity patterns
- Resource utilization

---

## Future Enhancements

### Planned Improvements

1. **Multi-table queries** - JOIN support with relationship intelligence
2. **Query explanation** - Visualize query plan and logic
3. **Historical learning** - Learn from past queries
4. **API mode** - Programmatic access without UI
5. **Real-time collaboration** - Multiple users sharing queries
6. **Advanced visualizations** - Interactive charts and dashboards

---

## Related Documentation

- **[Data Pipeline](DATA_PIPELINE.md)** - Data transformation architecture
- **[AI Engines](AI_ENGINES.md)** - AI adapter implementation
- **[Contributing](../CONTRIBUTING.md)** - Development guidelines

---

## Questions?

For architecture questions or suggestions:
- Open an issue with the "architecture" label
- Start a discussion on GitHub
- Review existing PRs for implementation patterns

---

**Built with careful consideration for modularity, extensibility, and maintainability.**

*Understanding the architecture helps you contribute effectively!*
