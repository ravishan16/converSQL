# Supabase Authentication Setup Guide

Complete guide for setting up Supabase with Google OAuth for the Single Family Loan Analytics application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Create Supabase Project](#step-1-create-supabase-project)
- [Step 2: Set up Google OAuth](#step-2-set-up-google-oauth)
- [Step 3: Configure Database Schema](#step-3-configure-database-schema)
- [Step 4: Configure Application](#step-4-configure-application)
- [Step 5: Test Authentication](#step-5-test-authentication)
- [Security Configuration](#security-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Supabase account (free tier available)
- Google Cloud Console account
- Domain name (for production)

## Step 1: Create Supabase Project

### 1.1 Create New Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click **"New project"**
3. Choose your organization
4. Enter project details:
   - **Name**: `single-family-loan-analytics`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your deployment
5. Click **"Create new project"**

### 1.2 Get Project Credentials
Once created, go to **Settings** → **API**:
- **Project URL**: `https://[project-id].supabase.co`
- **Anon key**: `eyJ...` (for client-side access)
- **Service role key**: `eyJ...` (for server-side admin access)

⚠️ **Important**: Keep these credentials secure!

## Step 2: Set up Google OAuth

### 2.1 Configure Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one

2. **Enable Google+ API**
   - Go to **APIs & Services** → **Library**
   - Search for "Google+ API" 
   - Click **Enable**

3. **Configure OAuth Consent Screen**
   - Go to **APIs & Services** → **OAuth consent screen**
   - Choose **External** (for public app) or **Internal** (for organization only)
   - Fill in required fields:
     - **App name**: `Single Family Loan Analytics`
     - **User support email**: Your email
     - **Developer contact information**: Your email
   - Add scopes: `email`, `profile`, `openid`
   - Add test users if needed

4. **Create OAuth Credentials**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth 2.0 Client IDs**
   - Application type: **Web application**
   - Name: `Single Family Loan App`
   - **Authorized redirect URIs**: 
     ```
     https://[your-project-id].supabase.co/auth/v1/callback
     http://localhost:8501 (for development)
     ```
   - Click **Create**
   - Copy **Client ID** and **Client Secret**

### 2.2 Configure Supabase Authentication

1. **Go to Supabase Dashboard**
   - Navigate to **Authentication** → **Providers**
   - Find **Google** provider

2. **Enable Google Provider**
   - Toggle **Enable sign in with Google**
   - Enter your Google OAuth credentials:
     - **Client ID**: From Google Console
     - **Client Secret**: From Google Console
   - Click **Save**

3. **Configure Site URL (Production)**
   - Go to **Authentication** → **Settings**
   - **Site URL**: `https://your-domain.com`
   - **Redirect URLs**: Add your production URLs

## Step 3: Configure Database Schema

### 3.1 Create User Profiles Table

Run this SQL in **SQL Editor** in Supabase:

```sql
-- Create user_profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    provider TEXT DEFAULT 'google',
    last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to read/update their own profile
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Create policy to allow insert during signup
CREATE POLICY "Users can insert their own profile during signup" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);
```

### 3.2 Create User Preferences Table

```sql
-- Create user_preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable Row Level Security
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can manage their own preferences" ON user_preferences
    FOR ALL USING (auth.uid() = user_id);
```

### 3.3 Create Query History Table

```sql
-- Create query_history table for analytics and user history
CREATE TABLE query_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    ai_provider TEXT DEFAULT 'claude',
    execution_time REAL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE query_history ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own query history" ON query_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own queries" ON query_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create index for better performance
CREATE INDEX idx_query_history_user_created ON query_history(user_id, created_at DESC);
```

### 3.4 Create Automatic Updated At Trigger

```sql
-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Step 4: Configure Application

### 4.1 Update Environment Variables

Add to your `.env` file:

```env
# ========================================
# AUTHENTICATION (SUPABASE)
# ========================================
# Enable authentication
ENABLE_AUTH=true

# Supabase configuration
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_KEY=eyJ[your-anon-key]
SUPABASE_SERVICE_KEY=eyJ[your-service-role-key]

# Google OAuth Configuration (optional - already configured in Supabase)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 4.2 Update Docker Configuration

Add to `docker-compose.yml`:

```yaml
services:
  fannie-mae-app:
    environment:
      # ... existing environment variables ...
      
      # Authentication
      - ENABLE_AUTH=${ENABLE_AUTH:-false}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
```

## Step 5: Test Authentication

### 5.1 Start Application

```bash
# Development
streamlit run app.py

# Docker
docker-compose up -d
```

### 5.2 Test Login Flow

1. **Access Application**
   - Go to `http://localhost:8501`
   - Should see login page if auth is enabled

2. **Test Google Login**
   - Click **"Sign in with Google"**
   - Should redirect to Google OAuth
   - Grant permissions
   - Should redirect back to app and be authenticated

3. **Verify Database**
   - Check Supabase dashboard → **Authentication** → **Users**
   - Should see your user account
   - Check **Table Editor** → **user_profiles** for profile data

### 5.3 Test Features

1. **User Menu**: Check sidebar for user profile and options
2. **Query Logging**: Run a query, check `query_history` table
3. **Preferences**: Try changing settings in user menu
4. **Sign Out**: Test sign out functionality

## Security Configuration

### Production Security Settings

1. **Supabase Dashboard** → **Authentication** → **Settings**:
   ```
   Site URL: https://your-production-domain.com
   Redirect URLs: 
   - https://your-production-domain.com
   - https://your-production-domain.com/auth/callback
   
   JWT Expiry: 3600 (1 hour)
   Refresh Token Rotation: Enabled
   ```

2. **Row Level Security**: Already enabled for all tables

3. **API Keys**:
   - Use **anon key** for client-side access
   - Keep **service role key** secure (server-side only)

### Environment Security

```env
# Production settings
ENABLE_AUTH=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ[anon-key-only]
# Don't expose service key in client-side environment
```

## Advanced Configuration

### Custom Domains (Production)

1. **Configure Custom Domain**
   - Supabase Dashboard → **Settings** → **Custom Domains**
   - Add your domain: `auth.your-domain.com`
   - Update DNS records as instructed

2. **Update OAuth Redirect**
   - Google Console → Update redirect URIs
   - Use custom domain: `https://auth.your-domain.com/auth/v1/callback`

### User Roles and Permissions

```sql
-- Add user roles (optional)
ALTER TABLE user_profiles ADD COLUMN role TEXT DEFAULT 'user';

-- Create admin users
UPDATE user_profiles 
SET role = 'admin' 
WHERE email IN ('admin@yourcompany.com');

-- Create policies for admin access
CREATE POLICY "Admins can view all profiles" ON user_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );
```

## Troubleshooting

### Common Issues

#### "Invalid redirect URI"
- **Check Google Console**: Ensure redirect URI matches exactly
- **Format**: Must be `https://[project-id].supabase.co/auth/v1/callback`
- **Protocol**: Use HTTPS for production

#### "User not found in database"
- **Check RLS policies**: Ensure policies allow user insertion
- **Check auth trigger**: User profile should auto-create on signup

#### "Authentication loop"
- **Check Site URL**: Must match your application URL
- **Clear browser cache**: Clear cookies and local storage
- **Check redirect URLs**: Ensure all valid URLs are listed

#### "CORS errors"
- **Supabase Settings**: Add your domain to allowed origins
- **Local development**: Add `http://localhost:8501`

### Database Queries for Debugging

```sql
-- Check authentication users
SELECT * FROM auth.users ORDER BY created_at DESC LIMIT 10;

-- Check user profiles
SELECT * FROM user_profiles ORDER BY created_at DESC;

-- Check query history
SELECT 
    up.name,
    qh.question,
    qh.ai_provider,
    qh.created_at
FROM query_history qh
JOIN user_profiles up ON qh.user_id = up.id
ORDER BY qh.created_at DESC
LIMIT 20;

-- Check user preferences
SELECT 
    up.name,
    pref.preferences
FROM user_preferences pref
JOIN user_profiles up ON pref.user_id = up.id;
```

### Reset Authentication

```sql
-- Clear all authentication data (CAUTION: This will delete all users!)
TRUNCATE auth.users CASCADE;
TRUNCATE user_profiles CASCADE;
TRUNCATE user_preferences CASCADE;
TRUNCATE query_history CASCADE;
```

## Monitoring and Analytics

### User Analytics Queries

```sql
-- Daily active users
SELECT 
    DATE(last_login) as date,
    COUNT(DISTINCT id) as active_users
FROM user_profiles
WHERE last_login >= NOW() - INTERVAL '30 days'
GROUP BY DATE(last_login)
ORDER BY date DESC;

-- Query volume by user
SELECT 
    up.name,
    up.email,
    COUNT(qh.id) as total_queries,
    MAX(qh.created_at) as last_query
FROM user_profiles up
LEFT JOIN query_history qh ON up.id = qh.user_id
GROUP BY up.id, up.name, up.email
ORDER BY total_queries DESC;

-- AI provider usage
SELECT 
    ai_provider,
    COUNT(*) as usage_count,
    AVG(execution_time) as avg_execution_time
FROM query_history
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY ai_provider;
```

## Next Steps

1. **Configure email templates** in Supabase for password reset, etc.
2. **Set up webhooks** for user events
3. **Implement user analytics** dashboard
4. **Add social login** providers (GitHub, Microsoft)
5. **Set up monitoring** for authentication errors

For additional support:
- [Supabase Documentation](https://supabase.com/docs)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Project Issues](https://github.com/your-repo/issues)