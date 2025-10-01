
# Conver---

## 📖 The Story Behind converSQL

### The Problem

Data is everywhere, but accessing it remains a technical barrier. Analysts spend hours writing SQL queries. Business users wait for reports. Data scientists translate questions into complex joins and aggregations. Meanwhile, the insights trapped in your data remain just out of reach for those who need them most.

Traditional BI tools offer pre-built dashboards, but they're rigid. They can't answer the questions you didn't anticipate. And when you need a custom query, you're back to writing SQL or waiting in the queue for engineering support.

### The Open Data Opportunity

What if we could turn this around? What if anyone could ask questions in plain English and get instant, accurate SQL queries tailored to their specific data domain?

That's where converSQL comes in. Built on the principle that **data should be conversational**, converSQL combines:
- **Ontological modeling**: Structured knowledge about your data domains, relationships, and business rules
- **AI-powered generation**: Multiple AI engines (Bedrock, Claude, Gemini, Ollama) that understand context and generate accurate SQL
- **Open data focus**: Showcasing what's possible with publicly available datasets like Fannie Mae's Single Family Loan Performance Data

### Our Mission

We believe data analysis should be:
- **Accessible**: Ask questions in natural language, get answers in seconds
- **Intelligent**: Understand business context, not just column names
- **Extensible**: Easy to adapt to any domain with any data structure
- **Open**: Built on open-source principles, welcoming community contributions

---

## 🏡 Flagship Implementation: Single Family Loan Analytics

To demonstrate converSQL's capabilities, we've built a production-ready application analyzing **9+ million mortgage loan records** from Fannie Mae's public dataset.

### Why This Matters

The Single Family Loan Performance Data represents one of the most comprehensive public datasets on U.S. mortgage markets. It contains granular loan-level data spanning originations, performance, modifications, and defaults. But with 110+ columns and complex domain knowledge required, it's challenging to analyze effectively.

**converSQL makes it conversational:**

🔍 **Natural Language Query:**  
*"Show me high-risk loans in California with credit scores below 620"*

✨ **Generated SQL:**
```sql
SELECT LOAN_ID, STATE, CSCORE_B, OLTV, DTI, DLQ_STATUS, CURRENT_UPB
FROM data
WHERE STATE = 'CA' 
  AND CSCORE_B < 620
  AND CSCORE_B IS NOT NULL
ORDER BY CSCORE_B ASC, OLTV DESC
LIMIT 20
```

📊 **Instant Results** — with context-aware risk metrics and portfolio insights.

# converSQL

> **Transform Natural Language into SQL — Intelligently**

**converSQL** is an open-source framework that bridges the gap between human questions and database queries. Using ontological data modeling and AI-powered query generation, converSQL makes complex data analysis accessible to everyone — from analysts to executives — without requiring SQL expertise.

## 🚀 Why Conversational SQL?

Stop writing complex SQL by hand! With Conversational SQL, you can:
- Ask questions in plain English and get optimized SQL instantly
- Integrate with multiple AI providers (Anthropic Claude, AWS Bedrock, local models)
- Extend to any domain with ontological data modeling
- Build interactive dashboards, query builders, and analytics apps

## 🏆 Flagship Use Case: Single Family Loan Analytics

This repo features a production-grade implementation for mortgage loan portfolio analysis. It’s a showcase of how Conversational SQL can power real-world, domain-specific analytics.

### Key Features

- **🧠 Ontological Intelligence**: 110+ fields organized into 15 business domains (Credit Risk, Geographic, Temporal, Performance, etc.)
- **🎯 Domain-Aware Context**: AI understands mortgage terminology — "high-risk" automatically considers credit scores, LTV ratios, and DTI
- **⚡ High-Performance Pipeline**: Pipe-separated CSVs → Parquet with schema enforcement, achieving 10x compression and instant query performance
- **🔐 Enterprise Security**: Google OAuth integration with Cloudflare D1 query logging
- **🚀 Multiple AI Engines**: Out-of-the-box support for AWS Bedrock, Claude API, and extensible to Gemini, Ollama, and more

---

## 🏗️ Architecture

