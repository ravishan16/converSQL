# Cloudflare R2 Setup Guide

This guide will walk you through setting up Cloudflare R2 for data storage and generating the necessary API keys for the Single Family Loan application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Create R2 Bucket](#step-1-create-r2-bucket)
- [Step 2: Generate R2 API Tokens](#step-2-generate-r2-api-tokens)
- [Step 3: Configure Application](#step-3-configure-application)
- [Step 4: Upload Data](#step-4-upload-data)
- [Step 5: Test Connection](#step-5-test-connection)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Cloudflare account (free tier available)
- Data files in Parquet format ready for upload

## Step 1: Create R2 Bucket

1. **Log into Cloudflare Dashboard**
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
   - Sign in with your account credentials

2. **Navigate to R2 Object Storage**
   - In the sidebar, click **"R2 Object Storage"**
   - Click **"Create bucket"**

3. **Configure Bucket**
   - **Bucket name**: `single-family-loan` (or your preferred name)
   - **Location**: Choose closest to your deployment region
   - Click **"Create bucket"**

## Step 2: Generate R2 API Tokens

### Option A: R2 API Tokens (Recommended)

1. **Navigate to API Tokens**
   - In Cloudflare Dashboard, go to **"R2 Object Storage"**
   - Click **"Manage R2 API tokens"**

2. **Create New Token**
   - Click **"Create API token"**
   - Give it a descriptive name: `single-family-loan-token`

3. **Set Permissions**
   - **Permissions**: Select the following:
     - ✅ `Object:Read` on your bucket
     - ✅ `Object:List` on your bucket
     - ✅ `Object:Write` (if you need to upload via API)

4. **Set Resource Restrictions**
   - **Include**: `All accounts` → Your account
   - **Include**: `All zones` → Specific bucket → `single-family-loan`

5. **Generate Token**
   - Click **"Continue to summary"**
   - Review permissions and click **"Create token"**
   - **Important**: Copy and save the following credentials immediately:
     - `Access Key ID`
     - `Secret Access Key`
     - `Endpoint URL` (will be in format: `https://[account-id].r2.cloudflarestorage.com`)

### Option B: Global API Key (Less Secure)

1. **Navigate to API Tokens**
   - Go to **"My Profile"** → **"API Tokens"**
   - Find **"Global API Key"** and click **"View"**

2. **Get Account Details**
   - You'll also need your **Account ID**
   - Find this in the right sidebar of any Cloudflare dashboard page

## Step 3: Configure Application

1. **Update Environment File**
   ```bash
   # Copy the example file
   cp .env.example .env
   ```

2. **Edit .env File**
   ```env
   # Cloudflare R2 Configuration
   R2_ENDPOINT_URL=https://[your-account-id].r2.cloudflarestorage.com
   R2_BUCKET_NAME=single-family-loan
   R2_ACCESS_KEY_ID=your_access_key_id_here
   R2_SECRET_ACCESS_KEY=your_secret_access_key_here
   R2_ACCOUNT_ID=your_cloudflare_account_id
   ```

3. **Set Data Sync Options**
   ```env
   # Force refresh data on every startup (set to false in production)
   FORCE_DATA_REFRESH=false
   
   # Cache TTL for data operations
   CACHE_TTL=3600
   ```

## Step 4: Upload Data

### Option A: Using Cloudflare Dashboard

1. **Navigate to Your Bucket**
   - Go to **"R2 Object Storage"** → Your bucket name
   - Click **"Upload"**

2. **Upload Parquet Files**
   - Drag and drop your `.parquet` files
   - Or click **"Select from computer"**
   - Ensure files are uploaded to the root of the bucket

### Option B: Using AWS CLI (S3 Compatible)

1. **Configure AWS CLI for R2**
   ```bash
   aws configure set aws_access_key_id YOUR_R2_ACCESS_KEY_ID
   aws configure set aws_secret_access_key YOUR_R2_SECRET_ACCESS_KEY
   aws configure set region auto
   ```

2. **Upload Files**
   ```bash
   aws s3 cp data/processed/data.parquet s3://single-family-loan/ \
     --endpoint-url https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
   ```

### Option C: Using Python Script

```python
import boto3

# Configure R2 client
client = boto3.client(
    's3',
    endpoint_url='https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com',
    aws_access_key_id='YOUR_ACCESS_KEY_ID',
    aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
    region_name='auto'
)

# Upload file
client.upload_file('data/processed/data.parquet', 'single-family-loan', 'data.parquet')
```

## Step 5: Test Connection

1. **Run Data Sync Script**
   ```bash
   python scripts/sync_data.py
   ```

2. **Expected Output**
   ```
   🌤️  Cloudflare R2 Data Sync
   ==========================================
   ✅ Connected to R2 bucket: single-family-loan
   📊 Found 1 parquet files in R2
   📥 Downloading data.parquet to data/processed/data.parquet
   ✅ Successfully downloaded data.parquet
   🎉 Data sync completed successfully! Application ready to start.
   ```

3. **Start Application**
   ```bash
   streamlit run app.py
   ```

## Troubleshooting

### Common Issues

#### "Failed to connect to R2"
- **Check credentials**: Verify `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`
- **Check endpoint URL**: Ensure format is `https://[account-id].r2.cloudflarestorage.com`
- **Verify bucket name**: Must match exactly (case-sensitive)

#### "No objects found in R2 bucket"
- **Check file upload**: Ensure `.parquet` files are uploaded to bucket root
- **Verify bucket name**: Double-check bucket name in configuration
- **Check file permissions**: Ensure API token has `Object:List` permission

#### "Download failed or file is empty"
- **Check API permissions**: Ensure token has `Object:Read` permission
- **Verify file integrity**: Check if files uploaded correctly
- **Check network connectivity**: Ensure server can reach Cloudflare

#### "R2 credentials not found"
- **Environment variables**: Ensure `.env` file is in project root
- **Variable names**: Check exact spelling of environment variable names
- **File loading**: Verify `python-dotenv` is installed and working

### Testing R2 Connection

```python
# Test script to verify R2 connection
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    region_name='auto'
)

try:
    # Test bucket access
    response = client.list_objects_v2(Bucket=os.getenv('R2_BUCKET_NAME'))
    print(f"✅ Connection successful!")
    print(f"📊 Found {len(response.get('Contents', []))} objects")
    
    for obj in response.get('Contents', []):
        print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Security Best Practices

1. **Use R2 API Tokens** instead of Global API Key
2. **Restrict permissions** to only what's needed
3. **Rotate keys regularly** for production deployments
4. **Use environment variables** never commit keys to version control
5. **Consider IP restrictions** for production API tokens

## Cost Optimization

1. **Monitor usage** in Cloudflare Dashboard
2. **Set up billing alerts** for unexpected usage
3. **Use appropriate storage class** for your access patterns
4. **Enable caching** in application (`CACHE_TTL=3600`)
5. **Minimize data refresh** (`FORCE_DATA_REFRESH=false`)

## Next Steps

- [Docker Deployment Guide](DOCKER_SETUP.md)
- [Authentication Setup](AUTH_SETUP.md)
- [Production Deployment](DEPLOYMENT.md)

---

For additional support, refer to:
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [R2 API Reference](https://developers.cloudflare.com/r2/api/)
- [Project Issues](https://github.com/your-repo/issues)