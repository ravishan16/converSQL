# Streamlit Cloud Deployment Guide

Simple guide for deploying the NLP to SQL Streamlit application directly from GitHub to Streamlit Cloud.

## Quick Start

### 1. Local Development
```bash
# Clone repository
git clone https://github.com/ravishan16/converSQL.git
cd converSQL

# Install dependencies
pip install -r requirements.txt

# Start application locally
make start
# or
streamlit run app.py
```

### 2. Streamlit Cloud Deployment
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository: `ravishan16/converSQL`
4. Set main file path: `app.py`
5. Configure environment variables (see below)
6. Deploy!

## Application Overview

### Features
- **Professional UI**: Clean, minimal interface for NLP to SQL conversion
- **AI Integration**: Configurable AI provider support
- **Environment-based Config**: Reads settings from environment variables
- **Responsive Design**: Works across different screen sizes

## Environment Configuration

### Required Environment Variables for Streamlit Cloud

In your Streamlit Cloud app settings, configure these environment variables:

#### Core Application Settings
```env
AI_PROVIDER=claude
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

#### AI Provider Configuration
```env
# Claude API (Recommended)
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Alternative: AWS Bedrock (if preferred)
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# AWS_DEFAULT_REGION=us-west-2
```

### Optional Configuration
```env
# Performance
CACHE_TTL=3600
ENABLE_PROMPT_CACHE=true

# Features
DEMO_MODE=false
```

## Streamlit Cloud Deployment Steps

### Step 1: Prepare Your Repository
1. Ensure your repository is public or you have access permissions
2. Make sure `app.py` is in the root directory
3. Verify `requirements.txt` contains all dependencies:
   ```
   streamlit>=1.40.0
   python-dotenv>=1.0.0
   anthropic>=0.40.0
   ```

### Step 2: Deploy to Streamlit Cloud
1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)
2. **Sign in**: Use your GitHub account
3. **New App**: Click "New app"
4. **Select Repository**: Choose `ravishan16/converSQL`
5. **Set Main File**: Enter `app.py`
6. **Branch**: Select `main` (default)
7. **Click Deploy**

### Step 3: Configure Environment Variables
1. **Go to App Settings**: Click the ⚙️ gear icon in your deployed app
2. **Secrets Management**: Add your environment variables
3. **Add Variables**: Copy your `.env` content or add variables individually:
   ```toml
   AI_PROVIDER = "claude"
   CLAUDE_API_KEY = "your_actual_claude_api_key"
   CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
   ```
4. **Save**: Click "Save" to restart the app with new variables

### Step 4: Verify Deployment
- Your app will be available at: `https://your-app-name.streamlit.app`
- Check that the AI Provider shows correctly in the System Status section
- Test the demo query functionality

## Local Development

### Using the Makefile
```bash
# Start the application with logging
make start

# Development mode with auto-reload
make dev

# Clean Python cache files
make clean

# Install dependencies
make install

# See all available commands
make help
```

### Manual Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Start Streamlit app
streamlit run app.py --server.port 8501

# With debug logging
streamlit run app.py --server.port 8501 --logger.level debug
```

## App Management

### Updating Your Deployment
1. **Make changes** to your code locally
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Update app features"
   git push origin main
   ```
3. **Streamlit Cloud** will automatically redeploy your app

### Monitoring
- **App Status**: Check your app dashboard at [share.streamlit.io](https://share.streamlit.io)
- **Logs**: View real-time logs in the Streamlit Cloud interface
- **Performance**: Monitor app metrics in the dashboard

### Restarting the App
- **Automatic**: Happens when you push code changes
- **Manual**: Click "Reboot" in your app dashboard
- **Environment Changes**: Edit secrets/variables and the app will restart

## Troubleshooting

### Common Issues

#### "Import Error" or "Module Not Found"
- Check that all dependencies are listed in `requirements.txt`
- Verify the versions are compatible
- Try clearing the cache in Streamlit Cloud

#### "Environment Variable Not Found"
- Verify variables are set in Streamlit Cloud secrets
- Check variable names match exactly (case-sensitive)
- Ensure no extra spaces in variable names or values

#### "App Not Loading"
- Check the logs in Streamlit Cloud dashboard
- Verify `app.py` is in the root directory
- Ensure the main file path is set correctly

#### AI Provider Issues
```bash
# Test locally first
make start

# Check environment variables
echo $AI_PROVIDER
echo $CLAUDE_API_KEY
```

### Performance Tips
- Use `@st.cache_data` for expensive operations
- Keep your `requirements.txt` minimal
- Monitor app memory usage in the dashboard

## Security Best Practices

### API Keys
- Never commit API keys to your repository
- Use Streamlit Cloud secrets for all sensitive data
- Rotate API keys regularly
- Monitor API usage for anomalies

### Repository Security
- Keep your repository public only if the code doesn't contain secrets
- Use `.gitignore` to exclude sensitive files
- Regular security updates for dependencies

## Next Steps

1. **Custom Domain**: Set up a custom domain for your app
2. **Authentication**: Add user authentication if needed
3. **Analytics**: Monitor usage with Streamlit's built-in analytics
4. **Scaling**: Consider Streamlit Cloud Teams for advanced features

## Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [GitHub Repository](https://github.com/ravishan16/converSQL)