from dataclasses import dataclass
from pathlib import Path
from typing import List

from conversql.data.catalog import DataCatalog, Dataset, ParquetDataset, StaticCatalog


@dataclass
class MyDataset(ParquetDataset):
    pass


@dataclass
class MyCatalog(StaticCatalog):
    pass


def make_catalog(root: str) -> DataCatalog:
    return MyCatalog(dataset=MyDataset(root=Path(root)))
