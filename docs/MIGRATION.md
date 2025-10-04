# Migration Guide

This guide explains how to transition from the legacy `src/` layout to the new modular `conversql/` package.

## Goals
- Keep app and tests running during the transition
- Enable dataset/ontology swapping without touching app code
- Maintain adapter-based AI providers

## Steps

1. Keep `app.py` imports unchanged initially; the `conversql` package shims call into `src`.
2. For new features, prefer importing from `conversql.*` modules.
3. Update individual modules gradually:
   - `src/core.execute_sql_query` -> `conversql.exec.duck.run_query`
   - Schema context building -> `conversql.ontology.schema.build_schema_context_from_parquet`
   - AI service -> `conversql.ai.AIService`
4. Once all imports are updated and tests pass, we can remove the legacy `src` modules or keep them as thin wrappers.

## Plugins

See `examples/dataset_plugin_skeleton/` for a minimal DataCatalog and Ontology example.
