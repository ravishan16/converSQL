
# Environment Configuration Guide

This guide provides clear instructions for configuring environment variables and dependencies for Conversational SQL and its Single Family Loan Analytics implementation.

## Environment Variables

Create a `.env` file in your project root with the following settings:

### Core Application
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
PYTHONPATH=/app
PROCESSED_DATA_DIR=data/processed/
CACHE_TTL=3600
FORCE_DATA_REFRESH=false
```

### AI Provider Configuration

#### AWS Bedrock (Recommended)
```bash
AI_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=4096
```

#### Anthropic Claude API
```bash
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4096
```

### Authentication (Optional)
```bash
ENABLE_AUTH=false
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Cloud Storage (Optional)
```bash
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=single-family-loan
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
```

## Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

## System Requirements

### Minimum
- CPU: 2+ cores
- RAM: 4GB (8GB recommended)
- Storage: 2GB free space
- Python: 3.9 or higher

### Recommended (Production)
- CPU: 4+ cores
- RAM: 16GB
- Storage: 10GB+ SSD
- Network: Stable internet for AI API calls

## Quick Setup

1. Clone the repository and set up your environment:
   ```bash
   git clone <repository-url>
   cd nlptosql
   cp .env.example .env
   pip install -r requirements.txt
   ```
2. Configure your AI provider in `.env`.
3. Launch the application:
   ```bash
   streamlit run app.py
   ```

## Troubleshooting

- Check credentials and environment variables.
- Ensure data files are present in `data/processed/`.
- Review logs for errors.

## Related Documentation

- [Cloud Storage Setup](R2_SETUP.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Cloudflare D1 Setup](D1_SETUP.md)

---

For help, open an issue on GitHub.