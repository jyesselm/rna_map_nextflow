# Bowtie2 Parameter Optimization

This guide explains how to use the Bowtie2 parameter optimization scripts to find optimal parameters that maximize signal-to-noise ratio while maintaining good alignment rates.

## Overview

Two optimization approaches are available:

1. **Grid Search** (`optimize_bowtie2_params.py`): Exhaustive testing of parameter combinations
2. **Bayesian Optimization** (`optimize_bowtie2_params_optuna.py`): Intelligent search using Optuna (recommended for comprehensive sweeps)

Both scripts evaluate parameters based on:
- **Alignment rate**: Percentage of reads that align
- **Signal-to-noise ratio**: AC/GU ratio from mutation histograms (primary metric)
- **Average MAPQ**: Mean mapping quality score
- **Bit vector acceptance rate**: Percentage of reads that pass quality filters
- **Quality score**: Weighted combination of the above metrics

The scripts are designed for ~150bp sequences typical in RNA structure probing experiments (e.g., DMS-MaP).

## Installation

### Basic Requirements
- Python 3.7+
- Bowtie2 installed and in PATH
- Python packages: `pandas`, `pyyaml`

Install basic dependencies:
```bash
pip install pandas pyyaml
```

### For Optuna-based Optimization (Recommended)
```bash
pip install optuna plotly
# Or install from project:
pip install -e ".[optuna]"
```

## Basic Usage

### Option 1: Optuna-based Optimization (Recommended for Comprehensive Sweeps)

Optuna uses Bayesian optimization to intelligently explore the parameter space, making it much more efficient than exhaustive grid search.

#### Single-end reads
```bash
python3 scripts/optimize_bowtie2_params_optuna.py \
    --fasta reference.fasta \
    --fastq1 reads.fastq \
    --output-dir optimization_results \
    --n-trials 100
```

#### Paired-end reads
```bash
python3 scripts/optimize_bowtie2_params_optuna.py \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --output-dir optimization_results \
    --n-trials 100
```

**Advantages of Optuna:**
- **Intelligent search**: Focuses on promising parameter regions
- **Pruning**: Automatically stops unpromising trials early
- **Visualizations**: Generates interactive plots of optimization history
- **Resumable**: Can save and resume optimization studies
- **Efficient**: Typically finds good parameters in 50-100 trials vs. 1000+ for grid search

### Option 2: Grid Search (Exhaustive Testing)

For smaller parameter spaces or when you want to test all combinations:

#### Single-end reads
```bash
python3 scripts/optimize_bowtie2_params.py \
    --fasta reference.fasta \
    --fastq1 reads.fastq \
    --output-dir optimization_results
```

#### Paired-end reads
```bash
python3 scripts/optimize_bowtie2_params.py \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --output-dir optimization_results
```

## Options

### Optuna Script (`optimize_bowtie2_params_optuna.py`)

#### Required Arguments
- `--fasta`: Path to reference FASTA file
- `--fastq1`: Path to first FASTQ file (or single-end reads)

#### Optional Arguments
- `--fastq2`: Path to second FASTQ file (for paired-end reads)
- `--output-dir`: Output directory (default: `bowtie2_optimization_optuna`)
- `--read-length`: Expected read length in bp (default: 150)
- `--threads`: Number of threads for alignment (default: 4)
- `--mapq-cutoff`: MAPQ cutoff for high-quality alignments (default: 20)
- `--n-trials`: Number of Optuna trials to run (default: 100, recommended: 50-200)
- `--timeout`: Timeout in seconds (optional)
- `--study-name`: Name for Optuna study (default: `bowtie2_optimization`)
- `--storage`: Optuna storage URL (e.g., `sqlite:///study.db`) for resuming studies

### Grid Search Script (`optimize_bowtie2_params.py`)

#### Required Arguments
- `--fasta`: Path to reference FASTA file
- `--fastq1`: Path to first FASTQ file (or single-end reads)

