#!/usr/bin/env python3
"""
Cloudflare R2 Data Sync Script
Downloads and syncs data from R2 bucket to local storage.
Runs at container startup to ensure data availability.
"""

import boto3
import os
import sys
import argparse
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Configuration from environment
R2_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', 'https://50ee71713e4e8762d5eab0e8ec442f1e.r2.cloudflarestorage.com')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'single-family-loan')
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
LOCAL_DATA_DIR = os.getenv('PROCESSED_DATA_DIR', 'data/processed/')
FORCE_REFRESH = os.getenv('FORCE_DATA_REFRESH', 'false').lower() == 'true'


def get_file_md5(file_path):
    """Calculate MD5 hash of a file."""
    if not os.path.exists(file_path):
        return None
    
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_r2_client():
    """Create and return R2 client."""
    if not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
        print("❌ R2 credentials not found. Please set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY")
        return None
    
    try:
        client = boto3.client(
            's3',
            endpoint_url=R2_ENDPOINT_URL,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name='auto'  # Cloudflare R2 uses 'auto'
        )
        
        # Test connection
        client.head_bucket(Bucket=R2_BUCKET_NAME)
        print(f"✅ Connected to R2 bucket: {R2_BUCKET_NAME}")
        return client
        
    except (ClientError, NoCredentialsError) as e:
        print(f"❌ Failed to connect to R2: {e}")
        return None


def list_r2_objects(client):
    """List all objects in the R2 bucket."""
    try:
        response = client.list_objects_v2(Bucket=R2_BUCKET_NAME)
        
        if 'Contents' not in response:
            print("⚠️  No objects found in R2 bucket")
            return []
        
        objects = []
        for obj in response['Contents']:
            # Focus on parquet files
            if obj['Key'].endswith('.parquet'):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
        
        print(f"📊 Found {len(objects)} parquet files in R2")
        return objects
        
    except ClientError as e:
        print(f"❌ Error listing R2 objects: {e}")
        return []


def download_file(client, r2_key, local_path):
    """Download a single file from R2."""
    try:
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        print(f"📥 Downloading {r2_key} to {local_path}")
        client.download_file(R2_BUCKET_NAME, r2_key, local_path)
        
        # Verify download
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            print(f"✅ Successfully downloaded {r2_key}")
            return True
        else:
            print(f"❌ Download failed or file is empty: {r2_key}")
            return False
            
    except ClientError as e:
        print(f"❌ Error downloading {r2_key}: {e}")
        return False


def sync_data():
    """Main sync function."""
    print("🚀 Starting R2 data sync...")
    
    # Create local data directory
    Path(LOCAL_DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Create R2 client
    client = create_r2_client()
    if not client:
        print("❌ Cannot proceed without R2 connection")
        return False
    
    # List R2 objects
    r2_objects = list_r2_objects(client)
    if not r2_objects:
        print("❌ No data files found in R2")
        return False
    
    # Sync each file
    success_count = 0
    total_files = len(r2_objects)
    
    for obj in r2_objects:
        r2_key = obj['key']
        local_file = os.path.join(LOCAL_DATA_DIR, os.path.basename(r2_key))
        
        # Check if we need to download
        should_download = FORCE_REFRESH
        
        if not should_download:
            if not os.path.exists(local_file):
                should_download = True
                print(f"📄 Local file missing: {r2_key}")
            else:
                # Compare file sizes (simple check)
                local_size = os.path.getsize(local_file)
                if local_size != obj['size']:
                    should_download = True
                    print(f"📄 Size mismatch for {r2_key}: local={local_size}, R2={obj['size']}")
        
        if should_download:
            if download_file(client, r2_key, local_file):
                success_count += 1
            else:
                print(f"❌ Failed to download {r2_key}")
        else:
            print(f"✅ File up to date: {r2_key}")
            success_count += 1
    
    print(f"\n📊 Sync Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {total_files - success_count}")
    
    if success_count == total_files:
        print("🎉 Data sync completed successfully!")
        return True
    else:
        print("⚠️  Data sync completed with errors")
        return False


def check_data_availability():
    """Check if data is available locally."""
    if not os.path.exists(LOCAL_DATA_DIR):
        return False
    
    parquet_files = [f for f in os.listdir(LOCAL_DATA_DIR) if f.endswith('.parquet')]
    
    if not parquet_files:
        print(f"📂 No parquet files found in {LOCAL_DATA_DIR}")
        return False
    
    print(f"✅ Found {len(parquet_files)} parquet files locally")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Sync data from Cloudflare R2')
    parser.add_argument('--force', action='store_true',
                       help='Force re-download even if data exists')
    args = parser.parse_args()

    print("=" * 50)
    print("🌤️  Cloudflare R2 Data Sync")
    print("=" * 50)

    # Check if data already exists and force refresh is not enabled
    force_refresh = FORCE_REFRESH or args.force
    if not force_refresh and check_data_availability():
        print("✅ Data already available locally. Skipping sync.")
        print("   Use --force flag or FORCE_DATA_REFRESH=true to force re-download")
        return 0

    if force_refresh:
        print("🔄 Force refresh enabled - will re-download data")

    # Perform sync
    success = sync_data()

    if success:
        print("\n🎉 Data sync successful! Application ready to start.")
        return 0
    else:
        print("\n❌ Data sync failed! Check configuration and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())