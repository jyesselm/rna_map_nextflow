# RNA MAP Nextflow - Testing Checklist

Use this checklist to systematically test the workflow on your cluster.

## Pre-Testing Setup

- [ ] Repository cloned to cluster
- [ ] Conda/Mamba available
- [ ] SLURM access confirmed
- [ ] Sufficient storage space available
- [ ] Test data accessible

## Installation Checklist

- [ ] Conda environment created: `conda env create -f environment.yml`
- [ ] Environment activated: `conda activate rna-map-nextflow`
- [ ] PYTHONPATH set: `export PYTHONPATH="${PWD}/lib:${PYTHONPATH}"`
- [ ] Added PYTHONPATH to `~/.bashrc` or `~/.zshrc` (for persistence)

## Tool Verification

- [ ] Java installed and version 8-18: `java -version`
- [ ] Nextflow installed: `nextflow -version`
- [ ] Bowtie2 installed: `which bowtie2`
- [ ] FastQC installed: `which fastqc`
- [ ] Trim Galore installed: `which trim_galore`
- [ ] Cutadapt installed: `which cutadapt`

## Python Library Verification

- [ ] lib/ directory exists: `ls -d lib/`
- [ ] Python can import lib.bit_vectors: `python -c "from lib.bit_vectors import generate_bit_vectors"`
- [ ] Python can import lib.core.config: `python -c "from lib.core.config import BitVectorConfig"`
- [ ] Python can import lib.analysis.statistics: `python -c "from lib.analysis.statistics import merge_all_merge_mut_histo_dicts"`
- [ ] Python can import lib.mutation_histogram: `python -c "from lib.mutation_histogram import write_mut_histos_to_json_file"`

## File Structure Verification

- [ ] main.nf exists: `test -f main.nf`
- [ ] nextflow.config exists: `test -f nextflow.config`
- [ ] modules/ directory exists: `test -d modules`
- [ ] workflows/ directory exists: `test -d workflows`
- [ ] conf/ directory exists: `test -d conf`
- [ ] lib/ directory exists: `test -d lib`

## Test Data Verification

- [ ] test/resources/case_1/test.fasta exists
- [ ] test/resources/case_1/test_mate1.fastq exists
- [ ] test/resources/case_1/test_mate2.fastq exists
- [ ] test/resources/case_1/test.csv exists
- [ ] Test data files are readable: `head test/resources/case_1/test.fasta`

## Test Execution Checklist

### Level 1: Comprehensive Test Suite
- [ ] Run `./test/nextflow/test_cluster.sh`
- [ ] All 7 test phases pass
- [ ] No errors in output

### Level 2: Syntax Validation
- [ ] Run `./test/nextflow/test_local_simple.sh`
- [ ] Workflow files validated
- [ ] Test data verified

### Level 3: Dry Run
- [ ] Nextflow help works: `nextflow run main.nf --help`
- [ ] Dry run completes: `nextflow run main.nf -profile slurm ... -resume`
- [ ] DAG generated successfully

### Level 4: Minimal Test
- [ ] Create minimal test job script
- [ ] Submit to SLURM: `sbatch test_cluster_minimal.sh`
- [ ] Job completes successfully
- [ ] Check job output: `cat test_*.out`
- [ ] No errors in job log: `cat test_*.err`

### Level 5: Output Verification (Minimal Test)
- [ ] Results directory created: `test_results_minimal/`
- [ ] Summary CSV exists: `test_results_minimal/*/BitVector_Files/summary.csv`
- [ ] Summary CSV has data: `head test_results_minimal/*/BitVector_Files/summary.csv`
- [ ] Mutation histograms exist: `ls test_results_minimal/*/BitVector_Files/mutation_histos.*`
- [ ] SAM file exists: `ls test_results_minimal/*/Mapping_Files/aligned.sam`

### Level 6: Full Test
- [ ] Create full test job script
- [ ] Submit to SLURM: `sbatch test_cluster_full.sh`
- [ ] Job completes successfully
- [ ] All steps executed (FastQC, Trim Galore, alignment, bit vectors)

### Level 7: Output Verification (Full Test)
- [ ] Results directory created: `test_results_full/`
- [ ] All output files present
- [ ] Summary CSV has expected columns
- [ ] Mutation histograms load correctly (Python test)
- [ ] Nextflow reports generated: `test_report_full.html`, `test_dag_full.html`

### Level 8: Parallel Processing Test
- [ ] Create parallel test job script
- [ ] Submit to SLURM: `sbatch test_cluster_parallel.sh`
- [ ] Job completes successfully
- [ ] FASTQ splitting works
- [ ] Multiple chunks processed
- [ ] Results merged correctly

## Configuration Verification

- [ ] conf/base.config exists and is valid
- [ ] conf/local.config exists (for local testing)
- [ ] conf/slurm.config exists (for cluster)
- [ ] SLURM account correct: `sacctmgr show user $USER`
- [ ] SLURM partition accessible: `sinfo -p <partition>`

## Performance Verification

- [ ] Job completes within expected time
- [ ] Memory usage reasonable
- [ ] CPU usage appropriate
- [ ] No excessive I/O

## Documentation Review

- [ ] Read CLUSTER_TESTING_GUIDE.md
- [ ] Reviewed CLUSTER_TESTING_QUICKREF.md
- [ ] Understood troubleshooting section
- [ ] Know where to find help

## Production Readiness

- [ ] All tests pass
- [ ] Results validated
- [ ] Configuration tuned for your cluster
- [ ] Resource limits appropriate
- [ ] Storage location configured
- [ ] Monitoring set up (optional)

## Notes

Use this space to record any issues or observations:

```
Date: ___________
Cluster: ___________
Issues: 
  - 
  - 
  - 

Solutions:
  - 
  - 
  - 

Next Steps:
  - 
  - 
  - 
```

---

**Quick Links:**
- Full Guide: [CLUSTER_TESTING_GUIDE.md](CLUSTER_TESTING_GUIDE.md)
- Quick Reference: [CLUSTER_TESTING_QUICKREF.md](CLUSTER_TESTING_QUICKREF.md)
- Test Scripts: [../../test/nextflow/](../../test/nextflow/)

