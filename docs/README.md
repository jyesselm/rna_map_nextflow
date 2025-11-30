# RNA MAP Nextflow Documentation

Complete documentation for the RNA MAP Nextflow workflow for RNA mutational profiling (MaP) analysis.

## 📚 Essential Documentation

### Getting Started
- **[README.md](../README.md)** - Main repository overview
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide
- **[SETUP.md](./SETUP.md)** - Complete setup guide (environment, IDE, linting)

### Workflow Usage
- **[PIPELINE_GUIDE.md](./PIPELINE_GUIDE.md)** - Workflow usage and configuration
- **[BOWTIE2_OPTIMIZATION.md](./BOWTIE2_OPTIMIZATION.md)** - Bowtie2 parameter optimization

### Testing & Deployment
- **[CLUSTER_TESTING_GUIDE.md](./CLUSTER_TESTING_GUIDE.md)** - Comprehensive cluster testing guide
- **[CLUSTER_TESTING_QUICKREF.md](./CLUSTER_TESTING_QUICKREF.md)** - Quick reference for cluster testing
- **[CONTAINER_USAGE.md](./CONTAINER_USAGE.md)** - Docker/Singularity container usage

### Advanced Topics
- **[MUTATION_TRACKING_GUIDE.md](./MUTATION_TRACKING_GUIDE.md)** - Mutation tracking and analysis
- **[MUTATION_PRESETS_SUMMARY.md](./MUTATION_PRESETS_SUMMARY.md)** - Mutation preset configurations
- **[BITVECTOR_STORAGE.md](./BITVECTOR_STORAGE.md)** - Bit vector storage formats
- **[CPP_IMPLEMENTATION.md](./CPP_IMPLEMENTATION.md)** - C++ implementation details
- **[PYSAM_SUPPORT.md](./PYSAM_SUPPORT.md)** - PySAM integration
- **[FILE_MANAGEMENT_STRATEGIES.md](./FILE_MANAGEMENT_STRATEGIES.md)** - File organization strategies

### Development & Code Quality
- **[NEXTFLOW_LINTING.md](./NEXTFLOW_LINTING.md)** - Nextflow code style and linting

## 🔧 Optimization (Separate Module)

**Note:** Optimization tools are now in a separate, self-contained module:
- **[../optimization/README.md](../optimization/README.md)** - Bowtie2 parameter optimization toolkit

The `optimization/` directory contains all optimization-related code, scripts, docs, and tests. This module can be used independently or extracted to a separate repository.

## 📖 Historical Documentation

Historical and detailed implementation documentation is archived in **[archive/](./archive/)**:
- Completed migration guides
- Implementation comparisons
- Performance analysis
- Historical optimization results

## 🗂️ Documentation Structure

```
docs/
├── README.md                    # This file (documentation index)
├── QUICKSTART.md               # Quick start guide
├── SETUP.md                    # Setup guide
├── PIPELINE_GUIDE.md           # Main workflow documentation
├── CLUSTER_TESTING_GUIDE.md    # Cluster testing
├── CONTAINER_USAGE.md          # Container usage
├── [Specialized guides]        # Advanced topics
├── archive/                    # Historical documentation
└── [Other guides]              # Additional documentation
```

## Quick Links

- **[Main README](../README.md)** - Repository overview
- **[Quick Start](./QUICKSTART.md)** - Get started quickly
- **[Setup Guide](./SETUP.md)** - Complete setup instructions
- **[Optimization](../optimization/README.md)** - Parameter optimization toolkit
- **[Cluster Testing](./CLUSTER_TESTING_GUIDE.md)** - Cluster deployment guide
