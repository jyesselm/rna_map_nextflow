# Repository Refactoring Plan

## Overview

This document outlines the plan to refactor the repository structure to match the standard Nextflow project layout while maintaining all functionality and leaving the `optimization/` directory untouched.

## Target Structure

```
rna_map_netflow/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # GitHub Actions CI/CD
│       └── docker-build.yml       # Container building
├── bin/                           # Executable scripts
│   ├── validate_nextflow.sh
│   └── build_singularity.sh
├── conf/                          # Configuration files (already correct)
│   ├── base.config
│   ├── local.config
│   ├── slurm.config
│   └── ...
├── containers/                    # Container definitions
│   ├── Dockerfile                 # Move from docker/
│   └── Singularity.def           # Create from build_singularity.sh
├── docs/                          # Documentation (already correct)
├── lib/                           # Nextflow library files (create if needed)
├── modules/                       # Nextflow DSL2 modules (already correct)
│   ├── bowtie2_align.nf
│   └── ...
├── python/                        # Python package
│   ├── src/
│   │   └── rna_map/              # Move from src/rna_map/
│   │       ├── __init__.py
│   │       └── ...
│   ├── tests/                     # Move from test/ (Python tests)
│   │   ├── __init__.py
│   │   ├── test_bit_vector.py
│   │   ├── test_cigar_parsing.py
│   │   ├── conftest.py
│   │   └── data/                  # Test data
│   ├── setup.py                   # Move from src/rna_map/
│   ├── pyproject.toml            # Move from src/rna_map/
│   └── requirements.txt          # Extract from environment.yml
├── cpp/                           # C++ code
│   ├── src/                       # Move from src/cpp/src/
│   │   └── ...
│   ├── include/                   # Move from src/cpp/include/
│   │   └── ...
│   ├── tests/                     # Move from src/cpp/tests/
│   │   └── ...
│   ├── CMakeLists.txt            # Move from src/cpp/
│   ├── setup.py                   # Move from src/cpp/
│   └── build.sh                   # Move from src/cpp/
├── test/                          # Pipeline tests
│   ├── data/                      # Move from test/resources/
│   ├── expected/                  # Create for expected outputs
│   └── integration/               # Move Nextflow tests from test/nextflow/
├── workflows/                     # Main workflow files (already correct)
│   ├── mapping.nf
│   └── parallel_mapping.nf
├── main.nf                        # Entry point (already correct)
├── nextflow.config                # Main configuration (already correct)
├── nextflow_schema.json           # Create if needed
├── environment.yml                # Conda environment (already correct)
├── .gitignore
├── LICENSE
└── README.md
```

## Current to Target Mapping

### Files/Directories to Move

1. **Container files**
   - `docker/Dockerfile` → `containers/Dockerfile`
   - `scripts/build_singularity.sh` → `containers/Singularity.def` (convert script to def file)

2. **Python package**
   - `src/rna_map/` → `python/src/rna_map/`
   - `src/rna_map/pyproject.toml` → `python/pyproject.toml`
   - `src/rna_map/setup.py` → `python/setup.py` (if exists, or create)
   - Python test files from `test/` → `python/tests/`
   - `test/resources/` → `python/tests/data/` (for Python tests)

3. **C++ code**
   - `src/cpp/` → `cpp/` (entire directory)
   - Keep structure: `src/`, `include/`, `tests/`, `CMakeLists.txt`, `setup.py`, `build.sh`

4. **Executable scripts**
   - `scripts/validate_nextflow.sh` → `bin/validate_nextflow.sh`
   - `scripts/build_singularity.sh` → `bin/build_singularity.sh` (keep as script, also create .def)

5. **Test reorganization**
   - `test/nextflow/` → `test/integration/`
   - `test/resources/` → `test/data/` (for pipeline tests)
   - Create `test/expected/` for expected outputs

6. **Scripts to evaluate**
   - `scripts/analyze_top_parameters.py` → Keep in `scripts/` or move to `python/scripts/`?
   - `scripts/build_cli_opts.py` → Move to `python/scripts/` (build tool)
   - `scripts/build_schema.py` → Move to `python/scripts/` (build tool)

### Files/Directories to Keep As-Is

- `conf/` - Already correct
- `docs/` - Already correct
- `modules/` - Already correct
- `workflows/` - Already correct
- `main.nf` - Already correct
- `nextflow.config` - Already correct
- `environment.yml` - Already correct
- `optimization/` - **Leave completely untouched**
- `README.md` - Update paths after refactoring
- `.gitignore` - Update paths after refactoring

### Files to Create

1. `python/requirements.txt` - Extract Python dependencies
2. `python/setup.py` - If doesn't exist, create from pyproject.toml
3. `containers/Singularity.def` - Convert from build script
4. `test/expected/` - Directory for expected test outputs
5. `.github/workflows/ci.yml` - If doesn't exist
6. `.github/workflows/docker-build.yml` - If doesn't exist
7. `nextflow_schema.json` - Parameter schema (if needed)