#### Optional Arguments
- `--fastq2`: Path to second FASTQ file (for paired-end reads)
- `--output-dir`: Output directory (default: `bowtie2_optimization`)
- `--read-length`: Expected read length in bp (default: 150)
- `--threads`: Number of threads for alignment (default: 4)
- `--mapq-cutoff`: MAPQ cutoff for high-quality alignments (default: 20)
- `--max-combinations`: Maximum number of parameter combinations to test (default: 50)
- `--quick`: Run quick test with ~20 combinations (faster, less thorough)

## Parameter Combinations Tested

The script tests combinations of:

1. **Seed length** (`-L`): 10, 12, 15, 20
2. **Seed mismatches** (`-N`): 0, 1, 2 (number of mismatches allowed in seed)
3. **Maximum insert size** (`-X`): 200, 300, 500, 1000 (for 150bp reads)
4. **Score minimum** (`--score-min`): None, `L,0,-0.6`, `L,0,-0.4`, `G,20,15`
5. **Mismatch penalty** (`--mp`): None, `6,2`, `4,2`
6. **Sensitivity modes**: `--very-fast-local`, `--fast-local`, `--sensitive-local`

All combinations include:
- `--local`: Local alignment mode
- `--no-unal`: Suppress unaligned reads
- `--no-discordant`: Suppress discordant alignments
- `--no-mixed`: Suppress mixed alignments

## Output Files

### Optuna Script Output

The Optuna script generates:

#### `optuna_study.json`
Best trial results with parameters and metrics.

#### `optuna_summary.csv`
Summary table with all completed trials:
- Trial number
- Quality score
- Signal-to-noise ratio
- Alignment rate
- Average MAPQ
- Bit vectors accepted
- All parameter values

#### `optuna_study.pkl`
Pickled Optuna study object for later analysis or resuming.

#### `visualizations/`
Interactive HTML plots:
- `optimization_history.html`: Optimization progress over trials
- `param_importances.html`: Parameter importance analysis
- `parallel_coordinate.html`: Parameter relationships

#### `results/trial_XXX/`
Directories containing SAM files and statistics for each trial.

### Grid Search Script Output

The grid search script generates:

#### `optimization_results.json`
Complete results for all tested combinations, including:
- Parameter settings
- Alignment statistics
- Quality metrics
- Signal-to-noise ratios
- Execution times

#### `optimization_summary.csv`
Summary table with key metrics for each combination:
- Combination ID
- Alignment rate
- High-quality rate
- Signal-to-noise ratio
- Quality score
- Average MAPQ
- Total alignments
- Execution time

#### `best_parameters.json`
Recommended parameter sets:
- **Best by quality score** (balanced recommendation)
- **Best by signal-to-noise** (maximum SNR)
- **Best by alignment rate** (maximum alignments)

#### `results/combo_XXX/`
Directories containing SAM files and statistics for each tested combination.

## Understanding the Results

### Quality Score
The quality score is a weighted combination:
- **40% signal-to-noise** (AC/GU ratio from mutation histogram) - Primary goal
- **30% alignment rate** - Maintain good coverage
- **20% MAPQ quality** - Normalized to 0-60 scale
- **10% bit vector acceptance rate** - Quality of accepted reads

Higher quality scores indicate better balance between signal-to-noise and alignment rate.

### Signal-to-Noise Ratio
The signal-to-noise ratio is calculated from mutation histograms:
- **AC/GU ratio**: Ratio of mutations at A/C positions vs G/U positions
- This is the standard metric used in RNA structure probing (DMS-MaP)
- Higher values indicate better signal quality
- Typical range: 2-10 for good quality data

This is different from alignment-based SNR - it measures the biological signal quality, not just alignment statistics.

## When to Use Each Approach

### Use Optuna (`optimize_bowtie2_params_optuna.py`) when:
- You want a **comprehensive parameter sweep** (recommended)
- You have a large parameter space to explore
- You want intelligent search that focuses on promising regions
- You want visualizations of the optimization process
- You want to resume optimization later

