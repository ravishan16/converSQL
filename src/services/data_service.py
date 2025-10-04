import logging
import math
import os
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from typing import List

import duckdb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.data_dictionary import generate_enhanced_schema_context
from src.visualization import render_visualization

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configuration from environment variables
PROCESSED_DATA_DIR = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed/"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
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


@st.cache_data(ttl=CACHE_TTL)
def load_parquet_files() -> List[str]:
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
def load_schema_context(parquet_files: List[str]) -> str:
    """Generate enhanced CREATE TABLE statements with rich metadata. Cached for performance."""
    if not parquet_files:
        return ""

    return generate_enhanced_schema_context(parquet_files)
