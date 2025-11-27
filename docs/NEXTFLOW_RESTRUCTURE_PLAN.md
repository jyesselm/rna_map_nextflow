# Nextflow Package Restructure Plan

## Overview

This plan outlines the restructuring of the RNA MAP repository to conform to standard Nextflow package conventions and remove all unnecessary Python code. The goal is to create a clean, maintainable Nextflow-first package structure.

## Current State Analysis

### Python Code Actually Used by Nextflow

**Directly imported in Nextflow modules:**
1. `rna_map.pipeline.functions.generate_bit_vectors()` - Core bit vector generation
2. `rna_map.core.config.BitVectorConfig` - Configuration dataclass
3. `rna_map.analysis.statistics.merge_all_merge_mut_histo_dicts()` - Merge histograms
4. `rna_map.mutation_histogram.write_mut_histos_to_json_file()` - Write JSON output

**Dependencies of above (transitive):**
- `rna_map.pipeline.bit_vector_generator.BitVectorGenerator` - Used by `generate_bit_vectors()`
- `rna_map.core.bit_vector` - Core bit vector data structures
- `rna_map.core.aligned_read` - Aligned read data structures
- `rna_map.analysis.mutation_histogram.MutationHistogram` - Mutation histogram class
- `rna_map.io.sam` - SAM file parsing
- `rna_map.io.fasta` - FASTA file parsing
- `rna_map.io.csv` - CSV file parsing
- `rna_map.io.bit_vector` - Bit vector I/O
- `rna_map.io.bit_vector_storage` - Bit vector storage formats
- `rna_map.logger` - Logging utilities
- `rna_map.exception` - Exception classes

### Python Code NOT Used by Nextflow

**CLI and Wrapper Code (can be removed or moved to separate package):**
- `rna_map/cli/` - All CLI code (nextflow_wrapper.py, parser.py, pipeline.py, bowtie2.py)
- `rna_map/cli.py` - Main CLI entry point
- `rna_map/cli_opts.py` - CLI option definitions
- `rna_map/cli_pipeline.py` - Pipeline CLI
- `rna_map/parameters.py` - Parameter parsing (not used by Nextflow)

**External Command Wrappers (not needed - Nextflow handles this):**
- `rna_map/external/` - All external command wrappers
- `rna_map/external_cmd.py` - External command execution

**IO Validation (not used by Nextflow):**
- `rna_map/io/validation.py` - Input validation

**Visualization (not used by workflow):**
- `rna_map/visualization/` - All visualization code

**Tools (not used by workflow):**
- `rna_map/tools/` - Utility tools

**Unused Core Modules:**
- `rna_map/core/inputs.py` - Not used (Nextflow handles inputs)
- `rna_map/core/results.py` - Only BitVectorResult needed, rest can go
- `rna_map/bit_vector.py` - Duplicate of core/bit_vector.py?
- `rna_map/sam.py` - Duplicate of io/sam.py?

**Pipeline Code (not used):**
- `rna_map/pipeline/simple_pipeline.py` - Only demultiplexing, not used by Nextflow

**Other:**
- `rna_map/settings.py` - Settings management
- `rna_map/util.py` - Utility functions
- `rna_map/utils/` - Utility modules

## Target Structure (Standard Nextflow Package)

```
rna-map-nextflow/
├── README.md                    # Main documentation
├── LICENSE
├── nextflow.config              # Main Nextflow config
├── nextflow_schema.json         # Parameter schema (optional)
├── environment.yml              # Conda environment
├── .github/
│   └── workflows/               # CI/CD workflows
│
├── modules/                     # Reusable Nextflow processes
│   ├── fastqc.nf
│   ├── trim_galore.nf
│   ├── bowtie2_build.nf
│   ├── bowtie2_align.nf
│   ├── rna_map_bit_vectors.nf
│   ├── split_fastq.nf
│   ├── join_sam.nf
│   ├── join_mutation_histos.nf
│   └── join_bit_vectors.nf
│
├── workflows/                   # Subworkflows
│   ├── mapping.nf
│   └── parallel_mapping.nf
│
├── lib/                         # Minimal Python library (only what Nextflow needs)
│   ├── __init__.py
│   ├── bit_vectors.py           # generate_bit_vectors() function
│   ├── config.py                # BitVectorConfig
│   ├── statistics.py            # merge_all_merge_mut_histo_dicts()
│   ├── mutation_histogram.py   # write_mut_histos_to_json_file()
│   └── [minimal dependencies]   # Only what's needed
│
├── bin/                         # Helper scripts (optional)
│   └── setup_env.sh
│
├── conf/                        # Configuration profiles
│   ├── base.config
│   ├── local.config
│   └── slurm.config
│
├── docs/                        # Documentation
│   ├── README.md
│   ├── USAGE.md
│   └── CONFIGURATION.md
│
├── test/                        # Test data and scripts
│   ├── data/
│   └── test.sh
│
└── scripts/                     # Utility scripts
    └── validate_outputs.py
```

