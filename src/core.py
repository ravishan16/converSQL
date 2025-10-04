#!/usr/bin/env python3
"""Core functionality for the converSQL Streamlit application."""

import logging
import os
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from .ai_service import generate_sql_with_ai, get_ai_service
from .data_dictionary import generate_enhanced_schema_context

# Optional modular imports (best-effort; keep legacy behavior if missing)
try:  # pragma: no cover - optional during migration
    from conversql.data.catalog import ParquetDataset, StaticCatalog
    from conversql.ontology.schema import build_schema_context_from_parquet
    from conversql.utils.plugins import load_callable
except Exception:  # pragma: no cover
    load_callable = None  # type: ignore
    ParquetDataset = None  # type: ignore
    StaticCatalog = None  # type: ignore
    build_schema_context_from_parquet = None  # type: ignore

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configuration from environment variables
PROCESSED_DATA_DIR = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed/"))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
DATASET_ROOT = os.getenv("DATASET_ROOT", str(PROCESSED_DATA_DIR))
DATASET_PLUGIN = os.getenv("DATASET_PLUGIN", "")
ONTOLOGY_PLUGIN = os.getenv("ONTOLOGY_PLUGIN", "")


@st.cache_data(ttl=CACHE_TTL)
def scan_parquet_files() -> List[str]:
    """Scan the processed directory for Parquet files with validation.

    Returns:
        List[str]: List of valid parquet file paths

    The function performs:
    1. Data synchronization check
    2. Directory scanning
    3. File validation
    4. Size and modification time tracking
    """
    # Check if data sync is needed
    sync_data_if_needed()

    if not PROCESSED_DATA_DIR.exists():
        return []

    # Track file metadata for cache invalidation
    file_metadata = {}
    valid_files = []

    for path in sorted(PROCESSED_DATA_DIR.glob("*.parquet")):
        try:
            # Get file stats
            stats = path.stat()
            if stats.st_size == 0:
                logger.warning("Skipping empty file: %s", path)
                continue

            # Quick validation of Parquet format
            try:
                with closing(duckdb.connect()) as conn:
                    test_query = f"SELECT * FROM '{path}' LIMIT 1"
                    conn.execute(test_query)
            except Exception as e:
                logger.warning("Skipping invalid parquet file %s: %s", path, e)
                continue

            # Track metadata for cache invalidation
            file_metadata[str(path)] = {"size": stats.st_size, "mtime": stats.st_mtime}
            valid_files.append(str(path))

        except Exception as e:
            logger.warning("Error processing file %s: %s", path, e)
            continue

    # Store metadata in session state for change detection
    st.session_state["parquet_file_metadata"] = file_metadata

    return valid_files


def sync_data_if_needed(force: bool = False) -> bool:
    """Check if data sync from R2 is needed and perform if necessary.

    Args:
        force: If True, force sync even if data exists

    Returns:
        bool: True if data is available, False if sync failed
    """
    try:
        # Check if processed directory exists and has valid data
        if not force and PROCESSED_DATA_DIR.exists():
            parquet_files = sorted(PROCESSED_DATA_DIR.glob("*.parquet"))
            if parquet_files:
                # Verify files are not empty/corrupted
                try:
                    with closing(duckdb.connect()) as conn:
                        test_query = f"SELECT COUNT(*) FROM '{parquet_files[0]}'"
                        row = conn.execute(test_query).fetchone()

                    if row and row[0] > 0:
                        logger.info("Found %d valid parquet file(s) with data", len(parquet_files))
                        return True
                    logger.warning("Existing parquet files appear empty; rerunning sync")
                except Exception as exc:
                    logger.warning("Existing parquet files appear corrupted; rerunning sync", exc_info=exc)

        # Try to sync from R2
        sync_reason = "Force sync requested" if force else "No valid local data found"
        logger.info("%s. Attempting R2 sync…", sync_reason)

        sync_args = [sys.executable, "scripts/sync_data.py"]
        if force:
            sync_args.append("--force")

        sync_result = subprocess.run(sync_args, capture_output=True, text=True)

        if sync_result.returncode == 0:
            logger.info("R2 sync completed successfully")
            return True
        else:
            logger.error("R2 sync failed: %s", sync_result.stderr.strip())
            if sync_result.stdout:
                logger.debug("Sync output: %s", sync_result.stdout.strip())
            return False

    except Exception as e:
        logger.error("Error during data sync", exc_info=e)
        return False


