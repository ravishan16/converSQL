-- Minimal Cloudflare D1 Schema for User Activity Logging
-- Keep it lightweight with only essential fields

-- User login tracking
CREATE TABLE IF NOT EXISTS user_logins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT
);

-- Query logging
CREATE TABLE IF NOT EXISTS user_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    ai_provider TEXT NOT NULL,
    execution_time REAL,
    query_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_logins_user_id ON user_logins(user_id);
CREATE INDEX IF NOT EXISTS idx_user_logins_time ON user_logins(login_time);
CREATE INDEX IF NOT EXISTS idx_user_queries_user_id ON user_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_user_queries_time ON user_queries(query_time);