## Migration Steps

### Phase 1: Create Minimal Python Library

**Goal:** Extract only the Python code needed by Nextflow into a minimal `lib/` directory.

**Steps:**
1. Create `lib/` directory at root
2. Copy and refactor required modules:
   - `lib/bit_vectors.py` - Extract `generate_bit_vectors()` and dependencies
   - `lib/config.py` - Extract `BitVectorConfig` and dependencies
   - `lib/statistics.py` - Extract `merge_all_merge_mut_histo_dicts()` and dependencies
   - `lib/mutation_histogram.py` - Extract `write_mut_histos_to_json_file()` and dependencies
3. Minimize dependencies - only include what's absolutely necessary
4. Update Nextflow modules to import from `lib/` instead of `rna_map/`

**Files to extract:**
- `rna_map/pipeline/functions.py` → `lib/bit_vectors.py`
- `rna_map/core/config.py` → `lib/config.py`
- `rna_map/analysis/statistics.py` → `lib/statistics.py`
- `rna_map/mutation_histogram.py` → `lib/mutation_histogram.py`

**Dependencies to include:**
- Core data structures: `bit_vector.py`, `aligned_read.py`
- I/O modules: `sam.py`, `fasta.py`, `csv.py`, `bit_vector.py`, `bit_vector_storage.py`
- Analysis: `mutation_histogram.py` (class definition)
- Utilities: `logger.py`, `exception.py`

### Phase 2: Restructure Nextflow Directory

**Goal:** Move Nextflow files to standard locations and clean up structure.

**Steps:**
1. Move `nextflow/modules/` → `modules/`
2. Move `nextflow/workflows/` → `workflows/`
3. Move `nextflow/main.nf` → `main.nf` (root)
4. Move `nextflow/nextflow.config` → `nextflow.config` (root)
5. Move `nextflow/params.config` → `conf/base.config`
6. Create `conf/local.config` and `conf/slurm.config` profiles
7. Update all import paths in Nextflow files

### Phase 3: Remove Unused Python Code

**Goal:** Delete all Python code not needed by Nextflow.

**Files to DELETE:**
- `rna_map/cli/` - Entire directory
- `rna_map/cli.py`
- `rna_map/cli_opts.py`
- `rna_map/cli_pipeline.py`
- `rna_map/parameters.py`
- `rna_map/external/` - Entire directory
- `rna_map/external_cmd.py`
- `rna_map/io/validation.py`
- `rna_map/visualization/` - Entire directory
- `rna_map/tools/` - Entire directory
- `rna_map/core/inputs.py`
- `rna_map/core/results.py` (keep only BitVectorResult if needed)
- `rna_map/bit_vector.py` (if duplicate)
- `rna_map/sam.py` (if duplicate)
- `rna_map/pipeline/simple_pipeline.py`
- `rna_map/settings.py`
- `rna_map/util.py`
- `rna_map/utils/` - Entire directory

**Files to KEEP (minimal set):**
- `lib/` - New minimal library
- Core data structures needed by lib
- I/O modules needed by lib
- Logger and exception classes

### Phase 4: Update Configuration

**Goal:** Standardize Nextflow configuration.

**Steps:**
1. Create `nextflow_schema.json` for parameter validation
2. Split `nextflow.config` into base config + profiles
3. Move test scripts to `test/` directory
4. Update environment.yml to only include what's needed
5. Remove Python package installation from environment.yml (install lib/ separately)

### Phase 5: Update Documentation

**Goal:** Update all documentation to reflect new structure.

**Steps:**
1. Update main README.md for Nextflow-first approach
2. Create USAGE.md with Nextflow examples
3. Create CONFIGURATION.md for config options
4. Update migration guide
5. Remove CLI documentation (or move to separate doc)