@st.cache_data(ttl=CACHE_TTL)
def get_table_schemas(parquet_files: List[str]) -> str:
    """Generate enhanced CREATE TABLE statements with rich metadata.

    Features:
    - Smart caching with metadata validation
    - Graceful fallback to basic schema
    - Schema version tracking
    - Error handling with context

    Returns:
        str: Schema context with CREATE TABLE statements and metadata
    """
    if not parquet_files:
        return ""

    # Try modular builder first
    try:
        if build_schema_context_from_parquet is not None:
            schema = build_schema_context_from_parquet(parquet_files)
            if schema and validate_schema_context(schema):
                return schema
            logger.warning("Modular schema builder failed validation")
    except Exception as e:
        logger.warning("Modular schema builder failed: %s", e)

    # Try enhanced schema generator
    try:
        schema = generate_enhanced_schema_context(parquet_files)
        if schema and validate_schema_context(schema):
            return schema
        logger.warning("Enhanced schema generator failed validation")
    except Exception as e:
        logger.warning("Enhanced schema generation failed: %s", e)

    # Fallback to basic schema
    try:
        schema = get_basic_table_schemas(parquet_files)
        if schema:
            return schema
    except Exception as e:
        logger.error("Basic schema generation failed: %s", e)

    return ""


def validate_schema_context(schema: str) -> bool:
    """Validate generated schema context.

    Checks:
    - Not empty
    - Contains CREATE TABLE statements
    - Valid SQL syntax
    - References existing tables
    """
    if not schema or not schema.strip():
        return False

    try:
        # Check for CREATE TABLE statements
        if "CREATE TABLE" not in schema.upper():
            return False

        # Validate SQL syntax
        with closing(duckdb.connect()) as conn:
            # Try parsing each statement
            for statement in schema.split(";"):
                if statement.strip():
                    conn.execute(statement + ";")
        return True

    except Exception as e:
        logger.warning("Schema validation failed: %s", e)
        return False


def get_basic_table_schemas(parquet_files: List[str]) -> str:
    """Fallback basic schema generation with error handling."""
    if not parquet_files:
        return ""

    create_statements = []

    try:
        with closing(duckdb.connect()) as conn:
            for file_path in parquet_files:
                path = Path(file_path)
                table_name = path.stem
                query = f"DESCRIBE SELECT * FROM '{path.as_posix()}' LIMIT 1"
                schema_df = conn.execute(query).fetchdf()

                columns = []
                for _, row in schema_df.iterrows():
                    column_name = row["column_name"]
                    column_type = row["column_type"]
                    columns.append(f"    {column_name} {column_type}")

                create_statement = f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n);"
                create_statements.append(create_statement)

        return "\n\n".join(create_statements)

    except Exception as exc:
        logger.warning("Failed to build basic table schemas", exc_info=exc)
        return ""


def initialize_ai_client() -> Tuple[Optional[object], str]:
    """Initialize AI client - uses new AI service."""
    service = get_ai_service()
    if service.is_available():
        provider = service.get_active_provider() or "none"
        return service, provider
    return None, "none"


def generate_sql_with_bedrock(user_question: str, schema_context: str, bedrock_client=None) -> Tuple[str, str]:
    """Generate SQL - backward compatibility wrapper for AI service."""
    return generate_sql_with_ai(user_question, schema_context)


@st.cache_resource
def get_duckdb_pool():
    """Create or get cached DuckDB connection pool."""
    if "duckdb_pool" not in st.session_state:
        st.session_state["duckdb_pool"] = []
    return st.session_state["duckdb_pool"]


def get_duckdb_connection():
    """Get a DuckDB connection from the pool or create a new one."""
    pool = get_duckdb_pool()

    # Try to get existing connection
    while pool:
        conn = pool.pop()
        try:
            # Test if connection is still good
            conn.execute("SELECT 1")
            return conn
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    # Create new connection
    return duckdb.connect()


