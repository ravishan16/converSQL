npm install -g wrangler

# Cloudflare D1 Database Setup

This guide explains how to set up Cloudflare D1 for logging user activity (logins and queries) in Conversational SQL.

## Quick Setup

### 1. Create the D1 Database
```bash
npm install -g wrangler
wrangler login
wrangler d1 create nlptosql-logs
```

### 2. Initialize the Database Schema
```bash
wrangler d1 execute nlptosql-logs --file=scripts/d1_schema.sql
```

### 3. Get Database Credentials
After creation, retrieve these from your Cloudflare dashboard:
- Account ID (right sidebar)
- Database ID (from `wrangler d1 create` output)
- API Token (create a custom token with `Cloudflare D1:Edit` permission)

### 4. Update Environment Variables
Add to your `.env` file:
```bash
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_D1_DATABASE_ID=your_database_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
```

## Database Schema

Minimal tables:

### user_logins
- id: Auto increment primary key
- user_id: Google user ID
- email: User email
- login_time: Timestamp
- user_agent: Browser info

### user_queries
- id: Auto increment primary key
- user_id: Google user ID
- email: User email
- question: Natural language question
- sql_query: Generated SQL
- ai_provider: claude/bedrock
- execution_time: Query execution time
- query_time: Timestamp

## Security

- Uses Cloudflare's secure REST API
- API token with minimal D1 permissions
- No sensitive data stored (only activity logs)
- App works without database if logging is disabled

## Benefits

- Lightweight: Only two tables
- Optional: App functions without logging
- Fast: Globally distributed
- Free tier: Generous limits
- No maintenance: Managed by Cloudflare

## Testing
```bash
wrangler d1 execute nlptosql-logs --command="SELECT COUNT(*) FROM user_logins;"
```

---

Logging is optional and runs silently in the background.