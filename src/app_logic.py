import streamlit as st

from src.services.ai_service import load_ai_service
from src.services.data_service import load_parquet_files, load_schema_context


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
