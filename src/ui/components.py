"""
UI components for converSQL application.
Optimized for performance and maintainability.
"""

import os
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st


@st.cache_data
def format_file_size(size_bytes: float) -> str:
    """Format file size in human readable format with caching."""
    if size_bytes == 0:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def render_section_header(title: str, description: str, icon: str = "🔍") -> None:
    """Render a consistent section header."""
    st.markdown(
        f"""
        <div class='section-card__header'>
            <h3>{icon} {title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_results(
    df: pd.DataFrame,
    title: str = "Results",
    execution_time: Optional[float] = None,
    max_display_rows: int = 1000,
) -> None:
    """Display query results with optimized performance."""
    if df is None or df.empty:
        st.warning("No results returned from query.")
        return

    # Limit display for performance
    display_df = df.head(max_display_rows) if len(df) > max_display_rows else df

    st.markdown("<div class='results-card'>", unsafe_allow_html=True)

    # Header with metrics
    header_cols = st.columns([3, 1, 1, 1])

    with header_cols[0]:
        st.markdown(f"### {title}")

    with header_cols[1]:
        st.metric("Rows", f"{len(df):,}")

    with header_cols[2]:
        st.metric("Columns", len(df.columns))

    with header_cols[3]:
        if execution_time is not None:
            st.metric("Time", f"{execution_time:.2f}s")

    # Show truncation warning if needed
    if len(df) > max_display_rows:
        st.warning(f"⚠️ Showing first {max_display_rows:,} rows of {len(df):,} total results")

    # Display the dataframe with optimized settings
    try:
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=min(400, max(200, len(display_df) * 35 + 50)),
        )
    except Exception as e:
        st.error(f"Error displaying results: {e}")
        # Fallback to simple display
        st.write(display_df)

    # Visualization recommendations
    if not df.empty and len(df.columns) >= 2:
        render_visualization_section(df, title)

    st.markdown("</div>", unsafe_allow_html=True)


def render_visualization_section(df: pd.DataFrame, title: str) -> None:
    """Render minimal visualization section using the unified visualizer."""
    try:
        from src.visualization import render_visualization

        # Use a stable container key derived from title
        container_key = "viz_" + "".join(ch for ch in title.lower() if ch.isalnum() or ch == "_")
        render_visualization(df, container_key=container_key)
    except Exception as e:
        st.error(f"Visualization error: {e}")
        with st.expander("🔍 Error Details", expanded=False):
            st.code(str(e))


@st.cache_data
def get_sample_queries() -> Dict[str, str]:
    """Get cached sample queries."""
    return {
        "": "",
        "Portfolio Overview": """
        SELECT
            COUNT(*) as total_loans,
            ROUND(SUM(ORIG_UPB)/1000000, 2) as total_upb_millions,
            ROUND(AVG(ORIG_RATE), 2) as avg_interest_rate,
            ROUND(AVG(OLTV), 1) as avg_ltv
        FROM data
        """,
        "Geographic Distribution": """
        SELECT
            STATE,
            COUNT(*) as loan_count,
            ROUND(AVG(ORIG_UPB), 0) as avg_upb,
            ROUND(AVG(ORIG_RATE), 2) as avg_rate
        FROM data
        WHERE STATE IS NOT NULL
        GROUP BY STATE
        ORDER BY loan_count DESC
        LIMIT 10
        """,
        "Credit Risk Analysis": """
        SELECT
            CASE
                WHEN CSCORE_B < 620 THEN 'Subprime'
                WHEN CSCORE_B < 680 THEN 'Near Prime'
                WHEN CSCORE_B < 740 THEN 'Prime'
                ELSE 'Super Prime'
            END as credit_tier,
            COUNT(*) as loans,
            ROUND(AVG(OLTV), 1) as avg_ltv,
            ROUND(AVG(ORIG_RATE), 2) as avg_rate
        FROM data
        WHERE CSCORE_B IS NOT NULL
        GROUP BY credit_tier
        ORDER BY MIN(CSCORE_B)
        """,
        "High Risk Loans": """
        SELECT
            STATE,
            COUNT(*) as high_ltv_loans,
            ROUND(AVG(CSCORE_B), 0) as avg_credit_score,
            ROUND(AVG(ORIG_RATE), 2) as avg_rate
        FROM data
        WHERE OLTV > 90 AND STATE IS NOT NULL
        GROUP BY STATE
        HAVING COUNT(*) > 100
        ORDER BY high_ltv_loans DESC
        """,
    }


def render_query_selector(key_prefix: str = "sample") -> str:
    """Render a query selector with cached options."""
    sample_queries = get_sample_queries()

    selected_sample = st.selectbox(
        "📋 Choose a sample query:",
        list(sample_queries.keys()),
        key=f"{key_prefix}_query_selector",
    )

    return sample_queries.get(selected_sample, "")


def render_error_message(error: Exception, context: str = "operation") -> None:
    """Render standardized error messages."""
    error_msg = str(error)

    # Common error patterns and user-friendly messages
    if "no such table" in error_msg.lower():
        st.error("❌ Table not found. Please check your table name and try again.")
    elif "syntax error" in error_msg.lower():
        st.error("❌ SQL syntax error. Please check your query syntax.")
    elif "connection" in error_msg.lower():
        st.error("❌ Database connection error. Please try again.")
    elif "timeout" in error_msg.lower():
        st.error("❌ Query timeout. Try simplifying your query or reducing the data size.")
    else:
        st.error(f"❌ {context.title()} failed: {error_msg}")

    # Show detailed error in expander for debugging
    with st.expander("🔍 Error Details", expanded=False):
        st.code(f"Error Type: {type(error).__name__}\nError Message: {error_msg}")


def render_loading_state(message: str = "Loading...") -> None:
    """Render a consistent loading state."""
    st.markdown(
        f"""
        <div style='text-align: center; padding: 2rem; color: var(--color-text-secondary);'>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>⏳</div>
            <div>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_success_message(message: str, details: Optional[str] = None) -> None:
    """Render a success message with optional details."""
    st.success(f"✅ {message}")

    if details:
        st.info(details)


def render_metric_card(
    title: str,
    value: Union[str, int, float],
    delta: Optional[Union[str, int, float]] = None,
    help_text: Optional[str] = None,
) -> None:
    """Render a metric card with consistent styling."""
    delta_html = (
        f'<div style="font-size: 0.8rem; color: var(--color-accent-primary-darker);">{delta}</div>' if delta else ""
    )

    st.markdown(
        f"""
        <div class='metric-card'>
            <div style='font-size: 0.8rem; color: var(--color-text-secondary); margin-bottom: 0.25rem;'>
                {title}
            </div>
            <div style='font-size: 1.5rem; font-weight: 600; color: var(--color-text-primary);'>
                {value}
            </div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if help_text:
        st.caption(help_text)


def render_status_badge(status: str, is_active: bool = False) -> str:
    """Render a status badge with appropriate styling."""
    color = "var(--color-success-text)" if is_active else "var(--color-text-secondary)"
    bg_color = "var(--color-success-bg)" if is_active else "var(--color-background-alt)"
    border_color = "var(--color-success-border)" if is_active else "var(--color-border-light)"

    return f"""
    <span style='background: {bg_color}; color: {color}; border: 1px solid {border_color};
                 padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 500;'>
        {status}
    </span>
    """


@st.cache_data
def get_table_info(parquet_files: List[str]) -> Dict[str, Any]:
    """Get cached table information."""
    table_info = {}

    for file_path in parquet_files:
        if os.path.exists(file_path):
            table_name = os.path.splitext(os.path.basename(file_path))[0]
            file_size = os.path.getsize(file_path)

            table_info[table_name] = {
                "file_path": file_path,
                "size": file_size,
                "size_formatted": format_file_size(file_size),
            }

    return table_info


def render_data_summary(parquet_files: List[str]) -> None:
    """Render a summary of available data."""
    table_info = get_table_info(parquet_files)

    if not table_info:
        st.warning("No data tables found.")
        return

    st.markdown("### 📊 Data Summary")

    # Create summary metrics
    total_files = len(table_info)
    total_size = sum(info["size"] for info in table_info.values())

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tables", total_files)
    with col2:
        st.metric("Total Size", format_file_size(total_size))

    # Show table details
    for table_name, info in table_info.items():
        with st.expander(f"📋 {table_name.upper()}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**File Path:** `{info['file_path']}`")
            with col2:
                st.write(f"**Size:** {info['size_formatted']}")


def render_app_footer(provider_text: str, *, show_divider: bool = True) -> None:
    """Render the shared converSQL footer."""
    if show_divider:
        try:
            st.divider()
        except AttributeError:
            st.markdown("<hr />", unsafe_allow_html=True)

    st.markdown(
        f"""
    <div style='background: linear-gradient(135deg, var(--color-background) 0%, var(--color-background-alt) 100%);
                border-top: 1px solid var(--color-border-light); padding: 2rem; margin-top: 2rem;
                text-align: center; border-radius: 0 0 8px 8px;'>
        <div style='color: var(--color-text-primary); font-weight: 500; font-size: 0.9rem; margin-bottom: 0.5rem;'>
            💬 converSQL - Natural Language to SQL Query Generation Platform
        </div>
        <div style='color: var(--color-text-secondary); font-size: 0.8rem; line-height: 1.4;'>
            Powered by <strong>Streamlit</strong> • <strong>DuckDB</strong> • <strong>{provider_text}</strong> • <strong>Ontological Data Intelligence</strong><br>
            <span style='font-size: 0.75rem; opacity: 0.8;'>
                Implementation Showcase: Single Family Loan Analytics
            </span>
        </div>
        <div class='footer-links' style='margin-top: 1rem; display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;'>
            <a href='https://github.com/ravishan16/converSQL' target='_blank' rel='noopener noreferrer'
               style='color: var(--color-accent-primary-darker); text-decoration: none; font-weight: 500; font-size: 0.85rem;'>GitHub Repository</a>
            <a href='https://github.com/ravishan16/converSQL/issues' target='_blank' rel='noopener noreferrer'
               style='color: var(--color-accent-primary-darker); text-decoration: none; font-weight: 500; font-size: 0.85rem;'>Issue Tracker</a>
            <a href='https://github.com/ravishan16/converSQL/pulls' target='_blank' rel='noopener noreferrer'
               style='color: var(--color-accent-primary-darker); text-decoration: none; font-weight: 500; font-size: 0.85rem;'>Pull Requests</a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
