"""DuckDB execution utilities."""

from __future__ import annotations

import os
from typing import List

import duckdb
import pandas as pd


def register_parquet_tables(conn: duckdb.DuckDBPyConnection, parquet_files: List[str]) -> None:
    for file_path in parquet_files:
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM '{file_path}'")


def run_query(sql: str, parquet_files: List[str]) -> pd.DataFrame:
    with duckdb.connect() as conn:
        register_parquet_tables(conn, parquet_files)
        return conn.execute(sql).fetchdf()


__all__ = ["register_parquet_tables", "run_query"]
