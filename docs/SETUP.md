# Setup Guide

Complete setup guide for RNA MAP Nextflow workflow including environment setup, IDE configuration, and linting.

## Environment Setup

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/jyesselm/rna_map_nextflow
cd rna_map_nextflow

# 2. Create conda environment
conda env create -f environment.yml
conda activate rna-map-nextflow

# 3. Install Python package (required!)
# This installs the package in editable mode so it's available without PYTHONPATH
cd python && pip install -e . && cd ..
```

### Verify Installation

```bash
# Check Nextflow
nextflow -version
# Should show: version 25.10.2+

# Check Java
java -version
# Should show: Java 17+ (required for Nextflow 25.x)

# Check Python package
python -c "import rna_map; print(rna_map.__version__)"
```

## IDE Setup (Cursor/VS Code)

### Install Nextflow IDE Extension

1. Open Extensions in Cursor:
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
   - Or click the Extensions icon in the sidebar

2. Search for "Nextflow IDE" or "nextflow.nextflow-ide"

3. Install the extension by nextflow

### Configuration

The `.vscode/settings.json` file is already configured with:
- Nextflow server path pointing to conda environment
- Java home configured
- File associations for `.nf` files

### Reload Window

After installing the extension:
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Developer: Reload Window"
3. Press Enter

The Nextflow language server should now start.

### Troubleshooting IDE Issues

#### Stale Linter Warnings

If you see warnings in the IDE but command-line linting shows no errors:

1. **Reload Window** (easiest):
   - `Cmd+Shift+P` → "Developer: Reload Window"

2. **Restart Language Server**:
   - `Cmd+Shift+P` → "Nextflow: Restart Language Server"

3. **Clear Cache** (if needed):
   - Close Cursor completely
   - Delete cache: `rm -rf ~/Library/Application\ Support/Cursor/CachedExtensions/*`
   - Restart Cursor

#### Verify Setup

Check the Output panel:
- View → Output (or `Cmd+Shift+U`)
- Select "Nextflow Language Server" from dropdown
- Look for "Language server started" messages

## Linting and Code Quality

### Nextflow Linting

This project uses Nextflow 25.10.2+ which includes built-in linting:

```bash
# Lint single file
conda activate rna-map-nextflow
nextflow lint main.nf

# Lint all files
nextflow lint .
```

All files should pass with zero warnings.

### Validation Script

Use the validation script for comprehensive checks:

```bash
./validate_nextflow.sh
```

This checks:
- Nextflow version compatibility
- Syntax validation
- Module structure
- Workflow structure

## Requirements

### System Requirements

- **Python**: 3.10+
- **Nextflow**: 25.04+ (25.10.2 recommended)
- **Java**: 17-24 (required for Nextflow 25.x)
- **Conda/Mamba**: For environment management

### Included in Environment

- Nextflow (25.10.2)
- Java (17)
- Bowtie2
- FastQC
- Trim Galore / Cutadapt
- Python dependencies

## Quick Start

After setup, see **[QUICKSTART.md](./QUICKSTART.md)** for usage examples.

## Additional Resources

- **[docs/NEXTFLOW_LINTING.md](./NEXTFLOW_LINTING.md)** - Detailed linting documentation
- **[docs/CLUSTER_TESTING_GUIDE.md](./CLUSTER_TESTING_GUIDE.md)** - Cluster setup and testing
- **[.vscode/EXTENSIONS.md](../.vscode/EXTENSIONS.md)** - IDE extension details

