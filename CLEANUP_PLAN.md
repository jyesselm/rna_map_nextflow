# Repository Cleanup Plan

## Recommendation: Optimization Work Organization

**Decision: Keep optimization scripts in main repo, but archive results separately**

### Rationale:
- ✅ Optimization scripts (`optimize_bowtie2_params*.py`) are useful tools that users may want
- ✅ Documentation about optimization belongs with the workflow
- ❌ Large result directories (1000s of files) clutter the main repo
- ❌ Temporary analysis files should be archived

### Proposed Structure:
1. **Main Repo** (this one): Keep workflow + optimization scripts + consolidated docs
2. **Archive/Move**: Large optimization result directories to separate location or .gitignore them

## Cleanup Actions Taken

### 1. Files/Directories to Remove (test outputs & temporary files)
- `=` (accidental file)
- `test_output_*/` directories
- `case2_baseline_test_results/`
- `case2_optimization_test/`
- `case2_test_results/`
- `optimization_optuna_test/`
- `optimization_optuna_improved_test/`
- `optimization_score_test/`
- `test_new_params/`
- `full_optimization/` (large result directory - should be archived)
- `my_optimization/` (large result directory - should be archived)
- Build artifacts already in .gitignore but not cleaned

### 2. Documentation Consolidation
**Root-level docs to move to `docs/optimization/`:**
- `TOP_100_PARAMETER_ANALYSIS.md` → `docs/optimization/TOP_100_PARAMETER_ANALYSIS.md`
- `CASE2_TEST_RESULTS.md` → `docs/optimization/CASE2_TEST_RESULTS.md`
- `CASE2_BASELINE_VS_OPTIMIZED.md` → `docs/optimization/CASE2_BASELINE_VS_OPTIMIZED.md`
- `CASE2_OPTIMIZATION_COMMAND.md` → `docs/optimization/CASE2_OPTIMIZATION_COMMAND.md`
- `BEST_PARAMETERS.md` → `docs/optimization/BEST_PARAMETERS.md`
- `OPTIMIZATION_IMPROVEMENTS.md` → `docs/optimization/OPTIMIZATION_IMPROVEMENTS.md`
- `OPTUNA_ENV_SETUP.md` → `docs/optimization/OPTUNA_ENV_SETUP.md`
- `ORIGINAL_BASELINE_PARAMETERS.md` → `docs/optimization/ORIGINAL_BASELINE_PARAMETERS.md`
- `PARAMETER_COMPARISON.md` → `docs/optimization/PARAMETER_COMPARISON.md`
- `POTENTIAL_OPTIMIZATION_PARAMETERS.md` → `docs/optimization/POTENTIAL_OPTIMIZATION_PARAMETERS.md`
- `RUN_OPTIMIZATION.md` → `docs/optimization/RUN_OPTIMIZATION.md`
- `SCORE_FUNCTION_TYPES.md` → `docs/optimization/SCORE_FUNCTION_TYPES.md`
- `ADDED_PARAMETERS.md` → `docs/optimization/ADDED_PARAMETERS.md`

**Keep in root (user-facing):**
- `README.md`
- `QUICKSTART.md`
- `RESTRUCTURE_SUMMARY.md` (if still relevant)

**Remove (outdated/duplicate):**
- Check for duplicates in docs/ folder

### 3. Scripts & Data Files
**Keep:**
- `scripts/optimize_bowtie2_params.py`
- `scripts/optimize_bowtie2_params_optuna.py`
- `analyze_top_parameters.py` → move to `scripts/`

**Parameter files (consider moving to docs/optimization/recommended_params/):**
- `best_parameters.txt` → `docs/optimization/recommended_params/best_parameters.txt`
- `original_baseline_parameters.txt` → `docs/optimization/recommended_params/original_baseline_parameters.txt`

**Remove:**
- `test_baseline_params_case2.py` (if redundant)
- `test_best_params_case2.py` (if redundant)
- `test_optuna_env.py` (if redundant)
- `RUN_CASE2_OPTIMIZATION.sh` (move to docs if useful example)
- `setup_optuna_env.sh` (if redundant with environment files)

### 4. Update .gitignore
Add patterns for:
- `*_optimization/` (result directories)
- `*_test_results/`
- `case*_test_results/`
- `case*_optimization_test/`

### 5. Environment Files
- Keep `environment.yml` (main)
- Consider consolidating `environment_optuna.yml` or documenting it better

## Summary

**Recommendation: Create separate repo for optimization experiments?**
- **No** - Keep scripts here, but archive results
- Create `docs/optimization/` for all optimization-related documentation
- Add optimization result directories to .gitignore
- Users can run optimizations and results won't clutter the repo

**Alternative (if you prefer separation):**
- Create `rna-map-bowtie2-optimization` repo for all optimization work
- Keep only basic docs in main repo
- Move optimization scripts to separate repo

