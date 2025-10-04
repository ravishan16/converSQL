# Dataset Plugin Skeleton

This example shows how to add a new dataset with an ontology.

- Implement a `DataCatalog` that returns your active dataset.
- Provide an ontology registry describing your domain fields.
- Provide a schema builder that returns a DuckDB-compatible CREATE TABLE context string for AI prompts.

See the code files for the minimal contracts.