**Recommended settings:**
- Start with `--n-trials 100` for initial exploration
- Increase to `--n-trials 200-300` for thorough optimization
- Use `--storage sqlite:///study.db` to save progress

### Use Grid Search (`optimize_bowtie2_params.py`) when:
- You want to test a specific set of parameter combinations
- You need reproducible, exhaustive testing
- You have a small parameter space (< 100 combinations)
- You want to compare all combinations directly

## Recommendations

1. **For maximum quality**: Use the "best by quality score" combination
   - Best balance of alignment rate and quality
   - Recommended for most use cases

2. **For maximum sensitivity**: Use the "best by alignment rate" combination
   - Maximizes number of aligned reads
   - May include more low-quality alignments

3. **For maximum specificity**: Use the "best by signal-to-noise" combination
   - Maximizes ratio of high-quality to low-quality alignments
   - May have lower overall alignment rate

## Example Workflow

```bash
# 1. Run optimization (quick test first)
python3 scripts/optimize_bowtie2_params.py \
    --fasta test.fasta \
    --fastq1 test_R1.fastq \
    --fastq2 test_R2.fastq \
    --read-length 150 \
    --quick \
    --output-dir quick_optimization

# 2. Review results
cat quick_optimization/best_parameters.json

# 3. Run full optimization if needed
python3 scripts/optimize_bowtie2_params.py \
    --fasta test.fasta \
    --fastq1 test_R1.fastq \
    --fastq2 test_R2.fastq \
    --read-length 150 \
    --max-combinations 100 \
    --output-dir full_optimization

# 4. Use best parameters in Nextflow pipeline
# Copy the bowtie2_args from best_parameters.json to your config
```

## Using Optimized Parameters

After optimization, use the recommended parameters in your Nextflow pipeline:

### Option 1: Command-line
```bash
nextflow run main.nf \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --bt2_alignment_args "--local;--no-unal;--no-discordant;--no-mixed;-X 300;-L 10;--mp 6,2;--score-min L,0,-0.6"
```

### Option 2: Config file
```groovy
// In your config file (e.g., conf/base.config)
params.bt2_alignment_args = "--local;--no-unal;--no-discordant;--no-mixed;-X 300;-L 10;--mp 6,2;--score-min L,0,-0.6"
```

## Tips

1. **Start with `--quick`**: Test with fewer combinations first to get a sense of optimal ranges
2. **Adjust `--mapq-cutoff`**: If your data has different quality characteristics, adjust the MAPQ cutoff
3. **Consider read length**: The script defaults to 150bp but can be adjusted with `--read-length`
4. **Parallel execution**: Use `--threads` to speed up individual alignments
5. **Review summary CSV**: Use spreadsheet software to visualize trends in the summary CSV

## Troubleshooting

### "No successful alignments"
- Check that Bowtie2 is installed and in PATH
- Verify FASTA and FASTQ files are valid
- Check that reference sequences match your data

### "Too many combinations"
- Use `--quick` for faster testing
- Reduce `--max-combinations` to test fewer parameter sets
- Focus on specific parameter ranges if you have prior knowledge

### Low alignment rates
- Try more sensitive settings (e.g., `--sensitive-local`)
- Increase maximum insert size (`-X`)
- Reduce seed length (`-L`)
- Adjust score minimum to be less stringent

## Performance

- **Quick mode** (`--quick`): ~20 combinations, ~10-30 minutes
- **Default mode**: ~50 combinations, ~30-90 minutes
- **Full mode** (`--max-combinations 200`): ~200 combinations, ~2-6 hours

Times depend on:
- Number of reads
- Read length
- Number of threads
- System performance

## Citation

If you use this optimization script in your research, please cite:
- The RNA-MAP Nextflow pipeline
- Bowtie2 (Langmead & Salzberg, 2012)

