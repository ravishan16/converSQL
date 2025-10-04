"""Data catalog abstractions for pluggable datasets.

Provides interfaces and a default ParquetCatalog using DuckDB to scan files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Protocol


class Dataset(Protocol):
    """Dataset interface exposing table discovery and schema context."""

    def list_tables(self) -> List[str]:
        ...

    def list_parquet_files(self) -> List[str]:
        ...


@dataclass
class ParquetDataset:
    """Simple dataset over a directory of parquet files."""

    root: Path

    def list_parquet_files(self) -> List[str]:
        return [str(p) for p in sorted(self.root.glob("*.parquet"))]

    def list_tables(self) -> List[str]:
        return [Path(f).stem for f in self.list_parquet_files()]


class DataCatalog(Protocol):
    """Data catalog capable of returning the active dataset."""

    def get_active_dataset(self) -> Dataset:
        ...


@dataclass
class StaticCatalog:
    """Minimal catalog that always returns the same dataset."""

    dataset: Dataset

    def get_active_dataset(self) -> Dataset:
        return self.dataset


__all__ = [
    "Dataset",
    "ParquetDataset",
    "DataCatalog",
    "StaticCatalog",
]
