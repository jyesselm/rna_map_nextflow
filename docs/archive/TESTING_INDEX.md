# Testing Documentation Index

This index helps you navigate all testing documentation for RNA MAP Nextflow.

## 🚀 Quick Start

**New to cluster testing? Start here:**

1. **Read**: [CLUSTER_TESTING_QUICKREF.md](CLUSTER_TESTING_QUICKREF.md) (5 min)
2. **Run**: `./test/nextflow/test_cluster.sh` (automated test)
3. **Follow**: [CLUSTER_TESTING_GUIDE.md](CLUSTER_TESTING_GUIDE.md) for detailed steps

## 📚 Documentation Files

### Essential Reading

1. **[CLUSTER_TESTING_GUIDE.md](CLUSTER_TESTING_GUIDE.md)** ⭐ **START HERE**
   - **625 lines** of comprehensive instructions
   - Step-by-step testing procedures
   - 5 testing levels (syntax → parallel)
   - SLURM job script templates
   - Troubleshooting guide
   - Result verification procedures
   - **Best for**: First-time setup and detailed testing

2. **[CLUSTER_TESTING_QUICKREF.md](CLUSTER_TESTING_QUICKREF.md)**
   - **87 lines** quick reference
   - Essential commands
   - Common issues & fixes table
   - One-command setup
   - **Best for**: Quick lookups and reminders

3. **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)**
   - **166 lines** systematic checklist
   - Pre-testing setup
   - Installation verification
   - Test execution steps
   - Output verification
   - **Best for**: Systematic testing and tracking progress

### Supporting Files

4. **[test/nextflow/README.md](../../test/nextflow/README.md)**
   - Overview of all test scripts
   - Testing order recommendations
   - Test data location
   - **Best for**: Understanding available test scripts

5. **[QUICKSTART.md](../../QUICKSTART.md)**
   - Quick installation and usage
   - Basic commands
   - **Best for**: General quick reference

## 🧪 Test Scripts

All test scripts are in `test/nextflow/`:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `test_cluster.sh` ⭐ | Comprehensive automated test | **First test on cluster** |
| `test_local_simple.sh` | Syntax validation | Quick validation |
| `test_local.sh` | Full workflow test | Local testing |
| `test_local_conda.sh` | Test with conda | Conda environment testing |
| `test_parallel.sh` | Parallel processing test | Test FASTQ splitting |

## 📋 Testing Workflow

### Recommended Testing Order

```
1. Read CLUSTER_TESTING_QUICKREF.md (5 min)
   ↓
2. Run test_cluster.sh (automated - 5-10 min)
   ↓
3. Follow CLUSTER_TESTING_GUIDE.md Level 1-3 (30 min)
   ↓
4. Run minimal test job (1-2 hours)
   ↓
5. Verify results using checklist
   ↓
6. Run full test (2-4 hours)
   ↓
7. Run parallel test (optional)
```

## 🎯 Testing Scenarios

### Scenario 1: First Time Setup
**Use**: CLUSTER_TESTING_GUIDE.md → "Initial Setup" section
**Time**: 30-60 minutes

### Scenario 2: Quick Verification
**Use**: CLUSTER_TESTING_QUICKREF.md → One-command setup
**Time**: 10-15 minutes

### Scenario 3: Systematic Testing
**Use**: TESTING_CHECKLIST.md
**Time**: 2-4 hours (depending on cluster)

### Scenario 4: Troubleshooting
**Use**: CLUSTER_TESTING_GUIDE.md → "Troubleshooting" section
**Time**: Variable

### Scenario 5: Production Setup
**Use**: CLUSTER_TESTING_GUIDE.md → "Advanced Testing" section
**Time**: 4-8 hours

## 🔍 Finding Information

### "How do I..."
- **...set up the environment?** → CLUSTER_TESTING_GUIDE.md "Initial Setup"
- **...run a quick test?** → CLUSTER_TESTING_QUICKREF.md
- **...create a SLURM job?** → CLUSTER_TESTING_GUIDE.md "Level 3: Single Sample Test"
- **...verify results?** → CLUSTER_TESTING_GUIDE.md "Verifying Results"
- **...fix import errors?** → CLUSTER_TESTING_GUIDE.md "Troubleshooting"
- **...test parallel processing?** → CLUSTER_TESTING_GUIDE.md "Level 5: Parallel Processing Test"
- **...check what I've tested?** → TESTING_CHECKLIST.md

## 📊 Documentation Statistics

- **Total documentation**: ~1,590 lines
- **Test scripts**: 5 scripts
- **Testing levels**: 5 levels (syntax → parallel)
- **Troubleshooting items**: 10+ common issues
- **SLURM templates**: 3 job script templates

## 🆘 Getting Help

1. **Check troubleshooting**: CLUSTER_TESTING_GUIDE.md → "Troubleshooting"
2. **Review checklist**: TESTING_CHECKLIST.md
3. **Check logs**: `.nextflow.log`, `test_*.out`, `test_*.err`
4. **Verify setup**: Run `test_cluster.sh` to identify issues

## 📝 Documentation Updates

Last updated: 2025-11-27
Version: 1.0.0

If you find issues or have suggestions, please update the documentation or report them.

---

**Quick Links:**
- [Main README](../../README.md)
- [Quick Start Guide](../../QUICKSTART.md)
- [Restructure Summary](../../RESTRUCTURE_SUMMARY.md)