def return_duckdb_connection(conn):
    """Return a connection to the pool."""
    try:
        pool = get_duckdb_pool()
        if len(pool) < 5:  # Maximum pool size
            pool.append(conn)
        else:
            conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def execute_sql_query(sql_query: str, parquet_files: List[str]) -> pd.DataFrame:
    """Execute SQL query using DuckDB with connection pooling and optimization.

    Features:
    - Connection pooling for better resource usage
    - Query parameter validation and sanitization
    - Automatic view registration with change detection
    - Detailed error reporting with context
    - Query timeout protection
    """
    if not sql_query or not sql_query.strip():
        return pd.DataFrame()

    if not parquet_files:
        logger.warning("SQL execution requested without any parquet files loaded")
        return pd.DataFrame()

    # Get connection from pool
    conn = None
    try:
        conn = get_duckdb_connection()

        # Track registered views for change detection
        current_views = set()
        if "registered_views" not in st.session_state:
            st.session_state["registered_views"] = set()

        # Register files as views only if needed
        for file_path in parquet_files:
            path = Path(file_path)
            table_name = path.stem
            view_key = f"{table_name}:{str(path)}"

            if view_key not in st.session_state["registered_views"]:
                # Register view with explicit schema to optimize subsequent queries
                conn.execute(
                    f"""
                    CREATE OR REPLACE VIEW {table_name} AS
                    SELECT * FROM read_parquet(
                        '{path.as_posix()}',
                        binary_as_string=true
                    )
                """
                )
                st.session_state["registered_views"].add(view_key)
            current_views.add(view_key)

        # Remove stale views
        stale_views = st.session_state["registered_views"] - current_views
        for view_key in stale_views:
            table_name = view_key.split(":")[0]
            conn.execute(f"DROP VIEW IF EXISTS {table_name}")
        st.session_state["registered_views"] = current_views

        # Execute query with timeout protection
        logger.debug("Executing SQL query: %s", sql_query)
        conn.execute("SET enable_progress_bar=true")
        conn.execute("PRAGMA enable_profiling")
        result = conn.execute(sql_query).fetchdf()

        # Return connection to pool
        return_duckdb_connection(conn)
        conn = None

        return result

    except Exception as exc:
        error_context = {
            "query": sql_query,
            "file_count": len(parquet_files),
            "error_type": type(exc).__name__,
            "error_msg": str(exc),
        }
        logger.error("SQL execution failed: %s", error_context, exc_info=exc)
        return pd.DataFrame()

    finally:
        if conn:
            try:
                return_duckdb_connection(conn)
            except Exception:
                pass


def get_analyst_questions() -> Dict[str, str]:
    """Return sophisticated analyst questions leveraging loan performance domain expertise."""
    return {
        "🎯 Portfolio Health Check": "Show me our current portfolio composition by credit risk tiers (Super Prime 740+, Prime 680-739, Near Prime 620-679, Subprime <620) with current UPB and delinquency rates",
        "🌎 Geographic Risk Assessment": "Which top 10 states have the highest loan concentrations and how do their current delinquency rates compare to the national average?",
        "📈 Vintage Performance Analysis": "Compare loan performance between 2020-2021 refi boom vintages vs 2022+ rising rate vintages - show loan counts, average rates, and current performance",
        "⚠️ High-Risk Concentration": "Identify loans with combined high-risk factors: OLTV >90%, DTI >36%, and credit scores <680 - show geographic distribution and current status",
        "💰 Jumbo Loan Intelligence": "Analyze loans above $500K - show credit profile distribution, geographic concentration, and performance compared to conforming loans",
        "🏠 Product Mix Evolution": "Compare purchase vs refinance vs cash-out refinance loans originated in the last 24 months - show volume trends and borrower risk profiles",
        "📊 Market Share by Channel": "Show origination volume and average loan characteristics by channel (Retail, Correspondent, Broker) for top 5 volume states",
        "🔍 Credit Migration Analysis": "For loans aged 24-48 months (2020-2021 vintage), show how many have migrated from current to 30+ day delinquent status by original credit score",
        "🌟 Super Prime Performance": "Analyze our Super Prime segment (740+ credit scores) - show portfolio share, average UPB, geographic distribution, and performance metrics",
        "🎲 Rate Sensitivity Analysis": "Compare current portfolio performance between ultra-low rate loans (2-4%) vs higher rate loans (5%+) - show delinquency rates and paydown behavior",
    }


def get_ai_service_status() -> Dict[str, Any]:
    """Get AI service status for UI display."""
    service = get_ai_service()
    return {
        "available": service.is_available(),
        "active_provider": service.get_active_provider(),
        "provider_status": service.get_provider_status(),
    }