## Step-by-Step Refactoring Plan

### Phase 1: Preparation (No file moves)

1. **Create backup branch**
   ```bash
   git checkout -b refactoring-backup
   git push origin refactoring-backup
   git checkout main
   git checkout -b refactor/repository-structure
   ```

2. **Update .gitignore**
   - Add new paths: `python/__pycache__/`, `cpp/build/`, etc.
   - Remove old paths if needed

3. **Create new directories**
   ```bash
   mkdir -p bin containers lib python/src python/tests python/tests/data
   mkdir -p cpp/src cpp/include cpp/tests
   mkdir -p test/data test/expected test/integration
   mkdir -p .github/workflows
   ```

### Phase 2: Move Container Files

1. Move Dockerfile
   ```bash
   git mv docker/Dockerfile containers/Dockerfile
   ```

2. Convert Singularity build script to .def file
   - Read `scripts/build_singularity.sh`
   - Create `containers/Singularity.def` with proper format
   - Keep `bin/build_singularity.sh` as utility script

3. Update references
   - Search for `docker/Dockerfile` references
   - Update to `containers/Dockerfile`

### Phase 3: Move Python Package

1. Move Python source
   ```bash
   git mv src/rna_map python/src/rna_map
   ```

2. Move Python package files
   ```bash
   # Move pyproject.toml and setup.py if at root of rna_map
   git mv python/src/rna_map/pyproject.toml python/pyproject.toml
   # Create python/setup.py if needed
   ```

3. Move Python tests
   ```bash
   # Identify Python test files
   git mv test/test_*.py python/tests/
   git mv test/conftest.py python/tests/  # if exists
   ```

4. Move test data for Python tests
   ```bash
   # Move minimal test data needed for Python unit tests
   # Keep larger datasets in test/data/ for pipeline tests
   ```

5. Create requirements.txt
   ```bash
   # Extract from environment.yml or pyproject.toml
   ```

6. Update Python imports
   - Search for `from src.rna_map` or `import src.rna_map`
   - Update to `from rna_map` or `import rna_map`
   - Update test imports

### Phase 4: Move C++ Code

1. Move C++ directory
   ```bash
   git mv src/cpp cpp
   ```

2. Update paths in C++ build files
   - Update `CMakeLists.txt` paths if needed
   - Update `setup.py` paths if needed
   - Update `build.sh` paths if needed

3. Update Python bindings
   - Check `python/src/rna_map/pipeline/` for C++ binding references
   - Update paths to `cpp/` directory

### Phase 5: Move Executable Scripts

1. Move scripts to bin/
   ```bash
   git mv scripts/validate_nextflow.sh bin/validate_nextflow.sh
   git mv scripts/build_singularity.sh bin/build_singularity.sh
   ```

2. Make scripts executable
   ```bash
   chmod +x bin/*.sh
   ```

3. Move build scripts to python/scripts/
   ```bash
   mkdir -p python/scripts
   git mv scripts/build_cli_opts.py python/scripts/
   git mv scripts/build_schema.py python/scripts/
   git mv scripts/analyze_top_parameters.py python/scripts/
   ```

### Phase 6: Reorganize Tests

1. Move Nextflow integration tests
   ```bash
   git mv test/nextflow test/integration
   ```

2. Move test resources
   ```bash
   git mv test/resources test/data
   ```

3. Create expected outputs directory
   ```bash
   mkdir -p test/expected
   # Move or copy expected outputs if they exist
   ```

4. Keep Python tests in python/tests/ (already moved in Phase 3)

### Phase 7: Update Configuration Files

1. Update nextflow.config
   - Update any hardcoded paths
   - Update module paths if needed
   - Update container paths

2. Update main.nf
   - Update any hardcoded paths
   - Update module includes if needed

