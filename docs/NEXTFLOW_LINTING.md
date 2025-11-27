# Nextflow Linting & Code Quality Tools

## Overview

Several tools are available for linting, formatting, and analyzing Nextflow code quality. This document outlines the available tools and how to integrate them into the RNA MAP project.

## Available Tools

### 1. Nextflow Built-in Linting (Recommended)

**Version**: Nextflow 25.04+ includes built-in linting

**Features:**
- Syntax checking using strict parser
- Code formatting
- Error detection before runtime
- Integrated into Nextflow CLI

**Usage:**
```bash
# Lint workflow files
nextflow lint main.nf

# Lint all .nf files in directory
nextflow lint nextflow/

# Format code
nextflow fmt main.nf

# Format all files
nextflow fmt nextflow/
```

**Benefits:**
- No additional dependencies
- Official Nextflow tool
- Catches syntax errors early
- Consistent formatting

### 2. nf-core Linting Tools

**Purpose**: Enforces nf-core community standards and best practices

**Installation:**
```bash
pip install nf-core
# or
conda install -c bioconda nf-core
```

**Usage:**
```bash
# Lint pipeline
nf-core lint nextflow/

# Lint with specific checks
nf-core lint nextflow/ --check all

# Lint specific checks only
nf-core lint nextflow/ --check nextflow_syntax,params_schema
```

**Checks Include:**
- Nextflow syntax validation
- Parameter schema validation
- Process naming conventions
- Module structure
- Documentation requirements
- Best practices

**Benefits:**
- Community-standard checks
- Comprehensive validation
- Helps maintain consistency
- Catches common mistakes

### 3. AWS Labs Linter Rules for Nextflow

**Purpose**: Static analysis using CodeNarc (Groovy static analysis)

**Repository**: https://github.com/awslabs/linter-rules-for-nextflow

**Features:**
- Detects errors before runtime
- Enforces coding standards
- Uses CodeNarc for Groovy analysis
- Customizable rules

**Installation:**
```bash
# Clone repository
git clone https://github.com/awslabs/linter-rules-for-nextflow.git
cd linter-rules-for-nextflow

# Follow installation instructions
```

**Usage:**
```bash
# Run linter
./lint.sh nextflow/main.nf
```

**Benefits:**
- Advanced static analysis
- Catches complex issues
- Customizable rules
- Good for large projects

### 4. Nextflow VS Code Extension

**Purpose**: Real-time linting and syntax checking in VS Code

**Installation:**
- Install "Nextflow" extension in VS Code
- Provides syntax highlighting, diagnostics, and code completion

**Features:**
- Real-time error detection
- Syntax highlighting
- Code completion
- Hover documentation
- Go to definition

**Benefits:**
- Integrated development experience
- Catches errors while typing
- Better productivity
- No command-line needed

## Recommended Setup for RNA MAP

### Phase 1: Basic Linting (Immediate)

**Use Nextflow built-in linting:**

```bash
# Add to CI/CD or pre-commit hook
nextflow lint nextflow/main.nf
nextflow lint nextflow/modules/
nextflow lint nextflow/workflows/
```

**Create lint script:**
```bash
#!/bin/bash
# nextflow/lint.sh

set -e

echo "Linting Nextflow workflow..."
nextflow lint main.nf
nextflow lint modules/
nextflow lint workflows/

echo "✅ All Nextflow files passed linting"
```

### Phase 2: Formatting (Quick Win)

**Use Nextflow formatting:**

```bash
# Format all files
nextflow fmt nextflow/

# Add to pre-commit hook
```

**Create format script:**
```bash
#!/bin/bash
# nextflow/fmt.sh

echo "Formatting Nextflow files..."
nextflow fmt main.nf
nextflow fmt modules/
nextflow fmt workflows/
echo "✅ Formatting complete"
```

### Phase 3: Comprehensive Linting (Recommended)

**Add nf-core linting:**

```bash
# Install
pip install nf-core

# Create lint configuration
# .nf-core-lint.yml (optional, uses defaults if not present)

# Run linting
nf-core lint nextflow/
```

