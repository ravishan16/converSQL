from typing import List

from conversql.ontology.schema import build_schema_context_from_parquet


def build_schema(files: List[str]) -> str:
    # You can customize this to your ontology
    return build_schema_context_from_parquet(files)