### Phase 6: Update Tests

**Goal:** Ensure tests work with new structure.

**Steps:**
1. Move test scripts to `test/` directory
2. Update test scripts to use new paths
3. Update Python tests to test `lib/` modules
4. Remove tests for deleted code

### Phase 7: Clean Up Build System

**Goal:** Simplify build and installation.

**Steps:**
1. Remove `pyproject.toml` (or simplify for lib/ only)
2. Update `setup.py` or `pyproject.toml` to only install `lib/`
3. Remove entry points for CLI commands
4. Update installation instructions

## Detailed File Mapping

### Nextflow Files (Keep and Reorganize)

```
nextflow/main.nf                    → main.nf
nextflow/nextflow.config            → nextflow.config
nextflow/params.config              → conf/base.config
nextflow/modules/*.nf               → modules/*.nf
nextflow/workflows/*.nf             → workflows/*.nf
nextflow/environment.yml            → environment.yml
nextflow/test_*.sh                  → test/*.sh
```

### Python Files (Extract to lib/)

```
rna_map/pipeline/functions.py       → lib/bit_vectors.py
rna_map/core/config.py              → lib/config.py
rna_map/analysis/statistics.py      → lib/statistics.py
rna_map/mutation_histogram.py       → lib/mutation_histogram.py

# Dependencies (copy to lib/):
rna_map/pipeline/bit_vector_generator.py → lib/bit_vector_generator.py
rna_map/core/bit_vector.py              → lib/core/bit_vector.py
rna_map/core/aligned_read.py            → lib/core/aligned_read.py
rna_map/analysis/mutation_histogram.py   → lib/core/mutation_histogram.py
rna_map/io/sam.py                        → lib/io/sam.py
rna_map/io/fasta.py                      → lib/io/fasta.py
rna_map/io/csv.py                        → lib/io/csv.py
rna_map/io/bit_vector.py                 → lib/io/bit_vector.py
rna_map/io/bit_vector_storage.py        → lib/io/bit_vector_storage.py
rna_map/logger.py                        → lib/logger.py
rna_map/exception.py                     → lib/exception.py
```

### Files to Delete

```
rna_map/cli/                          # DELETE
rna_map/cli.py                        # DELETE
rna_map/cli_opts.py                   # DELETE
rna_map/cli_pipeline.py               # DELETE
rna_map/parameters.py                 # DELETE
rna_map/external/                     # DELETE
rna_map/external_cmd.py                # DELETE
rna_map/io/validation.py               # DELETE
rna_map/visualization/                 # DELETE
rna_map/tools/                         # DELETE
rna_map/core/inputs.py                 # DELETE
rna_map/core/results.py                # DELETE (or keep minimal)
rna_map/pipeline/simple_pipeline.py    # DELETE
rna_map/settings.py                    # DELETE
rna_map/util.py                        # DELETE
rna_map/utils/                         # DELETE
```

## Implementation Order

1. **Phase 1** - Create minimal lib/ (can test independently)
2. **Phase 2** - Restructure Nextflow (update imports)
3. **Phase 3** - Delete unused code (after lib/ works)
4. **Phase 4** - Update configuration
5. **Phase 5** - Update documentation
6. **Phase 6** - Update tests
7. **Phase 7** - Clean up build system

## Benefits

1. **Standard Nextflow Structure** - Follows Nextflow best practices
2. **Minimal Dependencies** - Only Python code needed by workflow
3. **Easier Maintenance** - Clear separation of concerns
4. **Better Performance** - Smaller package, faster installation
5. **Clearer Purpose** - Nextflow-first, Python as library only

## Risks and Mitigation

**Risk:** Breaking existing workflows
- **Mitigation:** Keep old structure in a branch, test thoroughly

**Risk:** Missing dependencies
- **Mitigation:** Trace all imports carefully, test each module

**Risk:** Users relying on CLI
- **Mitigation:** Document migration path, provide wrapper script if needed

## Success Criteria

- [ ] Nextflow workflow runs with minimal Python library
- [ ] All tests pass
- [ ] Package size reduced by >50%
- [ ] Documentation updated
- [ ] No broken imports or missing dependencies
- [ ] Standard Nextflow package structure achieved

