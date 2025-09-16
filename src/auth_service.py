#!/usr/bin/env python3
"""
Supabase Authentication Service
Handles Google OAuth, user sessions, and profile management for Streamlit app.
"""

import streamlit as st
from supabase import create_client, Client
import os
import time
import json
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'


class AuthService:
    """Supabase authentication service for Streamlit."""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.enabled = ENABLE_AUTH
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Initialize Supabase client."""
        if not self.enabled:
            return
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.warning("⚠️ Authentication service unavailable.")
            self.enabled = False
            return
        
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            st.error(f"❌ Authentication service error: {str(e)[:100]}...")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return self.enabled and self.supabase is not None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        if not self.is_enabled():
            return True  # Skip auth if disabled
        
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user."""
        if not self.is_authenticated():
            return None
        
        return st.session_state.get('user')
    
    def get_auth_url(self, redirect_to: str = None) -> str:
        """Get Google OAuth URL."""
        if not self.is_enabled():
            return ""
        
        try:
            # Use the current URL as redirect if not specified
            if not redirect_to:
                redirect_to = st.query_params.get('redirect', 'http://localhost:8501')
            
            response = self.supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_to
                }
            })
            
            if response and hasattr(response, 'url'):
                return response.url
            else:
                return ""
            
        except Exception:
            return ""
    
    def handle_oauth_callback(self, url_params: Dict[str, Any]) -> bool:
        """Handle OAuth callback and set user session."""
        if not self.is_enabled():
            return True
        
        try:
            # Check for OAuth callback parameters
            if 'access_token' in url_params:
                access_token = url_params['access_token'][0]
                refresh_token = url_params.get('refresh_token', [None])[0]
                
                # Set session
                response = self.supabase.auth.set_session(access_token, refresh_token)
                
                if response.user:
                    # Store user in session state
                    st.session_state.user = {
                        'id': response.user.id,
                        'email': response.user.email,
                        'name': response.user.user_metadata.get('name', 'Unknown'),
                        'avatar_url': response.user.user_metadata.get('avatar_url'),
                        'provider': 'google',
                        'authenticated_at': time.time()
                    }
                    
                    # Create or update user profile in database
                    self._upsert_user_profile(st.session_state.user)
                    
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"❌ OAuth callback error: {e}")
            return False
    
    def _upsert_user_profile(self, user: Dict[str, Any]):
        """Create or update user profile in Supabase."""
        try:
            profile_data = {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'avatar_url': user.get('avatar_url'),
                'last_login': 'now()',
                'provider': user.get('provider', 'google')
            }
            
            # Upsert user profile
            self.supabase.table('user_profiles').upsert(profile_data).execute()
            
        except Exception as e:
            # Don't fail auth if profile update fails
            print(f"Warning: Failed to update user profile: {e}")
    
    def sign_out(self):
        """Sign out current user."""
        if not self.is_enabled():
            return
        
        try:
            self.supabase.auth.sign_out()
            
            # Clear session state
            if 'user' in st.session_state:
                del st.session_state.user
            
            # Clear other user-specific session data
            keys_to_clear = [
                'user_preferences', 
                'query_history',
                'generated_sql',
                'bedrock_error'
            ]
            
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
                    
        except Exception as e:
            st.error(f"❌ Sign out error: {e}")
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from database."""
        if not self.is_authenticated():
            return {}
        
        try:
            user = self.get_current_user()
            response = self.supabase.table('user_preferences').select('*').eq('user_id', user['id']).execute()
            
            if response.data:
                return response.data[0].get('preferences', {})
            
            return {}
            
        except Exception:
            return {}
    
    def save_user_preferences(self, preferences: Dict[str, Any]):
        """Save user preferences to database."""
        if not self.is_authenticated():
            return
        
        try:
            user = self.get_current_user()
            data = {
                'user_id': user['id'],
                'preferences': preferences,
                'updated_at': 'now()'
            }
            
            self.supabase.table('user_preferences').upsert(data).execute()
            
        except Exception as e:
            print(f"Warning: Failed to save user preferences: {e}")
    
    def log_query(self, question: str, sql_query: str, provider: str, execution_time: float):
        """Log user query for analytics and history."""
        if not self.is_authenticated():
            return
        
        try:
            user = self.get_current_user()
            data = {
                'user_id': user['id'],
                'question': question,
                'sql_query': sql_query,
                'ai_provider': provider,
                'execution_time': execution_time,
                'created_at': 'now()'
            }
            
            self.supabase.table('query_history').insert(data).execute()
            
        except Exception as e:
            print(f"Warning: Failed to log query: {e}")
    
    def get_user_query_history(self, limit: int = 10) -> list:
        """Get user's query history."""
        if not self.is_authenticated():
            return []
        
        try:
            user = self.get_current_user()
            response = self.supabase.table('query_history')\
                .select('*')\
                .eq('user_id', user['id'])\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception:
            return []


# Global auth service instance
_auth_service = None


def get_auth_service() -> AuthService:
    """Get or create global auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def require_auth():
    """Decorator/function to require authentication."""
    auth = get_auth_service()
    
    if not auth.is_enabled():
        return True  # Skip if auth disabled
    
    if not auth.is_authenticated():
        return False
    
    return True


def check_auth_callback():
    """Check for OAuth callback in URL parameters."""
    auth = get_auth_service()
    
    if not auth.is_enabled():
        return
    
    # Get URL parameters
    query_params = dict(st.query_params)
    
    # Handle different OAuth callback scenarios
    callback_handled = False
    
    # Method 1: Direct token callback
    if 'access_token' in query_params:
        # Convert single values to lists for backward compatibility
        formatted_params = {k: [v] if isinstance(v, str) else v for k, v in query_params.items()}
        if auth.handle_oauth_callback(formatted_params):
            callback_handled = True
    
    # Method 2: Authorization code callback
    elif 'code' in query_params:
        try:
            # Exchange code for session
            auth_code = query_params['code']
            response = auth.supabase.auth.exchange_code_for_session({
                "auth_code": auth_code
            })
            
            if response.user:
                # Store user in session state
                st.session_state.user = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'name': response.user.user_metadata.get('name', 'Unknown'),
                    'avatar_url': response.user.user_metadata.get('avatar_url'),
                    'provider': 'google',
                    'authenticated_at': time.time()
                }
                callback_handled = True
        except Exception:
            pass
    
    # Method 3: Error handling
    elif any(param in query_params for param in ['error', 'error_code', 'error_description']):
        st.error("❌ Authentication failed. Please try again.")
        callback_handled = True
    
    # Clear URL and refresh if callback was handled
    if callback_handled:
        st.query_params.clear()
        st.rerun()