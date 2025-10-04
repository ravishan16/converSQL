# Architecture v2: Modular Layout

This document describes the new, modular structure introduced to make datasets and ontologies swappable while keeping AI providers pluggable.

## Package map

- conversql/
  - ai/: AI service facade and prompts
  - data/: Dataset catalog abstractions (pluggable)
  - ontology/: Ontology registry and schema builders
  - exec/: Execution engines (DuckDB)
- src/: Legacy modules kept for compatibility in this branch and during migration

## Extension points

- DataCatalog: point to a local or remote dataset (e.g., Parquet directory)
- Ontology: provide domain metadata and portfolio context
- Schema builder: generate AI-friendly schema strings used by prompts
- AI adapters: unchanged (Claude, Bedrock, Gemini)

## Migration strategy

1. Keep existing `src/` modules intact until tests are updated.
2. Move imports in Streamlit UI from `src.*` to `conversql.*` gradually.
3. Provide shims in `conversql` that delegate to legacy `src` to avoid breakage.
4. When stable, retire the shims and update tests accordingly.

### Visualization module deprecation

- The legacy `src/visualizations.py` (heavy UI with many chart types) has been deprecated in favor of a minimal, resilient layer in `src/visualization.py`.
- All UI should import `render_visualization` from `src.visualization`.
- The old module now raises an ImportError to prevent accidental use and is excluded from coverage.

## Data/ontology swapping

Use `examples/dataset_plugin_skeleton/` as a starting point.

- Implement a DataCatalog and Ontology
- Build schema from your data source
- Wire into the app (future PR will add config flags)