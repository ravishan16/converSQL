# Repository Inventory

**Generated:** 2024-10-04  
**Purpose:** Document potentially unused files, large notebooks, and items for cleanup consideration

---

## Summary

This inventory identifies files that may be candidates for removal, archiving, or relocation based on static analysis and repository structure review.

### Statistics
- Total Python files: 44
- Total test files: ~20
- Documentation files: 12
- Notebooks: 2

---

## Actions Taken

### ✅ Moved to Archive
- `notebooks/pipeline_csv_to_parquet multifile.ipynb` → `notebooks/experiments/`
  - **Reason:** Large experimental notebook (36KB) not referenced in main pipeline
  - **Status:** Preserved in experiments directory for historical reference
  - **Action:** MOVED (not deleted)

---

## Files Under Review

### Configuration Files - Potential Consolidation

#### `.replit`
- **Size:** 714 bytes
- **Purpose:** Replit IDE configuration
- **Recommendation:** Keep if using Replit; consider adding to `.gitignore` if not needed in version control
- **Risk:** Low - IDE-specific configuration
- **Action:** REVIEW

#### `pyproject.toml` + `setup.cfg`
- **Purpose:** Both contain tool configuration (Black, isort, mypy, flake8)
- **Observation:** Configuration is split between two files
- **Recommendation:** Consider consolidating all tool config into `pyproject.toml` (modern standard)
- **Action:** CONSOLIDATE (optional optimization)

---

## Notebooks

### Active Notebooks
- `notebooks/pipeline_csv_to_parquet.ipynb` (24KB)
  - **Status:** Active, referenced in documentation
  - **Action:** KEEP

### Archived Notebooks
- `notebooks/experiments/pipeline_csv_to_parquet multifile.ipynb` (36KB)
  - **Status:** Experimental, preserved for reference
  - **Action:** ARCHIVED

---

## Documentation Assessment

All documentation files appear active and well-maintained:
- ✅ `docs/ARCHITECTURE.md` (20KB) - Core architecture documentation
- ✅ `docs/AI_ENGINES.md` (24KB) - AI adapter documentation
- ✅ `docs/DATA_PIPELINE.md` (19KB) - Data pipeline documentation
- ✅ `docs/VISUALIZATION.md` (17KB) - Visualization documentation
- ✅ Other docs: All appear referenced and active

**Observation:** `docs/ARCHITECTURE_V2.md` (1.7KB) is notably smaller than `ARCHITECTURE.md` (20KB)
- **Recommendation:** Verify if V2 is intended to replace or supplement ARCHITECTURE.md
- **Action:** REVIEW DOCUMENTATION STRATEGY

---

## Code Quality Notes

### Ignored Files in Coverage/Linting
The following file is explicitly excluded from coverage and linting:
- `src/ai_service_old.py`
  - **Status:** Listed in `.gitignore`, `pyproject.toml`, and `setup.cfg`
  - **Issue:** File reference exists but file not found in repository
  - **Recommendation:** Remove references from config files since file doesn't exist
  - **Action:** CLEANUP CONFIG

---

## Testing Infrastructure

### Test Structure
- Unit tests: `tests/unit/` - Well organized with 49 passing tests
- Integration tests: `tests/integration/` - Properly separated
- New smoke test: `tests/test_smoke_app.py` - Added for basic import validation

### Coverage
Current coverage is 75% for base adapter, with lower coverage for AI adapters (expected for integration code).

---

## Recommendations

### High Priority
1. ✅ **COMPLETED:** Move `pipeline_csv_to_parquet multifile.ipynb` to experiments
2. ✅ **COMPLETED:** Add smoke test for app initialization
3. **TODO:** Remove references to `src/ai_service_old.py` from config files

### Medium Priority
1. **Consider:** Consolidate tool configuration into `pyproject.toml` only
2. **Review:** Clarify relationship between `ARCHITECTURE.md` and `ARCHITECTURE_V2.md`
3. **Consider:** Add `.replit` to `.gitignore` if not needed in version control

### Low Priority
1. **Monitor:** Track unused code with regular `vulture` runs (tool added in `scripts/report_unused.sh`)
2. **Consider:** Create `notebooks/README.md` to document purpose of each notebook

---

## Future Cleanup Strategy

The `scripts/report_unused.sh` script has been added to help identify:
- Unused Python functions and classes (via vulture)
- Code with zero coverage (via pytest-cov)
- Import patterns that may indicate dead code

Run periodically with:
```bash
bash scripts/report_unused.sh
```

---

## Risk Assessment

**Overall Risk:** LOW
- All changes are non-destructive
- Experimental notebook preserved (moved, not deleted)
- No production code removed
- Smoke test added for safety

**Rollback:** Simple - revert the branch; all moved files can be restored from git history.

---

## Notes

This inventory is a living document. As the codebase evolves:
1. Run `scripts/report_unused.sh` periodically
2. Update this inventory when making structural changes
3. Review archived notebooks annually for potential deletion
4. Keep test coverage high to identify truly unused code
