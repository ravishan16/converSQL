#!/usr/bin/env python3
"""
converSQL - Natural Language to SQL Query Generation Platform
Powered by AI, ontological data modeling, and analytical intelligence.

Multi-provider AI support for flexible SQL generation.
"""

import os
import time

import pandas as pd
import streamlit as st

# Import AI service with new adapter pattern
from src.ai_service import generate_sql_with_ai, get_ai_service
from src.branding import get_favicon_path, get_logo_data_uri

# Import core functionality
from src.core import (
    execute_sql_query,
    get_ai_service_status,
    get_analyst_questions,
    get_table_schemas,
    scan_parquet_files,
)
from src.simple_auth import get_auth_service

# Import authentication
from src.simple_auth_components import simple_auth_wrapper
from src.ui import render_app_footer
from src.ui.style_optimized import load_css
from src.visualization import render_visualization

# Configure page with professional styling
favicon_path = get_favicon_path()

st.set_page_config(
    page_title="converSQL - Natural Language to SQL",
    page_icon=str(favicon_path) if favicon_path else "💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load optimized CSS styling
load_css()

# Load configuration from environment variables
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def display_results(result_df: pd.DataFrame, title: str, execution_time: float = None):
    """Display query results with download option and performance metrics."""
    if not result_df.empty:
        # Persist latest results for re-renders and visualization state
        st.session_state["last_result_df"] = result_df
        st.session_state["last_result_title"] = title

        st.markdown("<div class='results-card'>", unsafe_allow_html=True)
        # Compact performance header
        performance_info = f"✅ {title}: {len(result_df):,} rows"
        if execution_time:
            performance_info += f" • ⚡ {execution_time:.2f}s"
        st.success(performance_info)

        # More compact result metrics in fewer columns
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        with col1:
            st.metric("📊 Rows", f"{len(result_df):,}")
        with col2:
            st.metric("📋 Cols", len(result_df.columns))
        with col3:
            if execution_time:
                st.metric("⚡ Time", f"{execution_time:.2f}s")
        with col4:
            # Download button in the metrics row to save space
            csv_data = result_df.to_csv(index=False)
            filename = title.lower().replace(" ", "_") + "_results.csv"
            st.download_button(
                label="📥 CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                key=f"download_{title}",
            )

        # Use full width for the dataframe with responsive height
        height = min(600, max(200, len(result_df) * 35 + 50))  # Dynamic height based on rows
        st.dataframe(result_df, use_container_width=True, height=height)

        # Render chart beneath the table
        render_visualization(result_df)

        st.markdown("</div>", unsafe_allow_html=True)
        # Mark that we rendered results in this run to avoid double-render in persisted blocks
        st.session_state["_rendered_this_run"] = True
    else:
        st.warning("⚠️ No results found")


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_parquet_files():
    """Load and cache parquet files."""
    return scan_parquet_files()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_schema_context(_parquet_files):
    """Load and cache schema context."""
    return get_table_schemas(_parquet_files)


@st.cache_resource(ttl=3600)  # Cache for 1 hour
def load_ai_service():
    """Load and cache AI service with adapter pattern."""
    return get_ai_service()


def initialize_app_data():
    """Initialize application data and AI services efficiently."""
    # Initialize session state for non-data items only if missing
    if "generated_sql" not in st.session_state:
        st.session_state.generated_sql = ""
    if "ai_error" not in st.session_state:
        st.session_state.ai_error = ""
    if "show_edit_sql" not in st.session_state:
        st.session_state.show_edit_sql = False
    # Initialize result persistence slots
    st.session_state.setdefault("ai_query_result_df", None)
    st.session_state.setdefault("manual_query_result_df", None)
    st.session_state.setdefault("last_result_df", None)
    st.session_state.setdefault("last_result_title", None)

    # Reset per-run flags
    st.session_state["_rendered_this_run"] = False

    # Check if we need to initialize data (avoid reinitializing on every rerun)
    if "app_initialized" not in st.session_state or not st.session_state.app_initialized:
        # Show spinner only if we're actually loading data
        if "parquet_files" not in st.session_state:
            with st.spinner("🔄 Loading data files..."):
                st.session_state.parquet_files = load_parquet_files()

        if "schema_context" not in st.session_state:
            with st.spinner("🔄 Building schema context..."):
                st.session_state.schema_context = load_schema_context(st.session_state.parquet_files)

        if "ai_service" not in st.session_state:
            with st.spinner("🔄 Initializing AI services..."):
                st.session_state.ai_service = load_ai_service()
                st.session_state.ai_available = st.session_state.ai_service.is_available()

        # Mark as initialized only after all components are loaded
        st.session_state.app_initialized = True


def main():
    """Main Streamlit application."""

    # Check if data is available (should be loaded by now)
    if not st.session_state.get("parquet_files", []):
        st.error("❌ No data files found. Please ensure Parquet files are in the data/processed/ directory.")
        return

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
                        # No rerun needed - selectbox change triggers auto-rerun

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

    # Enhanced tab layout with separate tabs for Manual SQL and Schema
    tab_query, tab_manual, tab_ontology, tab_schema = st.tabs(
        [
            "🔍 Query Builder",
            "🛠️ Manual SQL",
            "️ Data Ontology",
            "🗂️ Database Schema",
        ]
    )

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    with tab_query:
        st.markdown(
            """
        <div class='section-card'>
            <div class='section-card__header'>
                <h3>Ask Questions About Your Loan Data</h3>
                <p>Use natural language to query your loan portfolio data.</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # More compact analyst question dropdown
        analyst_questions = get_analyst_questions()

        query_col1, query_col2 = st.columns([4, 1], gap="medium")
        with query_col1:
            selected_question = st.selectbox(
                "💡 **Common Questions:**",
                [""] + list(analyst_questions.keys()),
                help="Select a pre-defined question",
            )

        with query_col2:
            st.write("")
            if st.button("🎯 Use", disabled=not selected_question, use_container_width=True):
                if selected_question in analyst_questions:
                    st.session_state.user_question = analyst_questions[selected_question]
                    # No rerun needed - Streamlit will auto-update the text_area

        # Professional question input with better styling
        # Initialize user_question in session state
        if "user_question" not in st.session_state:
            st.session_state["user_question"] = ""

        st.markdown("<label class='text-label'>💭 Your Question:</label>", unsafe_allow_html=True)
        user_question = st.text_area(
            "Your Question",
            placeholder="e.g., What are the top 10 states by loan volume and their average interest rates?",
            help="Ask your question in natural language - be specific for better results",
            height=100,
            label_visibility="collapsed",
            key="user_question",
        )

        # AI Generation - Always show button, disable if conditions not met
        ai_service = st.session_state.get("ai_service")
        ai_provider = ai_service.get_active_provider() if ai_service else None

        # Get provider display name
        if ai_service and ai_provider:
            available_providers = ai_service.get_available_providers()
            provider_name = available_providers.get(ai_provider, ai_provider.title())
        else:
            provider_name = "AI"

        ai_available = st.session_state.get("ai_available", False)
        is_ai_ready = ai_available and user_question.strip()

        generate_button = st.button(
            f"🤖 Generate SQL with {provider_name}",
            type="primary",
            use_container_width=True,
            disabled=not is_ai_ready,
            help="Enter a question above to generate SQL" if not is_ai_ready else None,
        )

        if generate_button and is_ai_ready:
            with st.spinner(f"🧠 {provider_name} is analyzing your question..."):
                start_time = time.time()
                sql_query, error_msg = generate_sql_with_ai(user_question, st.session_state.get("schema_context", ""))
                ai_generation_time = time.time() - start_time
                st.session_state.generated_sql = sql_query
                st.session_state.ai_error = error_msg
                # Hide Edit panel on fresh generation to avoid empty editor gaps
                st.session_state.show_edit_sql = False

                # Log query for authenticated users
                auth = get_auth_service()
                if auth.is_authenticated() and sql_query and not error_msg:
                    auth.log_query(user_question, sql_query, provider_name, ai_generation_time)

                if sql_query and not error_msg:
                    st.info(f"🤖 {provider_name} generated SQL in {ai_generation_time:.2f} seconds")

        # Show warning only if AI is unavailable but user entered text
        if user_question.strip() and not st.session_state.get("ai_available", False):
            AI_UNAVAILABLE_MSG = (
                "🤖 AI Assistant unavailable. Please configure Claude API or AWS Bedrock access, "
                "or use Manual SQL in the Advanced tab."
            )
            st.warning(AI_UNAVAILABLE_MSG)

        # Display AI errors
        if st.session_state.ai_error:
            st.error(st.session_state.ai_error)
            st.session_state.ai_error = ""

        # Always show execute section, but conditionally enable
        st.markdown(
            """
            <div style='border-top: 1px solid var(--color-border-light); margin: 1.5rem 0;'></div>
            """,
            unsafe_allow_html=True,
        )

        # Show generated SQL with inline edit button
        has_sql = bool(st.session_state.generated_sql.strip()) if st.session_state.generated_sql else False
        if st.session_state.generated_sql:
            # Header with edit button inline
            col_header, col_edit = st.columns([10, 1])
            with col_header:
                st.markdown("**🧠 AI-Generated SQL**")
            with col_edit:
                if st.button("✏️", key="edit_sql_inline", disabled=not has_sql, help="Edit SQL"):
                    st.session_state.show_edit_sql = True
                    # No rerun needed - editor will appear on next natural render

            st.code(st.session_state.generated_sql, language="sql")

        # Execute button - full width
        if has_sql:
            execute_button = st.button(
                "✅ Execute Query",
                type="primary",
                use_container_width=True,
                key="execute_ai_query",
            )
            if execute_button:
                with st.spinner("⚡ Running query..."):
                    try:
                        start_time = time.time()
                        result_df = execute_sql_query(
                            st.session_state.generated_sql,
                            st.session_state.get("parquet_files", []),
                        )
                        execution_time = time.time() - start_time
                        # Hide Edit panel on execute to avoid empty editor gaps
                        st.session_state.show_edit_sql = False
                        # Persist AI results for re-renders
                        st.session_state["ai_query_result_df"] = result_df
                        st.session_state["last_result_tab"] = "tab1"
                        display_results(result_df, "AI Query Results", execution_time)
                    except Exception as e:
                        st.error(f"❌ Query execution failed: {str(e)}")
                        st.info("💡 Try editing the SQL or rephrasing your question")

        # (Edit panel moved to render AFTER results to avoid pre-results blank space)

        # If user requested editing, show modal-style editor in place
        if st.session_state.get("show_edit_sql", False):
            st.markdown("---")

            # Header with close button
            header_col, close_col = st.columns([10, 1])
            with header_col:
                st.markdown("**✏️ Edit SQL Query**")
            with close_col:
                if st.button("✖️", key="close_edit", help="Close editor"):
                    st.session_state.show_edit_sql = False
                    # No rerun needed - button click triggers auto-rerun

            edited_sql = st.text_area(
                "SQL Query",
                value=st.session_state.generated_sql,
                height=200,
                key="edit_sql",
                label_visibility="collapsed",
            )

            # Only Run button, full width
            if st.button("🚀 Run Edited Query", type="primary", use_container_width=True, key="run_edited"):
                with st.spinner("⚡ Running edited query..."):
                    try:
                        start_time = time.time()
                        result_df = execute_sql_query(
                            edited_sql,
                            st.session_state.get("parquet_files", []),
                        )
                        execution_time = time.time() - start_time
                        # Update session state and collapse editor
                        st.session_state.generated_sql = edited_sql
                        st.session_state.show_edit_sql = False
                        st.session_state["ai_query_result_df"] = result_df
                        st.session_state["last_result_tab"] = "tab1"
                        display_results(result_df, "Edited Query Results", execution_time)
                    except Exception as e:
                        st.error(f"❌ Query execution failed: {str(e)}")
                        st.info("💡 Check your SQL syntax and try again")

            st.markdown("---")

        # Persisted results rendering for AI tab: show last results across reruns
        # FIXED: Only show if we have actual data AND didn't render in this run
        if (
            st.session_state.get("last_result_tab") == "tab1"
            and isinstance(st.session_state.get("last_result_df"), pd.DataFrame)
            and not st.session_state.get("_rendered_this_run", False)
            and not st.session_state["last_result_df"].empty
        ):
            display_results(
                st.session_state["last_result_df"],
                st.session_state.get("last_result_title", "Previous Results"),
            )

    with tab_ontology:
        st.markdown(
            """
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: var(--color-text-primary); font-weight: 400; margin-bottom: 0.5rem;'>
                🗺️ Data Ontology Explorer
            </h3>
            <p style='color: var(--color-text-secondary); margin: 0; font-size: 0.95rem;'>
                Explore the structured organization of your data by domain and field.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Import ontology data
        from src.data_dictionary import LOAN_ONTOLOGY, PORTFOLIO_CONTEXT

        # Optional quick search across all fields (kept because you liked this)
        q = (
            st.text_input(
                "🔎 Quick search (field name or description)",
                key="ontology_quick_search",
                placeholder="e.g., CSCORE_B, OLTV, DTI",
            )
            .strip()
            .lower()
        )
        if q:
            results = []
            for domain_name, domain_info in LOAN_ONTOLOGY.items():
                for fname, meta in domain_info.get("fields", {}).items():
                    desc = getattr(meta, "description", "")
                    dtype = getattr(meta, "data_type", "")
                    if q in fname.lower() or q in str(desc).lower() or q in str(dtype).lower():
                        results.append((domain_name, fname, desc, dtype))
            if results:
                st.markdown("#### 🔍 Search results")
                for domain_name, fname, desc, dtype in results[:100]:
                    st.markdown(f"• **{fname}** ({dtype}) — {desc}")
                    st.caption(f"Domain: {domain_name.replace('_', ' ').title()}")
                st.markdown("---")
            else:
                st.info("No matching fields found.")

        # Domain Explorer (old format)
        st.markdown("### 🏗️ Ontological Domains")
        domain_names = list(LOAN_ONTOLOGY.keys())

        # Initialize session state to prevent navigation on first interaction
        if "ontology_domain_selector" not in st.session_state:
            st.session_state["ontology_domain_selector"] = domain_names[0] if domain_names else None

        selected_domain = st.selectbox(
            "Choose a domain to explore:",
            options=domain_names,
            format_func=lambda x: f"{x.replace('_', ' ').title()} ({len(LOAN_ONTOLOGY[x]['fields'])} fields)",
            key="ontology_domain_selector",
        )

        if selected_domain:
            domain_info = LOAN_ONTOLOGY[selected_domain]

            # Domain header card
            st.markdown(
                f"""
            <div style='background: linear-gradient(135deg, var(--color-accent-primary) 0%, var(--color-accent-primary-darker) 100%);
                        padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0; font-weight: 500;'>
                    {selected_domain.replace('_', ' ').title()}
                </h4>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.95rem;'>
                    {domain_info['domain_description']}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Fields table
            st.markdown("#### 📋 Fields in this Domain")
            fields_data = []
            for field_name, field_meta in domain_info["fields"].items():
                risk_indicator = "🔴" if getattr(field_meta, "risk_impact", None) else "🟢"
                fields_data.append(
                    {
                        "Field": field_name,
                        "Risk": risk_indicator,
                        "Description": getattr(field_meta, "description", ""),
                        "Business Context": (
                            (getattr(field_meta, "business_context", "") or "")[:100]
                            + ("..." if len(getattr(field_meta, "business_context", "")) > 100 else "")
                        ),
                    }
                )

            fields_df = pd.DataFrame(fields_data)
            st.dataframe(
                fields_df,
                use_container_width=True,
                hide_index=True,
            )

            # Field detail explorer
            st.markdown("#### 🔍 Field Details")
            field_names = list(domain_info["fields"].keys())
            selected_field = st.selectbox(
                "Select a field for detailed information:",
                options=field_names,
                key=f"field_select_{selected_domain}",
            )

            if selected_field:
                field_meta = domain_info["fields"][selected_field]
                st.markdown(
                    f"""
                <div style='background: var(--color-background-alt); padding: 1.5rem; border-radius: 8px; border-left: 4px solid var(--color-accent-primary-darker);'>
                    <h5 style='color: var(--color-text-primary); margin-top: 0;'>{selected_field}</h5>
                    <p><strong>Domain:</strong> {getattr(field_meta, 'domain', selected_domain)}</p>
                    <p><strong>Data Type:</strong> <code>{getattr(field_meta, 'data_type', '')}</code></p>
                    <p><strong>Description:</strong> {getattr(field_meta, 'description', '')}</p>
                    <p><strong>Business Context:</strong> {getattr(field_meta, 'business_context', '')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if getattr(field_meta, "risk_impact", None):
                    st.warning(f"⚠️ **Risk Impact:** {getattr(field_meta, 'risk_impact', '')}")
                if getattr(field_meta, "values", None):
                    st.markdown("**Value Codes:**")
                    for code, description in getattr(field_meta, "values", {}).items():
                        st.markdown(f"• `{code}`: {description}")
                if getattr(field_meta, "relationships", None):
                    st.info(f"🔗 **Relationships:** {', '.join(getattr(field_meta, 'relationships', []))}")
        st.markdown("### ⚖️ Risk Assessment Framework")
        st.markdown(
            f"""
        <div style='background: var(--color-warning-bg); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--color-accent-primary-darker); border: 1px solid var(--color-border-light); color: var(--color-warning-text);'>
            <p><strong>Credit Triangle:</strong> {PORTFOLIO_CONTEXT['risk_framework']['credit_triangle']}</p>
            <ul>
                <li><strong>Super Prime:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['super_prime']}</li>
                <li><strong>Prime:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['prime']}</li>
                <li><strong>Alt-A:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['alt_a']}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with tab_manual:
        st.markdown(
            """
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: var(--color-text-primary); font-weight: 400; margin-bottom: 0.5rem;'>
                🛠️ Manual SQL Query
            </h3>
            <p style='color: var(--color-text-secondary); margin: 0; font-size: 0.95rem;'>
                Write and execute SQL directly against the in-memory DuckDB table <code>data</code>.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Sample queries for manual use
        # Sample queries for manual use
        sample_queries = {
            "": "",
            "Total Portfolio": (
                "SELECT COUNT(*) as total_loans, ROUND(SUM(ORIG_UPB)/1000000, 2) " "as total_upb_millions FROM data"
            ),
            "Geographic Analysis": "SELECT STATE, COUNT(*) as loan_count, ROUND(AVG(ORIG_UPB), 0) as avg_upb, ROUND(AVG(ORIG_RATE), 2) as avg_rate FROM data WHERE STATE IS NOT NULL GROUP BY STATE ORDER BY loan_count DESC LIMIT 10",
            "Credit Risk": "SELECT CASE WHEN CSCORE_B < 620 THEN 'Subprime' WHEN CSCORE_B < 680 THEN 'Near Prime' WHEN CSCORE_B < 740 THEN 'Prime' ELSE 'Super Prime' END as credit_tier, COUNT(*) as loans, ROUND(AVG(OLTV), 1) as avg_ltv FROM data WHERE CSCORE_B IS NOT NULL GROUP BY credit_tier ORDER BY MIN(CSCORE_B)",
            "High LTV Analysis": "SELECT STATE, COUNT(*) as high_ltv_loans, ROUND(AVG(CSCORE_B), 0) as avg_credit_score FROM data WHERE OLTV > 90 AND STATE IS NOT NULL GROUP BY STATE HAVING COUNT(*) > 100 ORDER BY high_ltv_loans DESC",
        }

        # Initialize session state if not exists (prevents navigation on first interaction)
        if "manual_sql_text" not in st.session_state:
            st.session_state["manual_sql_text"] = ""
        if "manual_sample_query_selector" not in st.session_state:
            st.session_state["manual_sample_query_selector"] = ""

        # Sample query selector with Use button
        col1, col2 = st.columns([4, 1])
        with col1:
            selected_sample = st.selectbox(
                "📋 Choose a sample query:",
                [""] + list(sample_queries.keys())[1:],  # Skip the empty key
                key="manual_sample_query_selector",
            )
        with col2:
            st.write("")  # Spacing
            if st.button("🎯 Use", disabled=not selected_sample, use_container_width=True, key="use_manual_sample"):
                if selected_sample in sample_queries:
                    st.session_state["manual_sql_text"] = sample_queries[selected_sample]

        # Keep a compact, consistent editor area to avoid large empty gaps
        # Note: When using key, don't set value - session state controls it
        manual_sql = st.text_area(
            "Write your SQL query:",
            height=140,
            placeholder="SELECT * FROM data LIMIT 10",
            help="Use 'data' as the table name",
            key="manual_sql_text",
        )

        # Always show execute button, disable if no query
        has_manual_sql = bool(manual_sql.strip())
        execute_manual = st.button(
            "🚀 Execute Manual Query",
            type="primary",
            use_container_width=True,
            disabled=not has_manual_sql,
            help="Enter SQL query above to execute" if not has_manual_sql else None,
            key="execute_manual_button",
        )

        if execute_manual and has_manual_sql:
            with st.spinner("⚡ Running manual query..."):
                start_time = time.time()
                result_df = execute_sql_query(manual_sql, st.session_state.get("parquet_files", []))
                execution_time = time.time() - start_time
                # Persist for re-renders and visualization
                st.session_state["manual_query_result_df"] = result_df
                st.session_state["last_result_tab"] = "tab_manual"
                display_results(result_df, "Manual Query Results", execution_time)

        # Persisted results rendering for Manual SQL tab: show last results across reruns
        if (
            st.session_state.get("last_result_tab") == "tab_manual"
            and isinstance(st.session_state.get("last_result_df"), pd.DataFrame)
            and not st.session_state.get("_rendered_this_run", False)
        ):
            display_results(
                st.session_state["last_result_df"],
                st.session_state.get("last_result_title", "Previous Results"),
            )

    with tab_schema:
        st.markdown(
            """
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: var(--color-text-primary); font-weight: 400; margin-bottom: 0.5rem;'>
                    🗂️ Database Schema
                </h3>
                <p style='color: var(--color-text-secondary); margin: 0; font-size: 0.95rem;'>
                    Explore the physical schema and ontology-aligned views.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Schema presentation options
        schema_view = st.radio(
            "Choose schema view:",
            ["🎯 Quick Reference", "📋 Ontological Schema", "💻 Raw SQL"],
            horizontal=True,
        )

        schema_context = st.session_state.get("schema_context", "")

        if schema_view == "🎯 Quick Reference":
            # Quick reference with domain summary
            from src.data_dictionary import LOAN_ONTOLOGY

            st.markdown("#### Key Data Domains")

            # Create a compact domain overview
            for i in range(0, len(LOAN_ONTOLOGY), 3):  # Display in rows of 3
                cols = st.columns(3)
                domains = list(LOAN_ONTOLOGY.items())[i : i + 3]

                for j, (domain_name, domain_info) in enumerate(domains):
                    with cols[j]:
                        field_count = len(domain_info["fields"])

                        # Create colored cards for each domain
                        colors = [
                            "#F3E5D9",
                            "#E7C8B2",
                            "#F6EDE2",
                            "#E4C590",
                            "#ECD9C7",
                        ]
                        color = colors[i // 3 % len(colors)]

                        st.markdown(
                            f"""
                            <div style='background: {color}; color: var(--color-text-primary); padding: 1rem;
                                        border-radius: 8px; margin-bottom: 0.5rem; text-align: center; border: 1px solid var(--color-border-light);'>
                                <h5 style='margin: 0; font-size: 0.9rem;'>{domain_name.replace('_', ' ').title()}</h5>
                                <p style='margin: 0.25rem 0 0 0; font-size: 0.8rem; opacity: 0.85;'>
                                    {field_count} fields
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Sample fields reference
            st.markdown("#### 🔍 Common Fields")
            key_fields = {
                "LOAN_ID": "Unique loan identifier",
                "ORIG_DATE": "Origination date (MMYYYY)",
                "STATE": "State code (e.g., 'CA', 'TX')",
                "CSCORE_B": "Primary borrower FICO score",
                "OLTV": "Original loan-to-value ratio (%)",
                "DTI": "Debt-to-income ratio (%)",
                "ORIG_UPB": "Original unpaid balance ($)",
                "CURRENT_UPB": "Current unpaid balance ($)",
                "PURPOSE": "P=Purchase, R=Refi, C=CashOut",
            }

            field_cols = st.columns(2)
            field_items = list(key_fields.items())
            for i, (field, desc) in enumerate(field_items):
                col_idx = i % 2
                with field_cols[col_idx]:
                    st.markdown(f"• **{field}**: {desc}")

        elif schema_view == "📋 Ontological Schema":
            # Organized schema by domains
            if schema_context:
                # Extract the organized parts of the schema
                lines = schema_context.split("\n")
                in_create_table = False
                current_section = []
                sections = []

                for line in lines:
                    if "CREATE TABLE" in line:
                        if current_section:
                            sections.append("\n".join(current_section))
                        current_section = [line]
                        in_create_table = True
                    elif in_create_table:
                        current_section.append(line)
                        if line.strip() == ");":
                            in_create_table = False
                    elif not in_create_table and line.strip():
                        current_section.append(line)

                if current_section:
                    sections.append("\n".join(current_section))

                # Display each section with better formatting
                for i, section in enumerate(sections):
                    if "CREATE TABLE" in section:
                        table_name = section.split("CREATE TABLE ")[1].split(" (")[0]
                        with st.expander(f"📊 Table: {table_name.upper()}", expanded=i == 0):
                            st.code(section, language="sql")
                    elif section.strip():
                        with st.expander("📚 Business Intelligence Context", expanded=False):
                            st.text(section)
            else:
                st.warning("Schema not available")

        else:  # Raw SQL
            # Raw SQL schema view
            with st.expander("🗂️ Complete SQL Schema", expanded=False):
                if schema_context:
                    st.code(schema_context, language="sql")
                else:
                    st.warning("Schema not available")

    # Footer content with professional design
    ai_status = get_ai_service_status()
    ai_provider_text = ""
    if ai_status["available"]:
        provider = ai_status["active_provider"]
        if provider == "claude":
            ai_provider_text = "Claude API (Anthropic)"
        elif provider == "bedrock":
            ai_provider_text = "Amazon Bedrock"
        else:
            ai_provider_text = "AI Assistant"
    else:
        ai_provider_text = "Manual Analysis Mode"

    render_app_footer(ai_provider_text)


if __name__ == "__main__":
    # Initialize app data before authentication
    initialize_app_data()

    # Wrap main function with authentication
    simple_auth_wrapper(main)()
