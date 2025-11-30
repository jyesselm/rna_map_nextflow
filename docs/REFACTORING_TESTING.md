# Refactoring Testing Guide

## Quick Verification Tests

### 1. Python Package Structure ✅
```bash
cd python
ls -la src/rna_map/  # Should show package structure
ls -la tests/        # Should show test files
cat pyproject.toml   # Should have package-dir = {"" = "src"}
```

### 2. Python Package Installation Test
```bash
cd python
pip install -e .
python -c "from rna_map import __version__; print('✅ Package installed')"
```

### 3. Python Tests (if pytest available)
```bash
cd python
pytest tests/ -v --tb=short
```

### 4. C++ Structure Check
```bash
ls -la cpp/          # Should show src/, include/, tests/, CMakeLists.txt, etc.
```

### 5. C++ Build Test (if CMake available)
```bash
cd cpp
./build.sh  # or check if CMakeLists.txt exists
```

### 6. Nextflow Validation
```bash
./bin/validate_nextflow.sh
```

### 7. Nextflow Help (if Nextflow installed)
```bash
nextflow run main.nf --help
```

### 8. Check All Paths Updated
```bash
# Should return no results (all paths updated)
grep -r "src/rna_map\|src/cpp\|docker/\|scripts/" --include="*.nf" --include="*.sh" --include="*.md" . | grep -v "optimization/" | grep -v "REFACTORING" | grep -v ".git"
```

### 9. Directory Structure Verification
```bash
# Should show new structure
tree -L 2 -d -I '__pycache__|*.egg-info|build|.git' | head -30
```

## Known Issues

1. **C++ files**: Some C++ files may not be tracked by git (build artifacts, .so files)
   - This is expected - they're in .gitignore
   - The source files should be tracked

2. **Old directories**: `docker/`, `scripts/`, `src/` may still exist with untracked files
   - Safe to remove if empty or only contain cache files
   - Check with: `ls -la docker/ scripts/ src/`

3. **Python imports**: All should use `from rna_map` not `from src.rna_map`
   - Verified: ✅ All imports are correct

## Next Steps After Testing

1. If all tests pass, merge to main:
   ```bash
   git checkout main
   git merge refactor/repository-structure
   git push origin main
   ```

2. If issues found, fix on `refactor/repository-structure` branch and test again

3. Update CI/CD workflows if they reference old paths

