# Cloudflare D1 Database Setup

Minimal setup for user activity logging (logins and queries).

## 🚀 Quick Setup

### 1. Create D1 Database

```bash
# Install Wrangler (if not already installed)
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create D1 database
wrangler d1 create nlptosql-logs
```

### 2. Initialize Database Schema

```bash
# Run the schema creation
wrangler d1 execute nlptosql-logs --file=scripts/d1_schema.sql
```

### 3. Get Database Credentials

After creating the database, get these values from your Cloudflare dashboard:

1. **Account ID**: Dashboard → Right sidebar → Account ID
2. **Database ID**: From the `wrangler d1 create` output
3. **API Token**: Dashboard → My Profile → API Tokens → Create Token
   - Use template: "Custom token"
   - Permissions: `Cloudflare D1:Edit`
   - Account resources: Include your account

### 4. Update Environment Variables

Add to your `.env` file:

```bash
# Cloudflare D1 Database (optional)
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_D1_DATABASE_ID=your_database_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
```

## 📊 Database Schema

**Minimal tables:**

### `user_logins`
- `id` - Auto increment primary key
- `user_id` - Google user ID
- `email` - User email
- `login_time` - Timestamp
- `user_agent` - Browser info

### `user_queries`
- `id` - Auto increment primary key
- `user_id` - Google user ID
- `email` - User email
- `question` - Natural language question
- `sql_query` - Generated SQL
- `ai_provider` - claude/bedrock
- `execution_time` - Query execution time
- `query_time` - Timestamp

## 🔒 Security

- Uses Cloudflare's secure REST API
- API token with minimal D1 permissions only
- No sensitive data stored (just activity logs)
- Silent fail mode - app works without database

## ✅ Benefits

- **Lightweight**: Only 2 simple tables
- **Optional**: App works fine without it
- **Fast**: Cloudflare D1 is globally distributed
- **Free tier**: Generous limits for logging
- **No maintenance**: Managed by Cloudflare

## 🔧 Testing

```bash
# Test database connectivity
wrangler d1 execute nlptosql-logs --command="SELECT COUNT(*) FROM user_logins;"
```

---

**That's it!** The logging is completely optional and runs silently in the background.