3. Update conf/*.config files
   - Update container paths
   - Update any script paths

### Phase 8: Update Documentation

1. Update README.md
   - Update installation paths
   - Update example commands
   - Update directory structure diagram

2. Update docs/
   - Update paths in all documentation files
   - Update setup instructions
   - Update testing instructions

3. Create/update .github/workflows/
   - Update CI/CD paths
   - Update container build paths

### Phase 9: Update Import Statements

1. Python imports
   ```bash
   # Find all Python files
   find . -name "*.py" -not -path "./optimization/*" -not -path "./.git/*" | \
     xargs grep -l "from src.rna_map\|import src.rna_map"
   # Update to: from rna_map or import rna_map
   ```

2. Nextflow includes
   ```bash
   # Find all Nextflow files
   find . -name "*.nf" -not -path "./optimization/*" | \
     xargs grep -l "docker/\|src/\|scripts/"
   # Update paths
   ```

3. Shell scripts
   ```bash
   # Update paths in .sh files
   find . -name "*.sh" -not -path "./optimization/*" | \
     xargs grep -l "src/\|scripts/"
   ```

### Phase 10: Testing

1. **Python package tests**
   ```bash
   cd python
   pip install -e .
   pytest tests/ -v
   ```

2. **C++ build and tests**
   ```bash
   cd cpp
   ./build.sh
   # Run C++ tests if available
   ```

3. **Nextflow linting**
   ```bash
   ./bin/validate_nextflow.sh
   nextflow run main.nf --help
   ```

4. **Integration tests**
   ```bash
   # Run test/integration/ tests
   cd test/integration
   # Run test scripts
   ```

5. **Full pipeline test**
   ```bash
   nextflow run main.nf \
     -profile local \
     --fasta test/data/small_test.fasta \
     --fastq1 test/data/small_test_R1.fastq \
     --fastq2 test/data/small_test_R2.fastq \
     --output_dir test_output
   ```

### Phase 11: Cleanup

1. Remove old directories (if empty)
   ```bash
   rmdir docker/  # if empty
   rmdir scripts/  # if empty
   rmdir src/     # if empty
   ```

2. Remove __pycache__ and build artifacts
   ```bash
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -type d -name "*.egg-info" -exec rm -r {} +
   find . -name "*.pyc" -delete
   find . -name "*.so" -not -path "./cpp/build/*" -delete
   ```

3. Update .gitignore
   - Ensure all new paths are covered

### Phase 12: Commit Strategy

1. **Commit in logical groups**
   ```bash
   # Phase 2: Containers
   git add containers/
   git commit -m "refactor: move container files to containers/ directory"

   # Phase 3: Python
   git add python/
   git commit -m "refactor: move Python package to python/ directory"

   # Phase 4: C++
   git add cpp/
   git commit -m "refactor: move C++ code to cpp/ directory"

   # Phase 5: Scripts
   git add bin/ python/scripts/
   git commit -m "refactor: move executable scripts to bin/ and build scripts to python/scripts/"

   # Phase 6: Tests
   git add test/
   git commit -m "refactor: reorganize test directory structure"

   # Phase 7-9: Configuration and imports
   git add nextflow.config main.nf conf/ workflows/ modules/
   git commit -m "refactor: update configuration and import paths"

   # Phase 10: Documentation
   git add README.md docs/ .github/
   git commit -m "refactor: update documentation and CI/CD paths"

   # Phase 11: Cleanup
   git add .gitignore
   git commit -m "refactor: update .gitignore for new structure"
   ```

2. **Final commit message**
   ```bash
   git commit --allow-empty -m "refactor: complete repository structure reorganization

   - Moved container files to containers/
   - Moved Python package to python/
   - Moved C++ code to cpp/
   - Reorganized test structure
   - Updated all paths and imports
   - Left optimization/ directory untouched"
   ```

## Testing Checklist

### Pre-Refactoring Tests (Baseline)

- [ ] Run all Python tests: `pytest test/ -v`
- [ ] Build C++ code: `cd src/cpp && ./build.sh`
- [ ] Run Nextflow validation: `./scripts/validate_nextflow.sh`
- [ ] Run small pipeline test: `nextflow run main.nf -profile local --fasta ...`
- [ ] Check all imports work

### Post-Refactoring Tests

- [ ] Python package installs: `cd python && pip install -e .`
- [ ] Python tests pass: `cd python && pytest tests/ -v`
- [ ] C++ builds: `cd cpp && ./build.sh`
- [ ] C++ tests pass (if available)
- [ ] Nextflow validation: `./bin/validate_nextflow.sh`
- [ ] Nextflow help works: `nextflow run main.nf --help`
- [ ] Small pipeline test: `nextflow run main.nf -profile local ...`
- [ ] Integration tests pass: `cd test/integration && ./test_*.sh`
- [ ] All imports resolve correctly
- [ ] Documentation paths are correct
- [ ] CI/CD would pass (check workflow files)

## Risk Mitigation

1. **Backup branch**: Created before starting
2. **Incremental commits**: Commit after each phase
3. **Test after each phase**: Don't move to next phase until tests pass
4. **Keep optimization/ untouched**: Explicitly exclude from all operations
5. **Path updates**: Use `git mv` to preserve history
6. **Import updates**: Search and replace systematically

## Rollback Plan

If something goes wrong:

```bash
git checkout main
git branch -D refactor/repository-structure
# Start over or fix issues
```

## Notes

- Use `git mv` instead of `mv` to preserve file history
- Test after each major phase
- Update paths incrementally
- Keep optimization/ directory completely untouched
- Document any path changes in commit messages

