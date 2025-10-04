"""converSQL core package.

Modular architecture for AI-driven SQL generation over pluggable datasets and ontologies.

Key modules:
- conversql.ai: AI service, adapters, and prompts
- conversql.data: dataset catalog and sources
- conversql.ontology: ontology registry and schema builders
- conversql.exec: execution engines (DuckDB)
"""

from importlib.metadata import version, PackageNotFoundError

__all__ = [
    "__version__",
]

try:
    __version__ = version("conversql")  # if installed as a package
except PackageNotFoundError:
    __version__ = "0.0.0+local"
