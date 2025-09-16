# Environment Configuration Guide

Complete guide to configuring your Single Family Loan Analytics Platform environment variables and dependencies.

## 🔧 Environment Variables

Create a `.env` file in your project root with the following configurations:

### **Core Application**
```bash
# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
PYTHONPATH=/app

# Data Configuration
PROCESSED_DATA_DIR=data/processed/
CACHE_TTL=3600
FORCE_DATA_REFRESH=false
```

### **AI Provider Configuration**

#### Option 1: AWS Bedrock (Recommended)
```bash
# AWS Bedrock Configuration
AI_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=4096
```

#### Option 2: Anthropic Claude API
```bash
# Anthropic Claude Configuration
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4096
```

### **Authentication (Optional)**
```bash
# Supabase Authentication
ENABLE_AUTH=false
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### **Cloud Storage (Optional)**
```bash
# Cloudflare R2 Storage
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=single-family-loan
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
```

## 📦 Dependencies

### **Core Requirements**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually:
pip install streamlit pandas duckdb boto3 python-dotenv
pip install anthropic  # for Claude API
pip install boto3      # for AWS Bedrock
pip install supabase   # for authentication
```

### **Development Dependencies**
```bash
# Development tools
pip install pytest black flake8 mypy
pip install streamlit-autorefresh  # for development
```

## 🛠️ System Requirements

### **Minimum System Specs**
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for data files
- **Python**: 3.9 or higher

### **Recommended Production Specs**
- **CPU**: 4+ cores
- **RAM**: 16GB
- **Storage**: 10GB+ SSD
- **Network**: Stable internet for AI API calls

## 🚀 Quick Environment Setup

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd nlptosql
cp .env.example .env
```

### **2. Configure AI Provider**
Choose one AI provider and configure accordingly:

**For AWS Bedrock:**
```bash
# Add to .env
AI_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

**For Claude API:**
```bash
# Add to .env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_api_key
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Test Configuration**
```bash
# Test AI connectivity
python -c "from src.core import initialize_ai_client; print('✅ AI client initialized' if initialize_ai_client() else '❌ AI setup failed')"

# Test data access
python -c "from src.core import scan_parquet_files; files = scan_parquet_files(); print(f'✅ Found {len(files)} data files' if files else '⚠️ No data files found')"
```

### **5. Launch Application**
```bash
streamlit run app.py
```

## ⚙️ Configuration Options

### **AI Model Selection**

**AWS Bedrock Models:**
- `anthropic.claude-3-sonnet-20240229-v1:0` (Recommended)
- `anthropic.claude-3-haiku-20240307-v1:0` (Faster)
- `anthropic.claude-instant-v1` (Legacy)

**Claude API Models:**
- `claude-3-sonnet-20240229` (Recommended)
- `claude-3-haiku-20240307` (Faster)
- `claude-2.1` (Legacy)

### **Performance Tuning**

**For Large Datasets:**
```bash
CACHE_TTL=7200  # Increase cache duration
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1000  # MB
```

**For Development:**
```bash
STREAMLIT_SERVER_HEADLESS=false
STREAMLIT_SERVER_RUN_ON_SAVE=true
CACHE_TTL=300  # Shorter cache for development
```

## 🔍 Troubleshooting

### **Common Issues**

**AI Provider Connection Failed:**
```bash
# Check credentials
echo $ANTHROPIC_API_KEY  # Should not be empty
aws sts get-caller-identity  # Should return AWS account info
```

**Data Files Not Found:**
```bash
# Check data directory
ls -la data/processed/
# Should contain .parquet files
```

**Import Errors:**
```bash
# Check Python path
echo $PYTHONPATH
# Should include project root
```

**Memory Issues:**
```bash
# Monitor memory usage
htop
# Consider reducing CACHE_TTL or dataset size
```

### **Environment Validation Script**
```bash
# Create validate_env.py
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = ['AI_PROVIDER']
optional_vars = ['ANTHROPIC_API_KEY', 'AWS_ACCESS_KEY_ID', 'SUPABASE_URL']

print('🔍 Environment Validation:')
for var in required_vars:
    value = os.getenv(var)
    print(f'✅ {var}: {\"Set\" if value else \"❌ Missing\"}')

for var in optional_vars:
    value = os.getenv(var)
    if value:
        print(f'✅ {var}: Set')
"
```

## 📚 Related Documentation

- **[🔐 Authentication Setup](SUPABASE_SETUP.md)** - Configure user authentication
- **[☁️ Cloud Storage Setup](R2_SETUP.md)** - Set up data storage
- **[🚀 Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[⚡ Quick Start Guide](AUTH_QUICK_START.md)** - Get running quickly

---

**Need Help?** Check our troubleshooting guide or open an issue on GitHub.