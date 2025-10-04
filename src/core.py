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
    from conversql.utils.plugins import load_callable
    from conversql.data.catalog import ParquetDataset, StaticCatalog
    from conversql.ontology.schema import build_schema_context_from_parquet
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
    """Scan the processed directory for Parquet files. Cached for performance."""
    # Check if data sync is needed
    sync_data_if_needed()

    if not PROCESSED_DATA_DIR.exists():
        return []

    parquet_files = sorted(PROCESSED_DATA_DIR.glob("*.parquet"))

    return [str(path) for path in parquet_files]


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
    """Generate enhanced CREATE TABLE statements with rich metadata. Cached for performance."""
    if not parquet_files:
        return ""

    # If modular builder is available, prefer it to allow ontology swapping
    try:
        if build_schema_context_from_parquet is not None:
            return build_schema_context_from_parquet(parquet_files)
        return generate_enhanced_schema_context(parquet_files)
    except Exception:
        # Fallback to basic schema generation
        return get_basic_table_schemas(parquet_files)


def get_basic_table_schemas(parquet_files: List[str]) -> str:
    """Fallback basic schema generation."""
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


def execute_sql_query(sql_query: str, parquet_files: List[str]) -> pd.DataFrame:
    """Execute SQL query using DuckDB."""
    if not sql_query or not sql_query.strip():
        return pd.DataFrame()

    if not parquet_files:
        logger.warning("SQL execution requested without any parquet files loaded")
        return pd.DataFrame()

    try:
        with closing(duckdb.connect()) as conn:
            # Register each Parquet file as a view to avoid copying data into DuckDB
            for file_path in parquet_files:
                path = Path(file_path)
                table_name = path.stem
                conn.execute(
                    f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{path.as_posix()}')"
                )

            logger.debug("Executing SQL query: %s", sql_query)
            return conn.execute(sql_query).fetchdf()

    except Exception as exc:
        logger.error("SQL execution failed", exc_info=exc)
        return pd.DataFrame()


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
