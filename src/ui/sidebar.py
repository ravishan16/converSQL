import os
import time

import streamlit as st

from src.branding import get_logo_data_uri
from src.services.ai_service import get_ai_service_status
from src.services.data_service import format_file_size

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def render_sidebar():
    logo_data_uri = get_logo_data_uri()

    # Professional sidebar with enhanced styling
    with st.sidebar:
        if logo_data_uri:
            st.markdown(
                f"""
        <div class='sidebar-logo'>
            <img src='{logo_data_uri}' alt='converSQL logo' />
        </div>
        """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
        <div class='sidebar-hero'>
            <span class='sidebar-hero__pill-label'>Dataset</span>
            <span class='sidebar-hero__pill-value'>🏠 Single Family Loan Analytics</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Professional AI status display (cached)
        if "ai_status_cache" not in st.session_state:
            st.session_state.ai_status_cache = get_ai_service_status()
        ai_status = st.session_state.ai_status_cache

        if ai_status["available"]:
            provider_name = ai_status["active_provider"].title()
            st.markdown(
                """
            <div style='background-color: var(--color-success-bg); border: 1px solid var(--color-success-border);
                        border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;'>
                <div style='color: var(--color-success-text); font-weight: 500;'>
                    🤖 AI Assistant: {}
                </div>
            </div>
            """.format(
                    provider_name
                ),
                unsafe_allow_html=True,
            )

            # AI Provider Selector (if multiple available)
            ai_service = st.session_state.get("ai_service")
            if ai_service:
                available_providers = ai_service.get_available_providers()

                if len(available_providers) > 1:
                    st.markdown("---")
                    st.markdown("**🔄 Switch AI Provider:**")

                    provider_options = list(available_providers.keys())
                    current_provider = ai_service.get_active_provider()

                    # Find current index
                    default_index = (
                        provider_options.index(current_provider) if current_provider in provider_options else 0
                    )

                    selected_provider = st.selectbox(
                        "Select AI Provider",
                        options=provider_options,
                        format_func=lambda x: available_providers[x],
                        index=default_index,
                        key="sidebar_provider_selector",
                        help="Choose which AI provider to use for SQL generation",
                    )

                    # Update provider if changed
                    if selected_provider != current_provider:
                        ai_service.set_active_provider(selected_provider)
                        st.rerun()

            # Show provider details in professional expander
            with st.expander("🔧 AI Provider Details", expanded=False):
                status = ai_status["provider_status"]

                # Show all available providers
                st.markdown("**Available Providers:**")
                for provider_key, is_available in status.items():
                    if provider_key != "active":
                        provider_display = provider_key.title()
                        icon = "✅" if is_available else "❌"
                        status_text = "Available" if is_available else "Unavailable"
                        active_marker = " **(Active)**" if provider_key == ai_status["active_provider"] else ""
                        st.markdown(f"- **{provider_display}**: {icon} {status_text}{active_marker}")
        else:
            st.markdown(
                """
            <div style='background-color: var(--color-warning-bg); border: 1px solid var(--color-warning-border);
                        border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;'>
                <div style='color: var(--color-warning-text); font-weight: 500;'>
                    🤖 AI Assistant: Unavailable
                </div>
                <div style='color: var(--color-warning-text); font-size: 0.85rem; margin-top: 0.25rem;'>
                    Configure Claude API or Bedrock access
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Professional configuration status with debug info
        if DEMO_MODE:
            st.markdown(
                """
            <div style='background-color: var(--color-background-alt); border: 1px solid var(--color-border-light);
                        border-radius: 6px; padding: 0.5rem; margin: 0.5rem 0;'>
                <div style='color: var(--color-text-primary); font-size: 0.9rem; font-weight: 500;'>
                    🧪 Demo Mode Active
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Show detailed debug information in demo mode
            auth = get_auth_service()

            with st.expander("🔍 Auth Debug Info", expanded=False):
                st.markdown("**Authentication Status:**")
                st.markdown(f"- **Auth Enabled**: {auth.is_enabled()}")
                st.markdown(f"- **Is Authenticated**: {auth.is_authenticated()}")
                st.markdown(f"- **Demo Mode**: {DEMO_MODE}")

                # Show current query params
                query_params = dict(st.query_params)
                if query_params:
                    st.markdown("**Current URL Parameters:**")
                    for key, value in query_params.items():
                        st.markdown(f"- **{key}**: {str(value)[:100]}")
                else:
                    st.markdown("**Current URL Parameters**: None")

                # Show user session info if authenticated
                if "user" in st.session_state:
                    user = st.session_state.user
                    st.markdown("**User Session:**")
                    st.markdown(f"- **Email**: {user.get('email', 'N/A')}")
                    st.markdown(f"- **Name**: {user.get('name', 'N/A')}")
                    st.markdown(
                        f"- **Auth Time**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.get('authenticated_at', 0)))}"
                    )

                # Configuration status
                st.markdown("**Configuration:**")
                st.markdown(f"- **Google Client ID**: {'✅ Set' if os.getenv('GOOGLE_CLIENT_ID') else '❌ Missing'}")
                st.markdown(
                    f"- **Google Client Secret**: {'✅ Set' if os.getenv('GOOGLE_CLIENT_SECRET') else '❌ Missing'}"
                )
                st.markdown(f"- **Enable Auth**: {os.getenv('ENABLE_AUTH', 'true')}")

        try:
            st.divider()
        except AttributeError:
            st.markdown("<hr />", unsafe_allow_html=True)

        # Professional data tables section
        with st.expander("📋 Available Tables", expanded=False):
            parquet_files = st.session_state.get("parquet_files", [])
            if parquet_files:
                for file_path in parquet_files:
                    table_name = os.path.splitext(os.path.basename(file_path))[0]
                    st.markdown(
                        f"<div style='color: var(--color-text-primary); margin: 0.25rem 0;'>• <span style='font-weight: 500;'>{table_name}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div style='color: var(--color-text-secondary); font-style: italic;'>No tables loaded</div>",
                    unsafe_allow_html=True,
                )

        # Professional quick stats section
        with st.expander("📈 Portfolio Overview", expanded=True):
            if st.session_state.parquet_files:
                try:
                    import duckdb  # type: ignore[import-not-found]

                    # Use in-memory connection for stats only
                    with duckdb.connect() as conn:
                        # Get record count
                        total = conn.execute("SELECT COUNT(*) FROM 'data/processed/data.parquet'").fetchone()[0]

                        # Get total file size (cached calculation)
                        if "total_data_size" not in st.session_state:
                            st.session_state.total_data_size = sum(
                                os.path.getsize(f) for f in st.session_state.parquet_files if os.path.exists(f)
                            )
                        total_size = st.session_state.total_data_size

                        # Clean metrics display - one per row for readability
                        st.metric("📊 Total Records", f"{total:,}")
                        st.metric("💾 Data Size", format_file_size(total_size))
                        st.metric("📁 Data Files", len(st.session_state.parquet_files))
                        if total > 0 and total_size > 0:
                            records_per_mb = int(total / (total_size / (1024 * 1024)))
                            st.metric("⚡ Record Density", f"{records_per_mb:,} per MB")

                except Exception:
                    # Fallback stats - clean single column layout
                    if "total_data_size" not in st.session_state:
                        st.session_state.total_data_size = sum(
                            os.path.getsize(f) for f in st.session_state.parquet_files if os.path.exists(f)
                        )
                    st.metric("📁 Data Files", len(st.session_state.parquet_files))
                    st.metric(
                        "💾 Data Size",
                        format_file_size(st.session_state.total_data_size),
                    )
            else:
                st.markdown(
                    "<div style='color: var(--color-text-secondary); font-style: italic; text-align: center; padding: 1rem;'>No data loaded</div>",
                    unsafe_allow_html=True,
                )
