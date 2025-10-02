# converSQL Copilot Guide

## System map
- `app.py` is the Streamlit shell: it hydrates cached data via `initialize_app_data()`, gates the UI through `simple_auth_wrapper`, and delegates all heavy work to `src/core.py` and `src/ai_service.py`.
- `src/core.py` owns DuckDB execution and orchestrates data prep. `scan_parquet_files()` will run `scripts/sync_data.py` if `data/processed/*.parquet` are missing, so keep a local Parquet copy handy during tests to avoid network pulls.
- `src/ai_service.py` routes natural-language prompts into adapter implementations in `src/ai_engines/`. The prompt embeds the mortgage risk heuristics baked into `src/data_dictionary.py`; reuse `AIService._build_sql_prompt()` instead of crafting ad-hoc prompts.

## Data + ontology expectations
- Loan metadata lives in `data/processed/data.parquet`; schema text comes from `generate_enhanced_schema_context()` which stitches DuckDB types with ontology metadata from `src/data_dictionary.py` and `docs/DATA_DICTIONARY.md`.
- When adding derived features, update both the Parquet schema and the ontology entry so AI output and the Ontology Explorer tab stay in sync.
- The Streamlit Ontology tab imports `LOAN_ONTOLOGY` and `PORTFOLIO_CONTEXT`; breaking their shape (dict → FieldMetadata) will crash the UI.

## AI engine adapters
- Adapters must subclass `AIEngineAdapter` in `src/ai_engines/base.py`, expose `provider_id`, `name`, `is_available()`, and `generate_sql()`, then be exported via `src/ai_engines/__init__.py` and registered inside `AIService.adapters`.
- Use `clean_sql_response()` to strip markdown fences, and return `(sql, "")` on success; downstream callers treat any non-empty error string as failure.
- Keep `AI_PROVIDER` fallbacks working—tests rely on `AIService` surviving with zero credentials, so default to "unavailable" rather than raising.

## Developer workflows
- Install deps with `pip install -r requirements.txt`; prefer `make setup` for a clean environment (installs + cleanup).
- Fast test cycle: `make test-unit` skips integration markers; `make test` mirrors CI (pytest + coverage). Integration adapters are ignored by default via `pytest.ini`; remove the `--ignore` flags there if you really need live API coverage.
- Lint/format stack is Black 120 cols + isort + flake8 + mypy. `make ci` runs the whole suite and matches the GitHub Actions workflow.

## Environment & secrets
- Copy `.env.example` to `.env`, then set one provider block (`CLAUDE_API_KEY`, `AWS_*`, or `GEMINI_API_KEY`). Without credentials the UI drops to “AI unavailable” but manual SQL still works.
- Data sync needs Cloudflare R2 keys (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`). In offline dev, set `FORCE_DATA_REFRESH=false` and place Parquet files under `data/processed/`.
- Authentication defaults to Google OAuth (`ENABLE_AUTH=true`); set it to `false` for local hacking or provide `GOOGLE_CLIENT_ID/SECRET` plus HTTPS when deploying.

## Practical tips
- Clear Streamlit caches with `streamlit cache clear` if schema or ontology changes; otherwise stale `@st.cache_data` results linger.
- When writing new ingest code, mirror the type-casting helpers in `notebooks/pipeline_csv_to_parquet*.ipynb` so DuckDB types stay compatible.
- Logging to Cloudflare D1 is optional—`src/d1_logger.py` silently no-ops without `CLOUDFLARE_*` secrets, so you can call it safely even in tests.