**Create comprehensive lint script:**
```bash
#!/bin/bash
# nextflow/lint_comprehensive.sh

set -e

echo "=== Nextflow Built-in Linting ==="
nextflow lint main.nf
nextflow lint modules/
nextflow lint workflows/

echo ""
echo "=== nf-core Linting ==="
if command -v nf-core &> /dev/null; then
    nf-core lint nextflow/ --check all
else
    echo "⚠️  nf-core not installed, skipping"
    echo "   Install with: pip install nf-core"
fi

echo ""
echo "✅ All linting checks passed"
```

## Integration with Project

### Add to pyproject.toml

```toml
[tool.nextflow]
# Nextflow linting configuration
lint-enabled = true
format-enabled = true

[tool.nextflow.lint]
# Custom lint rules (if using AWS linter)
rules-file = ".nextflow-lint-rules.groovy"

[tool.nf-core]
# nf-core lint configuration
strict = false
fail-warned = false
```

### Pre-commit Hook

Create `.git/hooks/pre-commit` or use pre-commit framework:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Nextflow linting
echo "Linting Nextflow files..."
cd nextflow/
nextflow lint main.nf || exit 1
nextflow fmt --check main.nf || exit 1
cd ..

echo "✅ Nextflow linting passed"
```

### CI/CD Integration

**GitHub Actions example:**
```yaml
name: Nextflow Linting

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Nextflow
        run: |
          wget -qO- https://get.nextflow.io | bash
          sudo mv nextflow /usr/local/bin/
      
      - name: Lint Nextflow
        run: |
          cd nextflow/
          nextflow lint main.nf
          nextflow lint modules/
          nextflow lint workflows/
      
      - name: Install nf-core
        run: pip install nf-core
      
      - name: nf-core Lint
        run: |
          cd nextflow/
          nf-core lint . --check all
```

## Complexity Analysis

### Current Options

**1. Manual Review:**
- Review workflow DAG complexity
- Check process dependencies
- Analyze channel operations

**2. Nextflow Reports:**
```bash
# Generate execution report
nextflow run main.nf -with-report report.html

# Analyze:
# - Process execution times
# - Resource usage
# - Channel operations
```

**3. Custom Analysis:**
- Count processes per workflow
- Measure channel complexity
- Track subworkflow depth

### Recommended Metrics

**Workflow Complexity:**
- Number of processes
- Number of subworkflows
- Channel operation complexity
- Process dependency depth

**Process Complexity:**
- Lines of code per process
- Number of inputs/outputs
- Script complexity (can use Python tools for embedded scripts)

**Module Complexity:**
- Number of modules
- Module reuse frequency
- Inter-module dependencies

## Best Practices

### 1. Regular Linting
- Run linting before commits
- Include in CI/CD pipeline
- Fix issues immediately

### 2. Consistent Formatting
- Use `nextflow fmt` before commits
- Enforce formatting in CI/CD
- Document formatting standards

### 3. Code Review
- Review linting output in PRs
- Address complexity warnings
- Maintain code quality standards

### 4. Documentation
- Document any linting exceptions
- Explain complex patterns
- Keep linting rules updated

## Implementation Plan

### Immediate (Week 1)
1. ✅ Add Nextflow built-in linting to scripts
2. ✅ Create `lint.sh` script
3. ✅ Test linting on current codebase

### Short-term (Month 1)
1. Add nf-core linting
2. Set up pre-commit hooks
3. Integrate into CI/CD

### Long-term (Quarter 1)
1. Custom lint rules if needed
2. Complexity analysis tools
3. Automated quality reports

## Tools Comparison

| Tool | Ease of Use | Coverage | Customization | Recommendation |
|------|-------------|----------|--------------|----------------|
| Nextflow lint | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | **Start here** |
| nf-core lint | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **Add for comprehensive checks** |
| AWS Linter | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Advanced use cases |
| VS Code Extension | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Development only |

## Resources

- **Nextflow Linting**: https://www.nextflow.io/docs/edge/migrations/25-04.html
- **nf-core Tools**: https://nf-co.re/tools/docs/latest/
- **AWS Linter**: https://github.com/awslabs/linter-rules-for-nextflow
- **VS Code Extension**: https://nextflow.io/docs/latest/vscode.html

## Next Steps

1. Install Nextflow 25.04+ (if not already)
2. Create `nextflow/lint.sh` script
3. Test on current codebase
4. Add to pre-commit hooks
5. Integrate into CI/CD pipeline
6. Add nf-core linting for comprehensive checks