converSQL follows a clean, layered architecture designed for extensibility:

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  (Streamlit UI • Query Builder • Ontology Explorer)         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      AI Engine Layer                         │
│  (Adapter Pattern: Bedrock • Claude • Gemini • Ollama)      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Intelligence Layer                         │
│  (Ontology • Schema Context • Business Rules)               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      Data Layer                              │
│  (Parquet Files • DuckDB • R2 Storage • Query Execution)    │
└─────────────────────────────────────────────────────────────┘
```

### The Data Engineering Pipeline

Our showcase implementation demonstrates a complete data engineering workflow:

1. **Ingestion**: Fannie Mae's pipe-separated loan performance files
2. **Transformation**: Schema enforcement with explicit data types (VARCHAR, Float, Int16, etc.)
3. **Storage**: Parquet format with SNAPPY compression (10x size reduction)
4. **Performance**: DuckDB for blazing-fast analytical queries
5. **Ontology**: Structured metadata linking business concepts to database schema

📄 **[Learn more about the data pipeline →](docs/DATA_PIPELINE.md)**

---

## �️ Quick Start

### Prerequisites
- Python 3.11+
- Google OAuth credentials
- AI Provider (Claude API or AWS Bedrock)
- Cloudflare R2 or local data storage

### Installation
```bash
git clone <repository-url>
cd converSQL
pip install -r requirements.txt
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Configure your settings
# See setup guides for detailed instructions
```

### Launch
```bash
streamlit run app.py
```


## 📖 Developer Setup Guides

All setup and deployment guides are located in the `docs/` directory:

- **[Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md)** — Authentication configuration
- **[Cloud Storage Setup](docs/R2_SETUP.md)** — Cloudflare R2 data storage configuration
- **[Cloudflare D1 Setup](docs/D1_SETUP.md)** — Logging user activity with Cloudflare D1
- **[Environment Setup](docs/ENVIRONMENT_SETUP.md)** — Environment variables and dependencies
- **[Deployment Guide](docs/DEPLOYMENT.md)** — Deploy to Streamlit Cloud or locally



## � Documentation

### Setup Guides
- **[Environment Setup](docs/ENVIRONMENT_SETUP.md)** — Configure environment variables and dependencies
- **[Data Pipeline Setup](docs/DATA_PIPELINE.md)** — Understand and customize the data pipeline
- **[Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md)** — Enable authentication
- **[Cloud Storage Setup](docs/R2_SETUP.md)** — Configure Cloudflare R2
- **[Deployment Guide](docs/DEPLOYMENT.md)** — Deploy to production

### Developer Guides
- **[Contributing Guide](CONTRIBUTING.md)** — How to contribute to converSQL
- **[AI Engine Development](docs/AI_ENGINES.md)** — Add support for new AI providers
- **[Architecture Overview](docs/ARCHITECTURE.md)** — Deep dive into system design

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're:
- 🐛 Reporting bugs
- 💡 Suggesting features
- 🔧 Adding new AI engine adapters
- 📖 Improving documentation
- 🎨 Enhancing the UI

**Your contributions make converSQL better for everyone.**

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear commit messages
4. **Test thoroughly** — ensure existing functionality still works
5. **Submit a pull request** with a detailed description

📄 **[Read the full contributing guide →](CONTRIBUTING.md)**

### Adding New AI Engines

converSQL uses an adapter pattern for AI engines. Adding a new provider is straightforward:

1. Implement the `AIEngineAdapter` interface
2. Add configuration options
3. Register in the AI service
4. Test and document

📄 **[AI Engine Development Guide →](docs/AI_ENGINES.md)**

---

## 🎯 Use Cases Beyond Loan Analytics

While our flagship implementation focuses on mortgage data, converSQL is designed for **any domain** with tabular data:

### Financial Services
- Credit card transaction analysis
- Investment portfolio performance
- Fraud detection patterns
- Regulatory reporting

### Healthcare
- Patient outcomes analysis
- Clinical trial data exploration
- Hospital performance metrics
- Insurance claims analytics

### E-commerce
- Customer behavior patterns
- Inventory optimization
- Sales performance tracking
- Supply chain analytics

### Your Domain
**Bring your own data** — converSQL adapts through ontological modeling. Define your domains, specify relationships, and let AI handle the query generation.

---

## 🌟 Why converSQL?

### For Analysts
- **Stop writing SQL by hand** — describe what you want, get optimized queries
- **Explore data faster** — try different angles without syntax barriers
- **Focus on insights** — spend time analyzing, not coding

### For Data Engineers
- **Modular architecture** — swap AI providers, storage backends, or UI components
- **Production-ready** — authentication, logging, caching, error handling built-in
- **Extensible ontology** — encode business logic once, reuse everywhere

### For Organizations
- **Democratize data access** — empower non-technical users to explore data
- **Reduce bottlenecks** — less waiting for custom reports and queries
- **Open source** — no vendor lock-in, full transparency, community-driven development

---

## 🛣️ Roadmap

### Current Focus (v1.0)
- ✅ Multi-AI engine support (Bedrock, Claude, Gemini)
- ✅ Bedrock Guardrails integration for content filtering
- ✅ Ontological data modeling
- ✅ Single Family Loan Analytics showcase
- 🔄 Ollama adapter implementation
- 🔄 Enhanced query validation and optimization

### Future Enhancements (v2.0+)
- Multi-table query generation with JOIN intelligence
- Query explanation and visualization
- Historical query learning and optimization
- More domain-specific implementations (healthcare, e-commerce, etc.)
- API server mode for programmatic access
- Web-based ontology editor

**Have ideas?** [Open an issue](https://github.com/ravishan16/conversql/issues) or join the discussion!

---

## 📄 License

**MIT License** — Free to use, modify, and distribute.

See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Fannie Mae** for making Single Family Loan Performance Data publicly available
- **DuckDB** team for an incredible analytical database engine
- **Anthropic** and **AWS** for powerful AI models
- **Streamlit** for making data apps beautiful and easy
- **Open source community** for inspiration and contributions

---

## 📬 Stay Connected

- **⭐ Star this repo** to follow development
- **🐦 Share your use cases** — we'd love to hear how you're using converSQL
- **💬 Join discussions** — ask questions, share ideas, help others
- **🐛 Report issues** — help us improve

---

**Built with ❤️ by the converSQL community**

*Making data conversational, one query at a time.*