-- Supabase Database Schema for Authentication and User Management
-- Run these commands in your Supabase SQL Editor

-- 1. User Profiles Table
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    provider TEXT DEFAULT 'google',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 2. User Preferences Table
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable Row Level Security
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Users can manage their own preferences
CREATE POLICY "Users can manage own preferences" ON public.user_preferences
    FOR ALL USING (auth.uid() = user_id);

-- 3. Query History Table
CREATE TABLE IF NOT EXISTS public.query_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    ai_provider TEXT NOT NULL,
    execution_time FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.query_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own query history
CREATE POLICY "Users can view own query history" ON public.query_history
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own queries
CREATE POLICY "Users can insert own queries" ON public.query_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 4. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON public.user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_query_history_user_id ON public.query_history(user_id);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON public.query_history(created_at DESC);

-- 5. Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Create triggers to automatically update timestamps
CREATE TRIGGER handle_updated_at_user_profiles
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_updated_at_user_preferences
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- 7. Grant necessary permissions (if needed)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- 8. Optional: Create a view for user analytics (admin only)
CREATE OR REPLACE VIEW public.user_analytics AS
SELECT
    up.email,
    up.name,
    up.provider,
    up.created_at as user_created_at,
    up.last_login,
    COUNT(qh.id) as total_queries,
    MAX(qh.created_at) as last_query_at,
    AVG(qh.execution_time) as avg_execution_time
FROM public.user_profiles up
LEFT JOIN public.query_history qh ON up.id = qh.user_id
GROUP BY up.id, up.email, up.name, up.provider, up.created_at, up.last_login;

-- Note: This view should only be accessible to admin users
-- You may want to create additional RLS policies for admin access