
# Cloudflare R2 Setup Guide

This guide provides clear, step-by-step instructions for configuring Cloudflare R2 as the data storage backend for Conversational SQL and its Single Family Loan Analytics implementation.

## Table of Contents
- Prerequisites
- Create R2 Bucket
- Generate R2 API Tokens
- Configure Application
- Upload Data
- Test Connection
- Troubleshooting

## Prerequisites

- Cloudflare account (free tier is sufficient)
- Parquet-format data files ready for upload

## 1. Create an R2 Bucket

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com).
2. In the sidebar, select **R2 Object Storage**.
3. Click **Create bucket**.
4. Enter a bucket name (e.g., `single-family-loan`).
5. Select a location near your deployment region.
6. Click **Create bucket** to finish.

## 2. Generate R2 API Tokens

1. In the Cloudflare Dashboard, go to **R2 Object Storage**.
2. Click **Manage R2 API tokens**.
3. Click **Create API token** and provide a descriptive name (e.g., `single-family-loan-token`).
4. Set permissions:
   - `Object:Read` (required)
   - `Object:List` (required)
   - `Object:Write` (if you plan to upload via API)
5. Restrict resources to your account and the specific bucket.
6. Click **Continue to summary**, review, and then **Create token**.
7. Copy and save your `Access Key ID` and `Secret Access Key` securely.

## 3. Configure the Application

Add the following environment variables to your `.env` file:

```bash
R2_ENDPOINT_URL=https://<your-account-id>.r2.cloudflarestorage.com
R2_BUCKET_NAME=single-family-loan
R2_ACCESS_KEY_ID=<your-access-key>
R2_SECRET_ACCESS_KEY=<your-secret-key>
```

## 4. Upload Data

Upload your Parquet data files to the R2 bucket using the Cloudflare dashboard or API tools. Ensure files are named and organized as expected by the application (see data documentation for details).

## 5. Test Connection

Start the application and verify that it can access and read data from the R2 bucket. Check logs for any errors related to storage or permissions.

## Troubleshooting

- Double-check your API token permissions and resource restrictions.
- Ensure your environment variables match your Cloudflare configuration.
- Review application logs for error messages.

---

For further assistance, consult the official Cloudflare R2 documentation or open an issue in the Conversational SQL repository.
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