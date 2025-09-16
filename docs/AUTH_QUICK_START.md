# Authentication Quick Start Guide

Get Google OAuth authentication working in 10 minutes! 🚀

## ⚡ Quick Setup (10 minutes)

### 1. Create Supabase Project (3 minutes)
```bash
# Go to https://supabase.com/dashboard
# Click "New project" → Fill details → Wait for setup
```

### 2. Get Your Keys (1 minute)
In Supabase Dashboard → **Settings** → **API**:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJ[your-anon-key]
```

### 3. Set up Google OAuth (4 minutes)
1. **Google Console**: https://console.cloud.google.com/
2. **Create OAuth Client**:
   - APIs & Services → Credentials → Create OAuth 2.0 Client
   - Redirect URI: `https://your-project-id.supabase.co/auth/v1/callback`
3. **Copy Client ID & Secret**
4. **Supabase**: Authentication → Providers → Enable Google
   - Paste Client ID & Secret

### 4. Configure App (1 minute)
```bash
# Update .env file
ENABLE_AUTH=true
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJ[your-anon-key]
```

### 5. Set up Database (1 minute)
In Supabase **SQL Editor**, run:
```sql
-- User profiles table
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own profile" ON user_profiles FOR ALL USING (auth.uid() = id);

-- Query history table  
CREATE TABLE query_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    ai_provider TEXT DEFAULT 'claude',
    execution_time REAL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for query history
ALTER TABLE query_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own queries" ON query_history FOR ALL USING (auth.uid() = user_id);

-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) UNIQUE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for preferences
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;  
CREATE POLICY "Users can manage their own preferences" ON user_preferences FOR ALL USING (auth.uid() = user_id);
```

## 🎯 Test It Works

```bash
# Start the app
streamlit run app.py

# Should see login page → Click "Sign in with Google" → Success! 🎉
```

## 🔧 Development vs Production

### Development Setup
```env
ENABLE_AUTH=false  # Skip auth for quick testing
DEMO_MODE=true
```

### Production Setup
```env
ENABLE_AUTH=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ[anon-key]
DEMO_MODE=false
```

## 🚀 Docker Deployment

```bash
# Update .env with auth settings
cp .env.example .env
# Fill in your Supabase credentials

# Deploy with auth
docker-compose up -d
```

## 🎨 Auth Features You Get

### ✅ What Works Automatically
- 🔐 **Google OAuth Login** - One-click sign in
- 👤 **User Profiles** - Name, email, avatar
- 📊 **Query History** - Track user questions & SQL
- ⚙️ **User Preferences** - Save settings per user
- 🔒 **Secure Sessions** - JWT tokens, automatic refresh
- 🚪 **Sign Out** - Clean session termination

### 🎛️ UI Components
- **Login Page**: Beautiful Google OAuth interface  
- **User Menu**: Profile, history, preferences in sidebar
- **Auth Status**: Shows signed-in user
- **Protected Routes**: Automatic auth checks

### 📱 User Experience
- **Seamless Flow**: Login → Redirect → App access
- **Persistent Sessions**: Stay logged in across browser sessions
- **Query Tracking**: See your analysis history
- **Personal Settings**: Customizable preferences

## 🔍 Verification Checklist

After setup, verify these work:

- [ ] Login page appears when auth is enabled
- [ ] Google OAuth redirects and signs you in
- [ ] User profile appears in sidebar 
- [ ] Queries get logged to database
- [ ] Sign out clears session
- [ ] Re-login works seamlessly

## ⚠️ Common Issues & Fixes

### "Invalid redirect URI"
**Problem**: Google OAuth redirect doesn't match
```bash
# Fix: Check Google Console redirect URI exactly matches:
https://your-project-id.supabase.co/auth/v1/callback
```

### "Authentication not working"
**Problem**: Environment variables not loaded
```bash
# Fix: Check .env file is in project root
ls -la .env
# Should show: -rw-r--r-- 1 user user 1234 Dec 15 10:30 .env

# Fix: Restart application after env changes
```

### "User profile not created"  
**Problem**: Database policies not set correctly
```sql
-- Fix: Ensure RLS policies allow inserts
CREATE POLICY "Allow user profile creation" ON user_profiles 
    FOR INSERT WITH CHECK (auth.uid() = id);
```

### "Sign out doesn't work"
**Problem**: Session state not cleared
```bash
# Fix: Clear browser cache and local storage
# Or check auth_service.py sign_out() method
```

## 🎓 Next Steps

### Advanced Features
- **User Roles**: Admin vs regular users
- **Team Access**: Organization-based permissions  
- **API Keys**: Programmatic access
- **Audit Logs**: Track all user actions

### Customization
- **Branding**: Custom login page design
- **Providers**: Add GitHub, Microsoft OAuth
- **Workflows**: Email verification, password reset

### Monitoring  
- **Analytics**: User engagement tracking
- **Performance**: Query execution metrics
- **Security**: Failed login attempts

## 📚 Full Documentation

For complete setup details:
- [Complete Supabase Setup Guide](SUPABASE_SETUP.md)
- [Deployment Guide](DEPLOYMENT.md) 
- [R2 Setup Guide](R2_SETUP.md)

## 🆘 Need Help?

1. **Check logs**: `docker-compose logs fannie-mae-app`
2. **Supabase Dashboard**: Check Authentication → Users
3. **Database**: Verify tables exist in Table Editor
4. **Environment**: Confirm all variables are set

**Still stuck?** Open an issue with:
- Your .env file (with secrets redacted)
- Error messages from logs
- Steps you've tried

---

🎉 **That's it!** You now have enterprise-grade authentication in your Single Family Loan analytics app!