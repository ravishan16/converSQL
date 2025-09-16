# Single Family Loan Analytics Platform - Replit Setup

## Overview
This is a Streamlit-based Single Family Loan Analytics Platform that enables mortgage analysts to query loan portfolio data using natural language through AI-powered SQL generation. The platform features an ontological data model with 110+ data fields across 15 business domains.

## Recent Changes
- **2025-09-16**: Successfully imported GitHub repository and configured for Replit environment
- **2025-09-16**: Updated Streamlit configuration for port 5000 and host 0.0.0.0
- **2025-09-16**: Set up deployment configuration for autoscale production deployment

## Project Architecture
- **Frontend**: Streamlit web application with professional UI
- **Backend**: DuckDB for high-performance analytics on parquet data files
- **AI Integration**: Support for AWS Bedrock and Anthropic Claude API
- **Authentication**: Optional Supabase-based user management
- **Storage**: Local parquet files with optional Cloudflare R2 sync

## Current Configuration
- **Port**: 5000 (configured for Replit environment)
- **Host**: 0.0.0.0 (accepts all connections)
- **Deployment**: Autoscale (stateless web app)
- **Dependencies**: All Python packages installed via requirements.txt

## Data Files
- Contains 9+ million loan records in parquet format
- Data directory: `data/processed/`
- Main data file: `data.parquet` (validated and working)

## Environment Setup Required
To fully utilize the platform, users need to configure:
1. **AI Provider**: Either AWS Bedrock or Anthropic Claude API credentials
2. **Authentication** (Optional): Supabase configuration
3. **Cloud Storage** (Optional): Cloudflare R2 for data sync

## Key Features Working
✅ Streamlit app runs successfully on port 5000
✅ Data files are loaded and accessible
✅ UI renders correctly with professional styling
✅ Deployment configuration is set for production
✅ All dependencies are installed

## Known Minor Issues
- Some Streamlit deprecation warnings (use_container_width parameter)
- Empty label accessibility warnings (non-critical)
- General email config option deprecation notice

## Next Steps for Full Functionality
1. Configure AI provider credentials (AWS Bedrock or Claude API)
2. Set up authentication if needed (Supabase)
3. Configure environment variables as needed
4. Test AI-powered SQL generation features