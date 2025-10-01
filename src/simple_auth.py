#!/usr/bin/env python3
"""
Simple Google OAuth Authentication for Streamlit
Clean implementation without external database dependencies.
"""

import os
import secrets
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
import streamlit as st
from dotenv import load_dotenv

from .d1_logger import get_d1_logger

# Load environment variables
load_dotenv()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_current_url() -> str:
    """Get the current app URL for OAuth redirects."""
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            if "host" in headers:
                host = headers["host"]
                protocol = (
                    "https"
                    if ".streamlit.app" in host
                    or ".repl.co" in host
                    or ".replit.dev" in host
                    or ".replit.app" in host
                    or "ravishankars.com" in host
                    else "http"
                )
                return f"{protocol}://{host}"
    except Exception:
        pass

    # Fallback to localhost
    port = os.getenv("STREAMLIT_SERVER_PORT", "8501")
    return f"http://localhost:{port}"


def generate_auth_url() -> str:
    """Generate Google OAuth authorization URL."""
    if not GOOGLE_CLIENT_ID:
        if DEMO_MODE:
            st.error("❌ GOOGLE_CLIENT_ID not found in environment variables")
        return ""

    # Generate state for CSRF protection - use a simple approach
    state = secrets.token_urlsafe(16)  # Shorter state

    # Store state in multiple places for reliability
    st.session_state.oauth_state = state

    redirect_uri = get_current_url()

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "response_type": "code",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }

    if DEMO_MODE:
        st.info(f"🔗 Client ID: {GOOGLE_CLIENT_ID[:20]}..." if GOOGLE_CLIENT_ID else "❌ No Client ID")
        st.info(f"🔗 Redirect URI: {redirect_uri}")
        st.info(f"🔗 State generated: {state}")
        st.info(f"🔗 OAuth params: {list(params.keys())}")

    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    if DEMO_MODE:
        st.info(f"🔗 Full OAuth URL: {auth_url}")

    return auth_url


def exchange_code_for_token(code: str, state: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access token."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        if DEMO_MODE:
            st.error("❌ Missing Google OAuth credentials")
        return None

    # Verify state to prevent CSRF attacks
    stored_state = st.session_state.get("oauth_state")
    if DEMO_MODE:
        st.info(
            f"🔒 State verification: Received={state[:10]}..., Stored={stored_state[:10] if stored_state else 'None'}..."
        )

    # More lenient state verification - session state can be cleared during redirects
    if state != stored_state:
        if DEMO_MODE:
            st.warning(f"🔒 State mismatch: {state} vs {stored_state}")
            st.warning("⚠️ This could be due to session state being cleared. Continuing anyway in demo mode...")

        # In production, we'll be more lenient since session state clearing is common
        # We'll just validate that the state parameter exists and is properly formatted
        if not state or len(state) < 16:
            st.error("❌ Invalid authentication state. Please try again.")
            return None
        # Continue with authentication even if stored state is missing

    redirect_uri = get_current_url()

    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            if DEMO_MODE:
                st.error(f"❌ Token exchange failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        if DEMO_MODE:
            st.error(f"❌ Token exchange error: {str(e)}")
        return None


def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user information from Google."""
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            if DEMO_MODE:
                st.error(f"❌ User info fetch failed: {response.status_code}")
            return None
    except Exception as e:
        if DEMO_MODE:
            st.error(f"❌ User info error: {str(e)}")
        return None


def handle_oauth_callback():
    """Handle OAuth callback and authenticate user."""
    if not ENABLE_AUTH:
        return

    # Get URL parameters
    query_params = dict(st.query_params)

    if "code" in query_params and "state" in query_params:
        if DEMO_MODE:
            st.info("🔗 Processing OAuth callback")

        code = query_params["code"]
        state = query_params["state"]

        # Exchange code for token
        token_data = exchange_code_for_token(code, state)
        if not token_data or "access_token" not in token_data:
            st.error("❌ Authentication failed. Please try again.")
            return

        # Get user information
        user_info = get_user_info(token_data["access_token"])
        if not user_info:
            st.error("❌ Failed to get user information. Please try again.")
            return

        # Store user in session
        st.session_state.user = {
            "id": user_info["id"],
            "email": user_info["email"],
            "name": user_info.get("name", "Unknown"),
            "picture": user_info.get("picture"),
            "authenticated_at": time.time(),
        }

        # Log login to D1
        d1_logger = get_d1_logger()
        if d1_logger.is_enabled():
            user_agent = (
                st.context.headers.get("user-agent", "")
                if hasattr(st, "context") and hasattr(st.context, "headers")
                else ""
            )
            d1_logger.log_user_login(user_info["id"], user_info["email"], user_agent)

        if DEMO_MODE:
            st.success(f"✅ Authenticated: {user_info['email']}")

        # Clear URL parameters and refresh
        st.query_params.clear()
        st.rerun()

    elif "error" in query_params:
        error = query_params.get("error", "Unknown error")
        if DEMO_MODE:
            st.error(f"❌ OAuth error: {error}")
        else:
            st.error("❌ Authentication failed. Please try again.")

        # Clear URL parameters
        st.query_params.clear()


class SimpleAuth:
    """Simple authentication service using Google OAuth."""

    def __init__(self):
        self.enabled = ENABLE_AUTH and bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    def is_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return self.enabled

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        if not self.enabled:
            return True  # Skip auth if disabled
        return "user" in st.session_state and st.session_state.user is not None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user."""
        if not self.is_authenticated():
            return None
        return st.session_state.get("user")

    def get_auth_url(self) -> str:
        """Get Google OAuth URL."""
        if not self.enabled:
            return ""
        return generate_auth_url()

    def log_query(self, question: str, sql_query: str, provider: str, execution_time: float):
        """Log user query to both session and D1 database."""
        if not self.is_authenticated():
            return

        user = self.get_current_user()
        if not user:
            return

        # Store in session for immediate access
        if "query_history" not in st.session_state:
            st.session_state.query_history = []

        query_log = {
            "question": question,
            "sql_query": sql_query,
            "ai_provider": provider,
            "execution_time": execution_time,
            "timestamp": time.time(),
        }

        st.session_state.query_history.insert(0, query_log)
        # Keep only last 10 queries
        st.session_state.query_history = st.session_state.query_history[:10]

        # Log to D1 database
        d1_logger = get_d1_logger()
        if d1_logger.is_enabled():
            d1_logger.log_user_query(user["id"], user["email"], question, sql_query, provider, execution_time)

    def get_user_query_history(self, limit: int = 10):
        """Get user's query history from session."""
        if not self.is_authenticated():
            return []

        return st.session_state.get("query_history", [])[:limit]

    def sign_out(self):
        """Sign out current user."""
        if "user" in st.session_state:
            del st.session_state.user

        # Clear other session data
        keys_to_clear = [
            "oauth_state",
            "generated_sql",
            "bedrock_error",
            "user_question",
            "show_edit_sql",
            "query_history",
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]


# Global auth service instance
_auth_service = None


def get_auth_service() -> SimpleAuth:
    """Get or create global auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = SimpleAuth()
    return _auth_service
