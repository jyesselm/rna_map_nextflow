# Cluster Execution Improvements

This document summarizes improvements made to the RNA MAP Nextflow workflow for better cluster execution.

## Key Improvements

### 1. Package Installation Instead of PYTHONPATH

**Problem**: Previously, the workflow relied on setting `PYTHONPATH` to make the `lib/` package available. This was error-prone and required manual configuration in every job script.

**Solution**: The Python package is now installed in editable mode (`pip install -e .`) before running processes. This ensures the `lib/` package is available system-wide without requiring PYTHONPATH.

**Changes Made**:
- Removed PYTHONPATH export from `modules/rna_map_bit_vectors.nf`
- Added automatic package installation to `beforeScript` in all SLURM profiles:
  - `conf/slurm.config`
  - `conf/slurm_local.config`
  - `conf/slurm_optimized.config`
  - `conf/slurm_hybrid.config`
- Updated test scripts (`test_cluster_job.sh`, `test_cluster_job_local.sh`) to install package
- Updated documentation to reflect package installation approach

**Benefits**:
- No manual PYTHONPATH configuration needed
- More reliable - package is installed in conda environment
- Easier debugging - package is available in all Python processes
- Consistent behavior across different execution environments

### 2. Automatic Package Installation

The `beforeScript` in all SLURM profiles now includes:

```groovy
beforeScript = '''
    # Install Python package in editable mode if not already installed
    if ! python -c "import lib" 2>/dev/null; then
        cd "${baseDir}" && pip install -e . --quiet || true
    fi
'''
```

This ensures:
- Package is installed automatically before each process runs
- Installation is skipped if package is already available (performance optimization)
- Works across all SLURM execution profiles

### 3. Updated Documentation

All documentation has been updated to reflect the package installation approach:

- `docs/CLUSTER_TESTING_GUIDE.md` - Updated setup instructions
- `docs/CLUSTER_TESTING_QUICKREF.md` - Updated quick reference
- Removed all PYTHONPATH references
- Added package installation steps to all examples

## Usage

### Before (Old Approach)
```bash
export PYTHONPATH="${PWD}/lib:${PYTHONPATH}"
nextflow run main.nf -profile slurm ...
```

### After (New Approach)
```bash
pip install -e .
nextflow run main.nf -profile slurm ...
```

**Note**: The package is automatically installed by Nextflow processes, but installing it manually ensures it's available for testing and debugging.

## Testing

To verify the package is installed correctly:

```bash
# Activate conda environment
conda activate rna-map-nextflow

# Install package
pip install -e .

# Verify installation
python -c "from lib.bit_vectors import generate_bit_vectors; print('✅ lib imports work')"
python -c "from lib.core.config import BitVectorConfig; print('✅ lib.core imports work')"
```

## Additional Recommendations

Based on cluster execution best practices, consider these additional improvements:

1. **Resource Monitoring**: Add resource usage tracking to identify bottlenecks
2. **Error Recovery**: Implement better retry logic for transient cluster failures
3. **Work Directory**: Use scratch space (`$SCRATCH`) for work directories to reduce I/O on shared filesystems
4. **Caching**: Enable Nextflow caching for faster reruns of completed processes
5. **Logging**: Centralize logging to a shared location for easier debugging

## Migration Notes

If you have existing job scripts that set PYTHONPATH, you can safely remove those lines. The package installation approach is backward compatible and will work with existing workflows.

## Troubleshooting

### Issue: "Module not found: lib"

**Solution**:
```bash
# Install the package
pip install -e .

# Verify installation
python -c "from lib.bit_vectors import generate_bit_vectors; print('OK')"
```

### Issue: Package installation fails

**Possible causes**:
- Not in project root directory
- Conda environment not activated
- Missing dependencies (check `environment.yml`)

**Solution**:
```bash
# Ensure you're in project root
cd /path/to/rna_map_nextflow

# Activate conda environment
conda activate rna-map-nextflow

# Install package
pip install -e .
```

