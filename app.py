#!/usr/bin/env python3
"""
Single Family Loan Analytics Platform
Advanced data intelligence and AI-powered loan portfolio analysis.
"""

import streamlit as st
import pandas as pd
import os
import time
from typing import List

# Import core functionality
from src.core import (
    initialize_ai_client,
    scan_parquet_files,
    get_table_schemas,
    generate_sql_with_bedrock,
    execute_sql_query,
    get_analyst_questions,
    get_ai_service_status
)

# Import authentication
from src.simple_auth_components import simple_auth_wrapper
from src.simple_auth import get_auth_service

# Configure page with professional styling
st.set_page_config(
    page_title="Single Family Loan Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: none;
    border-bottom: 1px solid #dee2e6;
}
.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 8px 8px 0 0;
    color: #495057;
    font-weight: 500;
    padding: 0.75rem 1.5rem;
    margin: 0 0.25rem;
    border-bottom: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
    color: white;
    border-color: #007bff;
    box-shadow: 0 2px 4px rgba(0,123,255,0.2);
}
.metric-card {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.5rem;
    padding: 1rem;
}
.stSelectbox > div > div {
    border-radius: 0.5rem;
}
.stTextArea > div > div {
    border-radius: 0.5rem;
}
.stButton > button {
    border-radius: 0.5rem;
    font-weight: 500;
}
.stSuccess {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}
.stWarning {
    background-color: #fff3cd;
    border-color: #ffeaa7;
    color: #856404;
}
</style>
""", unsafe_allow_html=True)

# Load configuration from environment variables
DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'


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
                key=f"download_{title}"
            )
        
        # Use full width for the dataframe with responsive height
        height = min(600, max(200, len(result_df) * 35 + 50))  # Dynamic height based on rows
        st.dataframe(
            result_df,
            width="stretch",
            height=height
        )
        
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
def load_ai_client():
    """Load and cache AI client."""
    return initialize_ai_client()

def initialize_app_data():
    """Initialize application data and AI services efficiently."""
    # Initialize session state for non-data items only if missing
    if 'generated_sql' not in st.session_state:
        st.session_state.generated_sql = ""
    if 'bedrock_error' not in st.session_state:
        st.session_state.bedrock_error = ""
    if 'show_edit_sql' not in st.session_state:
        st.session_state.show_edit_sql = False

    # Check if we need to initialize data (avoid reinitializing on every rerun)
    if 'app_initialized' not in st.session_state or not st.session_state.app_initialized:
        # Show spinner only if we're actually loading data
        if 'parquet_files' not in st.session_state:
            with st.spinner("🔄 Loading data files..."):
                st.session_state.parquet_files = load_parquet_files()

        if 'schema_context' not in st.session_state:
            with st.spinner("🔄 Building schema context..."):
                st.session_state.schema_context = load_schema_context(st.session_state.parquet_files)

        if 'ai_client' not in st.session_state or 'ai_provider' not in st.session_state:
            with st.spinner("🔄 Initializing AI services..."):
                st.session_state.ai_client, st.session_state.ai_provider = load_ai_client()
                st.session_state.ai_available = st.session_state.ai_client is not None

        # Mark as initialized only after all components are loaded
        st.session_state.app_initialized = True


def main():
    """Main Streamlit application."""
    
    # Check if data is available (should be loaded by now)
    if not st.session_state.get('parquet_files', []):
        st.error("❌ No data files found. Please ensure Parquet files are in the data/processed/ directory.")
        return
    
    # Professional sidebar with enhanced styling
    with st.sidebar:
        # Header with better styling
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0; margin-bottom: 1rem; 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border-radius: 8px; border: 1px solid #dee2e6;'>
            <h3 style='color: #495057; margin: 0; font-weight: 400;'>📊 System Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Data overview with metrics styling
        parquet_files = st.session_state.get('parquet_files', [])
        st.markdown("""
        <div style='margin-bottom: 0.5rem;'>
            <span style='color: #6c757d; font-size: 0.9rem; font-weight: 500;'>Data Files:</span>
            <span style='color: #28a745; font-weight: 600; margin-left: 0.5rem;'>{}</span>
        </div>
        """.format(len(parquet_files)), unsafe_allow_html=True)
        
        # Professional AI status display
        ai_status = get_ai_service_status()
        if ai_status['available']:
            provider_name = ai_status['active_provider'].title()
            st.markdown("""
            <div style='background-color: #d4edda; border: 1px solid #c3e6cb; 
                        border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;'>
                <div style='color: #155724; font-weight: 500;'>
                    🤖 AI Assistant: {}
                </div>
            </div>
            """.format(provider_name), unsafe_allow_html=True)
            
            # Show provider details in professional expander
            with st.expander("🔧 AI Provider Details", expanded=False):
                status = ai_status['provider_status']
                st.markdown("""
                **System Status:**
                - **Active Provider**: {}
                - **Bedrock**: {}
                - **Claude API**: {}
                """.format(
                    provider_name,
                    '✅ Available' if status['bedrock'] else '❌ Unavailable',
                    '✅ Available' if status['claude'] else '❌ Unavailable'
                ))
        else:
            st.markdown("""
            <div style='background-color: #fff3cd; border: 1px solid #ffeaa7; 
                        border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;'>
                <div style='color: #856404; font-weight: 500;'>
                    🤖 AI Assistant: Unavailable
                </div>
                <div style='color: #856404; font-size: 0.85rem; margin-top: 0.25rem;'>
                    Configure Claude API or Bedrock access
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Professional configuration status with debug info
        if DEMO_MODE:
            st.markdown("""
            <div style='background-color: #cce5ff; border: 1px solid #b3d7ff;
                        border-radius: 6px; padding: 0.5rem; margin: 0.5rem 0;'>
                <div style='color: #004085; font-size: 0.9rem; font-weight: 500;'>
                    🧪 Demo Mode Active
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                if 'user' in st.session_state:
                    user = st.session_state.user
                    st.markdown("**User Session:**")
                    st.markdown(f"- **Email**: {user.get('email', 'N/A')}")
                    st.markdown(f"- **Name**: {user.get('name', 'N/A')}")
                    st.markdown(f"- **Auth Time**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.get('authenticated_at', 0)))}")

                # Configuration status
                st.markdown("**Configuration:**")
                st.markdown(f"- **Google Client ID**: {'✅ Set' if os.getenv('GOOGLE_CLIENT_ID') else '❌ Missing'}")
                st.markdown(f"- **Google Client Secret**: {'✅ Set' if os.getenv('GOOGLE_CLIENT_SECRET') else '❌ Missing'}")
                st.markdown(f"- **Enable Auth**: {os.getenv('ENABLE_AUTH', 'true')}")
        
        st.markdown("<div style='margin: 1rem 0; border-bottom: 1px solid #e9ecef;'></div>", unsafe_allow_html=True)
        
        # Professional data tables section
        with st.expander("📋 Available Tables", expanded=False):
            parquet_files = st.session_state.get('parquet_files', [])
            if parquet_files:
                for file_path in parquet_files:
                    table_name = os.path.splitext(os.path.basename(file_path))[0]
                    st.markdown(f"<div style='color: #495057; margin: 0.25rem 0;'>• <span style='font-weight: 500;'>{table_name}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color: #6c757d; font-style: italic;'>No tables loaded</div>", unsafe_allow_html=True)
        
        # Professional quick stats section
        with st.expander("📈 Portfolio Overview", expanded=True):
            if st.session_state.parquet_files:
                try:
                    import duckdb
                    conn = duckdb.connect()
                    
                    # Get record count
                    total = conn.execute("SELECT COUNT(*) FROM 'data/processed/data.parquet'").fetchone()[0]
                    
                    # Get total file size
                    total_size = sum(os.path.getsize(f) for f in st.session_state.parquet_files if os.path.exists(f))
                    
                    # Clean metrics display - one per row for readability
                    st.metric("📊 Total Records", f"{total:,}")
                    st.metric("💾 Data Size", format_file_size(total_size))
                    st.metric("📁 Data Files", len(st.session_state.parquet_files))
                    if total > 0 and total_size > 0:
                        records_per_mb = int(total / (total_size / (1024*1024)))
                        st.metric("⚡ Record Density", f"{records_per_mb:,} per MB")
                    
                    conn.close()
                    
                except Exception:
                    # Fallback stats - clean single column layout
                    total_size = sum(os.path.getsize(f) for f in st.session_state.parquet_files if os.path.exists(f))
                    st.metric("📁 Data Files", len(st.session_state.parquet_files))
                    st.metric("💾 Data Size", format_file_size(total_size))
            else:
                st.markdown("<div style='color: #6c757d; font-style: italic; text-align: center; padding: 1rem;'>No data loaded</div>", unsafe_allow_html=True)
    
    # Professional header with subtle styling
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='color: #2c3e50; margin-bottom: 0.5rem; font-weight: 300;'>
            🏠 Single Family Loan Analytics
        </h1>
        <p style='color: #6c757d; font-size: 1.1rem; margin: 0;'>
            AI-Powered Loan Portfolio Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced tab layout with ontology exploration
    tab1, tab2, tab3 = st.tabs(["🔍 Query Builder", "🗺️ Data Ontology", "🔧 Advanced"])
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    with tab1:
        st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #495057; font-weight: 400; margin-bottom: 0.5rem;'>
                Ask Questions About Your Loan Data
            </h3>
            <p style='color: #6c757d; margin: 0; font-size: 0.95rem;'>
                Use natural language to query your loan portfolio data
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # More compact analyst question dropdown
        analyst_questions = get_analyst_questions()
        
        col1, col2 = st.columns([4, 1])
        with col1:
            selected_question = st.selectbox(
                "💡 **Common Questions:**",
                [""] + list(analyst_questions.keys()),
                help="Select a pre-defined question"
            )
        
        with col2:
            st.write("")  # Add spacing to align button
            if st.button("🎯 Use", disabled=not selected_question):
                if selected_question in analyst_questions:
                    st.session_state.user_question = analyst_questions[selected_question]
                    st.rerun()
        
        # Professional question input with better styling
        st.markdown("<div style='margin: 1.5rem 0 0.5rem 0;'><label style='font-weight: 500; color: #495057;'>💭 Your Question:</label></div>", unsafe_allow_html=True)
        user_question = st.text_area(
            "Your Question",
            value=st.session_state.get('user_question', ''),
            placeholder="e.g., What are the top 10 states by loan volume and their average interest rates?",
            help="Ask your question in natural language - be specific for better results",
            height=100,
            label_visibility="collapsed"
        )
        
        # AI Generation - Always show button, disable if conditions not met
        ai_provider = st.session_state.get('ai_provider')
        provider_name = ai_provider.title() if ai_provider else "AI"
        ai_available = st.session_state.get('ai_available', False)
        is_ai_ready = ai_available and user_question.strip()
        
        generate_button = st.button(
            f"🤖 Generate SQL with {provider_name}",
            type="primary",
            width="stretch",
            disabled=not is_ai_ready,
            help="Enter a question above to generate SQL" if not is_ai_ready else None
        )
        
        if generate_button and is_ai_ready:
            with st.spinner(f"🧠 {provider_name} is analyzing your question..."):
                start_time = time.time()
                sql_query, error_msg = generate_sql_with_bedrock(
                    user_question, 
                    st.session_state.get('schema_context', ''),
                    st.session_state.get('ai_client')
                )
                ai_generation_time = time.time() - start_time
                st.session_state.generated_sql = sql_query
                st.session_state.bedrock_error = error_msg
                
                # Log query for authenticated users
                auth = get_auth_service()
                if auth.is_authenticated() and sql_query and not error_msg:
                    auth.log_query(user_question, sql_query, provider_name, ai_generation_time)
                
                if sql_query and not error_msg:
                    st.info(f"🤖 {provider_name} generated SQL in {ai_generation_time:.2f} seconds")
        
        # Show warning only if AI is unavailable but user entered text
        if user_question.strip() and not st.session_state.get('ai_available', False):
            st.warning("🤖 AI Assistant unavailable. Please configure Claude API or AWS Bedrock access, or use Manual SQL in the Advanced tab.")
        
        # Display AI errors
        if st.session_state.bedrock_error:
            st.error(st.session_state.bedrock_error)
            st.session_state.bedrock_error = ""
        
        # Always show execute section, but conditionally enable
        st.markdown("---")
        
        # Show generated SQL if available
        if st.session_state.generated_sql:
            st.markdown("### 🧠 AI-Generated SQL")
            st.code(st.session_state.generated_sql, language="sql")
        
        # Always show buttons, disable based on state
        col1, col2 = st.columns([3, 1])
        with col1:
            has_sql = bool(st.session_state.generated_sql.strip()) if st.session_state.generated_sql else False
            execute_button = st.button(
                "✅ Execute Query",
                type="primary",
                width="stretch",
                disabled=not has_sql,
                help="Generate SQL first to execute" if not has_sql else None
            )
            if execute_button and has_sql:
                with st.spinner("⚡ Running query..."):
                    start_time = time.time()
                    result_df = execute_sql_query(st.session_state.generated_sql, st.session_state.get('parquet_files', []))
                    execution_time = time.time() - start_time
                    display_results(result_df, "AI Query Results", execution_time)
        
        with col2:
            edit_button = st.button(
                "✏️ Edit",
                width="stretch",
                disabled=not has_sql,
                help="Generate SQL first to edit" if not has_sql else None
            )
            if edit_button and has_sql:
                st.session_state.show_edit_sql = True
            
            # Edit SQL interface
            if st.session_state.get('show_edit_sql', False):
                st.markdown("### ✏️ Edit SQL Query")
                edited_sql = st.text_area(
                    "Modify the query:",
                    value=st.session_state.generated_sql,
                    height=150,
                    key="edit_sql"
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("🚀 Run Edited Query", type="primary", width="stretch"):
                        with st.spinner("⚡ Running edited query..."):
                            start_time = time.time()
                            result_df = execute_sql_query(edited_sql, st.session_state.get('parquet_files', []))
                            execution_time = time.time() - start_time
                            display_results(result_df, "Edited Query Results", execution_time)
                with col2:
                    if st.button("❌ Cancel", width="stretch"):
                        st.session_state.show_edit_sql = False
                        st.rerun()
    
    with tab2:
        st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #495057; font-weight: 400; margin-bottom: 0.5rem;'>
                🗺️ Data Ontology Explorer
            </h3>
            <p style='color: #6c757d; margin: 0; font-size: 0.95rem;'>
                Explore the structured organization of all 110+ data fields across 15 business domains
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Import ontology data
        from src.data_dictionary import LOAN_ONTOLOGY, PORTFOLIO_CONTEXT

        # Portfolio Overview
        # st.markdown("### 📊 Portfolio Overview")

        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.metric(
        #         label="📈 Total Coverage",
        #         value=PORTFOLIO_CONTEXT['overview']['coverage'].split()[0] + " M loans"
        #     )
        # with col2:
        #     st.metric(
        #         label="📅 Data Vintage",
        #         value=PORTFOLIO_CONTEXT['overview']['vintage_range']
        #     )
        # with col3:
        #     st.metric(
        #         label="🎯 Loss Rate",
        #         value=PORTFOLIO_CONTEXT['performance_summary']['lifetime_loss_rate']
        #     )

        st.markdown("<br>", unsafe_allow_html=True)

        # Domain Explorer
        st.markdown("### 🏗️ Ontological Domains")

        # Create domain selection
        domain_names = list(LOAN_ONTOLOGY.keys())
        selected_domain = st.selectbox(
            "Choose a domain to explore:",
            options=domain_names,
            format_func=lambda x: f"{x.replace('_', ' ').title()} ({len(LOAN_ONTOLOGY[x]['fields'])} fields)"
        )

        if selected_domain:
            domain_info = LOAN_ONTOLOGY[selected_domain]

            # Domain header
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0; font-weight: 500;'>
                    {selected_domain.replace('_', ' ').title()}
                </h4>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.95rem;'>
                    {domain_info['domain_description']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Fields in this domain
            st.markdown("#### 📋 Fields in this Domain")

            fields_data = []
            for field_name, field_meta in domain_info['fields'].items():
                risk_indicator = "🔴" if field_meta.risk_impact else "🟢"

                fields_data.append({
                    "Field": field_name,
                    "Risk": risk_indicator,
                    "Description": field_meta.description,
                    "Business Context": field_meta.business_context[:100] + "..." if len(field_meta.business_context) > 100 else field_meta.business_context
                })

            # Display fields table
            fields_df = pd.DataFrame(fields_data)
            st.dataframe(
                fields_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Field": st.column_config.TextColumn(width="medium"),
                    "Risk": st.column_config.TextColumn(width="small"),
                    "Description": st.column_config.TextColumn(width="large"),
                    "Business Context": st.column_config.TextColumn(width="large")
                }
            )

            # Field detail explorer
            st.markdown("#### 🔍 Field Details")
            field_names = list(domain_info['fields'].keys())
            selected_field = st.selectbox(
                "Select a field for detailed information:",
                options=field_names,
                key=f"field_select_{selected_domain}"
            )

            if selected_field:
                field_meta = domain_info['fields'][selected_field]

                # Field details card
                st.markdown(f"""
                <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #007bff;'>
                    <h5 style='color: #495057; margin-top: 0;'>{selected_field}</h5>
                    <p><strong>Domain:</strong> {field_meta.domain}</p>
                    <p><strong>Data Type:</strong> <code>{field_meta.data_type}</code></p>
                    <p><strong>Description:</strong> {field_meta.description}</p>
                    <p><strong>Business Context:</strong> {field_meta.business_context}</p>
                </div>
                """, unsafe_allow_html=True)

                # Risk impact if present
                if field_meta.risk_impact:
                    st.warning(f"⚠️ **Risk Impact:** {field_meta.risk_impact}")

                # Values/codes if present
                if field_meta.values:
                    st.markdown("**Value Codes:**")
                    for code, description in field_meta.values.items():
                        st.markdown(f"• `{code}`: {description}")

                # Relationships if present
                if field_meta.relationships:
                    st.info(f"🔗 **Relationships:** {', '.join(field_meta.relationships)}")

        # Risk Framework Summary
        st.markdown("### ⚖️ Risk Assessment Framework")
        st.markdown(f"""
        <div style='background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;'>
            <p><strong>Credit Triangle:</strong> {PORTFOLIO_CONTEXT['risk_framework']['credit_triangle']}</p>
            <ul>
                <li><strong>Super Prime:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['super_prime']}</li>
                <li><strong>Prime:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['prime']}</li>
                <li><strong>Alt-A:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['alt_a']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: #495057; font-weight: 400; margin-bottom: 0.5rem;'>
                🔧 Advanced Options
            </h3>
            <p style='color: #6c757d; margin: 0; font-size: 0.95rem;'>
                Manual SQL queries and database schema exploration
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🛠️ Manual SQL Query")
            
            # Sample queries for manual use
            sample_queries = {
                "": "",
                "Total Portfolio": "SELECT COUNT(*) as total_loans, ROUND(SUM(ORIG_UPB)/1000000, 2) as total_upb_millions FROM data",
                "Geographic Analysis": "SELECT STATE, COUNT(*) as loan_count, ROUND(AVG(ORIG_UPB), 0) as avg_upb, ROUND(AVG(ORIG_RATE), 2) as avg_rate FROM data WHERE STATE IS NOT NULL GROUP BY STATE ORDER BY loan_count DESC LIMIT 10",
                "Credit Risk": "SELECT CASE WHEN CSCORE_B < 620 THEN 'Subprime' WHEN CSCORE_B < 680 THEN 'Near Prime' WHEN CSCORE_B < 740 THEN 'Prime' ELSE 'Super Prime' END as credit_tier, COUNT(*) as loans, ROUND(AVG(OLTV), 1) as avg_ltv FROM data WHERE CSCORE_B IS NOT NULL GROUP BY credit_tier ORDER BY MIN(CSCORE_B)",
                "High LTV Analysis": "SELECT STATE, COUNT(*) as high_ltv_loans, ROUND(AVG(CSCORE_B), 0) as avg_credit_score FROM data WHERE OLTV > 90 AND STATE IS NOT NULL GROUP BY STATE HAVING COUNT(*) > 100 ORDER BY high_ltv_loans DESC"
            }
            
            selected_sample = st.selectbox("📋 Choose a sample query:", list(sample_queries.keys()))
            
            manual_sql = st.text_area(
                "Write your SQL query:",
                value=sample_queries[selected_sample],
                height=200,
                placeholder="SELECT * FROM data LIMIT 10",
                help="Use 'data' as the table name"
            )
            
            # Always show execute button, disable if no query
            has_manual_sql = bool(manual_sql.strip())
            execute_manual = st.button(
                "🚀 Execute Manual Query",
                type="primary",
                width="stretch",
                disabled=not has_manual_sql,
                help="Enter SQL query above to execute" if not has_manual_sql else None
            )
            
            if execute_manual and has_manual_sql:
                with st.spinner("⚡ Running manual query..."):
                    start_time = time.time()
                    result_df = execute_sql_query(manual_sql, st.session_state.get('parquet_files', []))
                    execution_time = time.time() - start_time
                    display_results(result_df, "Manual Query Results", execution_time)
        
        with col2:
            st.markdown("### 📊 Database Schema")

            # Schema presentation options
            schema_view = st.radio(
                "Choose schema view:",
                ["🎯 Quick Reference", "📋 Ontological Schema", "💻 Raw SQL"],
                horizontal=True
            )

            schema_context = st.session_state.get('schema_context', '')

            if schema_view == "🎯 Quick Reference":
                # Quick reference with domain summary
                from src.data_dictionary import LOAN_ONTOLOGY

                st.markdown("#### Key Data Domains")

                # Create a compact domain overview
                for i in range(0, len(LOAN_ONTOLOGY), 3):  # Display in rows of 3
                    cols = st.columns(3)
                    domains = list(LOAN_ONTOLOGY.items())[i:i+3]

                    for j, (domain_name, domain_info) in enumerate(domains):
                        with cols[j]:
                            field_count = len(domain_info['fields'])

                            # Create colored cards for each domain
                            colors = ["#3498db", "#e74c3c", "#f39c12", "#2ecc71", "#9b59b6"]
                            color = colors[i//3 % len(colors)]

                            st.markdown(f"""
                            <div style='background: {color}; color: white; padding: 1rem;
                                        border-radius: 8px; margin-bottom: 0.5rem; text-align: center;'>
                                <h5 style='margin: 0; font-size: 0.9rem;'>{domain_name.replace('_', ' ').title()}</h5>
                                <p style='margin: 0.25rem 0 0 0; font-size: 0.8rem; opacity: 0.9;'>
                                    {field_count} fields
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

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
                    "PURPOSE": "P=Purchase, R=Refi, C=CashOut"
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
                    lines = schema_context.split('\n')
                    in_create_table = False
                    current_section = []
                    sections = []

                    for line in lines:
                        if 'CREATE TABLE' in line:
                            if current_section:
                                sections.append('\n'.join(current_section))
                            current_section = [line]
                            in_create_table = True
                        elif in_create_table:
                            current_section.append(line)
                            if line.strip() == ');':
                                in_create_table = False
                        elif not in_create_table and line.strip():
                            current_section.append(line)

                    if current_section:
                        sections.append('\n'.join(current_section))

                    # Display each section with better formatting
                    for i, section in enumerate(sections):
                        if 'CREATE TABLE' in section:
                            table_name = section.split('CREATE TABLE ')[1].split(' (')[0]
                            with st.expander(f"📊 Table: {table_name.upper()}", expanded=i==0):
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
    
    # Professional footer with enhanced styling
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    # Footer content with professional design
    ai_status = get_ai_service_status()
    ai_provider_text = ""
    if ai_status['available']:
        provider = ai_status['active_provider']
        if provider == 'claude':
            ai_provider_text = "Claude API (Anthropic)"
        elif provider == 'bedrock':
            ai_provider_text = "Amazon Bedrock"
        else:
            ai_provider_text = "AI Assistant"
    else:
        ai_provider_text = "Manual Analysis Mode"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-top: 1px solid #dee2e6; padding: 2rem; margin-top: 2rem;
                text-align: center; border-radius: 0 0 8px 8px;'>
        <div style='color: #495057; font-weight: 500; font-size: 0.9rem; margin-bottom: 0.5rem;'>
            🏠 Single Family Loan Analytics Platform
        </div>
        <div style='color: #6c757d; font-size: 0.8rem; line-height: 1.4;'>
            Powered by <strong>Streamlit</strong> • <strong>DuckDB</strong> • <strong>Google OAuth</strong> • <strong>{ai_provider_text}</strong><br>
            <span style='font-size: 0.75rem; opacity: 0.8;'>
                Single Family Loan Performance Data
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize app data before authentication
    initialize_app_data()
    
    # Wrap main function with authentication
    simple_auth_wrapper(main)()