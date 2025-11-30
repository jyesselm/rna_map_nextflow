# Repository Cleanup - Quick Summary

## Current State

### Root Directory Issues
- **12 markdown files** cluttering root
- Multiple obsolete cleanup docs
- Duplicate validation/warning docs
- Old test outputs and reports

### Directory Issues  
- **`nextflow/` directory** - Entirely obsolete (already migrated)
  - Contains duplicate modules
  - Old test outputs
  - Obsolete README and configs

### README Proliferation
- **7 README files** across repo
- Some contain duplicate/overlapping info
- Hard to know which to read

### Documentation Scattered
- 70+ markdown files total
- Archive with 20+ historical files
- Multiple guides for same topics

## Cleanup Actions

### DELETE (~30-40 files)
1. Entire `nextflow/` directory
2. Obsolete cleanup docs (CLEANUP_PLAN.md, CLEANUP_SUMMARY.md, etc.)
3. One-time validation docs (WARNINGS_*.md, NEXTFLOW_VALIDATION_RESULTS.md)
4. Test output directories
5. Old reports and trace files

### MOVE (~5-8 files)
1. QUICKSTART.md → docs/
2. SETUP_NEXTFLOW_LINTING.md → docs/ (merge into SETUP.md)
3. CLEAR_IDE_CACHE.md → docs/ (merge into SETUP.md)
4. validate_nextflow.sh → scripts/ or delete

### CONSOLIDATE
1. **README files**: 7 → 4 (keep only essential ones)
2. **Setup guides**: 3 files → 1 docs/SETUP.md
3. **Root docs**: 12 → 0 (all moved to docs/)

## Expected Results

### Before Cleanup
```
Root: 12 .md files
nextflow/: Entire obsolete directory
README files: 7 scattered around
Docs: 70+ files, hard to navigate
```

### After Cleanup  
```
Root: 1 README.md + essential configs only
nextflow/: DELETED
README files: 4 (1 root + 3 specialized)
Docs: Organized, ~50 files, clear structure
```

## Impact

✅ **Cleaner root directory** - Only essential files
✅ **No duplicates** - Removed duplicate modules/docs
✅ **Better navigation** - Consolidated READMEs and docs
✅ **Smaller repo** - ~30% reduction in files
✅ **Easier maintenance** - Clear structure

## Next Steps

See REPO_CLEANUP_PLAN.md for detailed implementation steps.
