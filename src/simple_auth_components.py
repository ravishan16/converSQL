#!/usr/bin/env python3
"""
Simple Authentication Components for Streamlit
Clean UI components for Google OAuth login and user management.
"""

import os

import streamlit as st

from .branding import get_logo_data_uri
from .core import get_ai_service_status
from .simple_auth import get_auth_service, handle_oauth_callback
from .ui import render_app_footer


def render_login_page():
    """Render the login page with Google OAuth."""
    auth = get_auth_service()

    # Inject converSQL-specific styling for the login experience
    st.markdown(
        """
    <style>
    :root {
        --color-background: #FAF6F0;
        --color-background-alt: #FDFDFD;
        --color-text-primary: #3A3A3A;
        --color-text-secondary: #7C6F64;
        --color-accent-primary: #DDBEA9;
        --color-accent-primary-darker: #B45F4D;
        --color-border-light: #E4C590;
    }

    .footer-links {
        margin-top: 1rem;
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        flex-wrap: wrap;
    }

    .footer-links a {
        color: var(--color-accent-primary-darker);
        text-decoration: none;
        font-weight: 500;
        font-size: 0.85rem;
    }

    .footer-links a:hover {
        color: #d89c7f;
    }

    .login-wrapper {
        max-width: 560px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.75rem;
    }

    .login-hero {
        text-align: center;
        padding: 1.5rem 1rem 0 1rem;
        margin: 0;
    }

    .login-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .login-logo img {
        width: clamp(280px, 70vw, 460px);
        height: auto;
        filter: drop-shadow(0 12px 28px rgba(180, 95, 77, 0.18));
    }

    .login-logo--fallback {
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: 0.06em;
        color: var(--color-text-primary, #3A3A3A);
    }

    .login-tagline {
        color: var(--color-text-secondary, #7C6F64);
        font-size: 1.05rem;
        margin: 0.25rem 0 0 0;
    }

    .login-card {
        width: 100%;
        background: linear-gradient(140deg, var(--color-background-alt, #FDFDFD) 0%, var(--color-background, #FAF6F0) 100%);
        border: 1px solid var(--color-border-light, #E4C590);
        border-radius: 18px;
        padding: 2.5rem 2.25rem;
        text-align: center;
        box-shadow: 0 18px 40px rgba(180, 95, 77, 0.18);
    }

    .login-card h3 {
        color: var(--color-text-primary, #3A3A3A);
        font-weight: 500;
        margin-bottom: 0.85rem;
        letter-spacing: 0.01em;
    }

    .login-card p {
        color: var(--color-text-secondary, #7C6F64);
        margin-bottom: 1.75rem;
        line-height: 1.65;
    }

    .login-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        width: min(320px, 100%);
        margin: 0 auto 1.75rem auto;
        padding: 0.9rem 1.5rem;
        border-radius: 999px;
        border: 1px solid var(--color-accent-primary-darker, #B45F4D);
        background: linear-gradient(120deg, var(--color-accent-primary, #DDBEA9) 0%, var(--color-accent-primary-darker, #B45F4D) 100%);
        color: var(--color-background-alt, #FDFDFD);
        font-weight: 600;
        text-decoration: none;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 12px 24px rgba(180, 95, 77, 0.22);
    }

    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 30px rgba(180, 95, 77, 0.28);
    }

    .login-button--disabled {
        cursor: not-allowed;
        opacity: 0.7;
        background: linear-gradient(120deg, rgba(221, 190, 169, 0.6) 0%, rgba(180, 95, 77, 0.6) 100%);
        box-shadow: none;
    }

    .login-details {
        margin-top: 1.25rem;
        background: rgba(221, 190, 169, 0.18);
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid rgba(228, 197, 144, 0.55);
        text-align: left;
    }

    .login-details strong {
        color: var(--color-text-primary, #3A3A3A);
    }

    .login-divider {
        width: 100%;
        margin: 0 auto 1.75rem auto;
        border-bottom: 1px solid rgba(228, 197, 144, 0.5);
    }

    </style>
    """,
        unsafe_allow_html=True,
    )

    # Center the login content
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        logo_data_uri = get_logo_data_uri()
        if logo_data_uri:
            logo_block = "<div class='login-logo'>" f"<img src='{logo_data_uri}' alt='converSQL logo' />" "</div>"
        else:
            logo_block = "<div class='login-logo login-logo--fallback'>💬 converSQL</div>"

        auth_url = auth.get_auth_url()
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

        if auth_url:
            login_cta = (
                f"<a class='login-button' href='{auth_url}' target='_self' rel='noopener noreferrer'>"
                "🔐 <span>Sign in with Google</span>"
                "</a>"
            )
        else:
            login_cta = "<div class='login-button login-button--disabled'>" "❌ Google OAuth unavailable" "</div>"

        st.markdown(
            f"""
        <div class='login-wrapper'>
            <div class='login-hero'>
                {logo_block}
                <p class='login-tagline'>Natural language to SQL for mortgage analytics teams.</p>
            </div>
            <div class='login-card'>
                <h3>Secure access to the converSQL workspace</h3>
                <p>Authenticate with Google to run natural language analytics on your portfolio data with ontological guardrails.</p>
                {login_cta}
                <div class='login-details'>
                    <strong>What you get inside:</strong>
                    <ul style='margin: 0.75rem 0 0 1.25rem; padding: 0; color: var(--color-text-secondary, #7C6F64);'>
                        <li>Natural language ➜ SQL generation with converSQL prompts</li>
                        <li>Curated ontology of 110+ mortgage risk attributes</li>
                        <li>Portfolio performance dashboards and manual SQL console</li>
                    </ul>
                </div>
            </div>
        </div>
        <div class='login-divider'></div>
        """,
            unsafe_allow_html=True,
        )

        if demo_mode and auth_url:
            st.info("🔗 Demo mode: use the OAuth link below if you are not redirected automatically.")
            st.code(auth_url)
            st.markdown(f"[Open Google OAuth in this tab]({auth_url})")
        elif not auth_url:
            st.error("❌ Authentication service unavailable. Please check your Google OAuth configuration.")

        # Info section
        with st.expander("ℹ️ About This Application", expanded=False):
            st.markdown(
                """
            **converSQL** pairs ontological intelligence with natural language interfaces to deliver:

            - 🤖 **AI-Guided SQL** – Structured prompts that bake in mortgage risk heuristics.
            - 🧠 **Ontology-Aware Context** – 15 business domains and 110+ field definitions on tap.
            - ⚡ **Streamlined Execution** – DuckDB acceleration, cached schema, and curated prompts.
            - 🔒 **Enterprise Guardrails** – OAuth sign-in, optional audit logging, and provider failovers.
            """
            )

        # Footer matching main app styling
        ai_status = get_ai_service_status()
        if ai_status.get("available"):
            provider = ai_status.get("active_provider", "ai_assistant")
            if provider == "claude":
                ai_provider_text = "Claude API (Anthropic)"
            elif provider == "bedrock":
                ai_provider_text = "Amazon Bedrock"
            else:
                ai_provider_text = provider.replace("_", " ").title()
        else:
            ai_provider_text = "Manual Analysis Mode"

        render_app_footer(ai_provider_text)


def render_user_menu():
    """Render user menu in sidebar."""
    auth = get_auth_service()
    user = auth.get_current_user()

    if not user:
        return

    with st.sidebar:
        st.markdown("---")

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
        result = main_app_function()
        render_user_menu()
        return result

    return wrapper
