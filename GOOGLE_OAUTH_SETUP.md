# Google OAuth Setup Guide

This app now uses direct Google OAuth for authentication - no database required!

## 🚀 Quick Setup

### 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth 2.0 Client IDs**
5. Choose **Web application**
6. Add your redirect URIs (see below)
7. Copy the **Client ID** and **Client Secret**

### 2. Configure Redirect URIs

In your Google OAuth client, add these authorized redirect URIs:

**For localhost:**
```
http://localhost:8501
```

**For IP address access:**
```
http://YOUR_IP_ADDRESS:8501
```

**For Replit:**
```
https://your-repl-name.your-username.repl.co
```

**For Streamlit Cloud:**
```
https://your-app-name.streamlit.app
```

### 3. Set Environment Variables

Create a `.env` file with:

```bash
# Google OAuth (required)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Auth settings
ENABLE_AUTH=true
DEMO_MODE=false  # Set to true for debugging
```

## ✅ Benefits of This Approach

- **No Database**: No Supabase or external database needed
- **Simple**: Just Google OAuth credentials required
- **Fast**: Direct authentication flow
- **Clean**: No complex setup or multiple services
- **Secure**: Google handles all security aspects

## 🔧 Configuration Options

```bash
ENABLE_AUTH=false    # Disable authentication entirely
DEMO_MODE=true       # Show debug information
```

## 🐛 Debugging

Set `DEMO_MODE=true` to see:
- OAuth URLs being generated
- Redirect URIs being used
- Authentication flow details
- Configuration status

## 📱 How It Works

1. User clicks "Sign in with Google"
2. App redirects to Google OAuth
3. Google redirects back with authorization code
4. App exchanges code for user information
5. User information stored in session (no database)
6. User stays authenticated until session expires

## 🔒 Security Features

- **CSRF Protection**: State parameter prevents attacks
- **Session-based**: No persistent storage of credentials
- **Google Security**: Leverages Google's security infrastructure
- **Automatic Cleanup**: Clears sensitive data on logout

## 🚀 Deployment

The app automatically detects your environment and uses the correct redirect URI:
- Localhost: `http://localhost:8501`
- IP access: `http://your-ip:8501`
- Replit: `https://repl-url`
- Streamlit Cloud: `https://app-url`

Just make sure to add all the URLs you'll use to your Google OAuth configuration!

---

**That's it!** Much simpler than the previous Supabase setup. 🎉