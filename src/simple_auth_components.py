#!/usr/bin/env python3
"""
Simple Authentication Components for Streamlit
Clean UI components for Google OAuth login and user management.
"""

import os
import time

import streamlit as st

from .simple_auth import get_auth_service, handle_oauth_callback


def render_login_page():
    """Render the login page with Google OAuth."""
    auth = get_auth_service()

    # Center the login content
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Professional login header
        st.markdown(
            """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: #2c3e50; font-weight: 300; margin-bottom: 0.5rem;'>
                🏠 Single Family Loan Analytics
            </h1>
            <p style='color: #6c757d; font-size: 1.1rem; margin: 0;'>
                AI-Powered Loan Portfolio Intelligence
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Professional login card
        with st.container():
            st.markdown(
                """
            <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        padding: 2.5rem; border-radius: 12px; text-align: center;
                        border: 1px solid #dee2e6; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <h3 style='color: #495057; font-weight: 400; margin-bottom: 1rem;'>
                    🔐 Secure Access Required
                </h3>
                <p style='color: #6c757d; margin-bottom: 1.5rem; line-height: 1.5;'>
                    Sign in with your Google account to access the loan analytics platform.
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Google Sign-In Button
            if st.button("🔐 Sign in with Google", type="primary", width="stretch"):
                auth_url = auth.get_auth_url()

                if auth_url:
                    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
                    if DEMO_MODE:
                        st.info("🔗 Redirecting to Google OAuth...")
                        st.code(auth_url)
                        st.markdown(f"[Click here if not redirected automatically]({auth_url})")

                    # Multiple redirect methods for better compatibility
                    st.markdown(
                        f"""
                    <meta http-equiv="refresh" content="0; url={auth_url}">
                    <script>
                        setTimeout(function() {{
                            window.open('{auth_url}', '_self');
                        }}, 100);
                    </script>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Also provide a direct link as backup
                    st.markdown(
                        f"""
                    <div style='text-align: center; margin-top: 1rem;'>
                        <a href="{auth_url}" style='color: #1f77b4; text-decoration: none;'>
                            → Continue to Google OAuth
                        </a>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    with st.spinner("Redirecting to Google..."):
                        time.sleep(2)
                else:
                    st.error("❌ Authentication service unavailable. Please check your Google OAuth configuration.")

        st.markdown("---")

        # Info section
        with st.expander("ℹ️ About This Application", expanded=False):
            st.markdown(
                """
            **Single Family Loan Analytics Platform** provides comprehensive loan data analysis:

            **Core Features:**
            - 🤖 **AI-Powered Queries**: Natural language to SQL conversion
            - 📊 **Interactive Analytics**: Dynamic data exploration and visualization
            - ⚡ **High Performance**: Optimized query engine with DuckDB
            - 🔒 **Secure Access**: Protected with Google OAuth
            - 📈 **Portfolio Insights**: Risk metrics and performance tracking

            **Data Infrastructure:**
            - Single Family Loan performance data (56.8M+ loans)
            - Real-time data sync from Cloudflare R2 storage
            - Comprehensive data dictionary with domain expertise
            """
            )

        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
            "Powered by Streamlit and Google OAuth"
            "</div>",
            unsafe_allow_html=True,
        )


def render_user_menu():
    """Render user menu in sidebar."""
    auth = get_auth_service()
    user = auth.get_current_user()

    if not user:
        return

    with st.sidebar:
        st.markdown("---")

        # User profile section
        st.markdown(
            """
        <div style='margin: 1rem 0; padding-bottom: 0.5rem; border-bottom: 1px solid #e9ecef;'>
            <h4 style='color: #495057; font-weight: 500; margin: 0;'>👤 Profile</h4>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # User info
        st.markdown(
            f"<div style='color: #495057; font-weight: 500; margin-bottom: 0.25rem;'>👤 {user.get('name', 'User')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color: #6c757d; font-size: 0.85rem; margin-bottom: 1rem;'>📧 {user.get('email', '')}</div>",
            unsafe_allow_html=True,
        )

        # Show user picture if available
        if user.get("picture"):
            st.image(user["picture"], width=50)

        # Sign out button
        if st.button("🚪 Sign Out", type="primary", width="stretch"):
            auth.sign_out()
            st.rerun()


def simple_auth_wrapper(main_app_function):
    """
    Simple auth wrapper for the entire Streamlit app.
    Usage: simple_auth_wrapper(main)()
    """

    def wrapper():
        auth = get_auth_service()

        # Handle OAuth callback FIRST
        handle_oauth_callback()

        # Skip auth if disabled
        if not auth.is_enabled():
            DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
            if DEMO_MODE:
                st.info("🔓 Authentication disabled. Running in open access mode.")
            return main_app_function()

        # Check if user is authenticated
        if not auth.is_authenticated():
            render_login_page()
            return

        # User is authenticated - show the main app
        render_user_menu()
        return main_app_function()

    return wrapper
