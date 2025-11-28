/*
 * RNA MAP Nextflow Workflow
 * 
 * This workflow processes RNA mutational profiling (MaP) sequencing data.
 * Mapping steps (FastQC, Trim Galore, Bowtie2) are handled by Nextflow.
 * Bit vector generation and analysis remain in Python.
 * 
 * Uses modular design with reusable processes and subworkflows.
 */

// Include modules
include { FASTQC } from './modules/fastqc.nf'
include { TRIM_GALORE } from './modules/trim_galore.nf'
include { BOWTIE2_BUILD } from './modules/bowtie2_build.nf'
include { BOWTIE2_ALIGN } from './modules/bowtie2_align.nf'
include { RNA_MAP_BIT_VECTORS } from './modules/rna_map_bit_vectors.nf'
include { WORKFLOW_STATS } from './modules/workflow_stats.nf'

// Include subworkflows
include { MAPPING } from './workflows/mapping.nf'
include { PARALLEL_MAPPING } from './workflows/parallel_mapping.nf'

// Workflow parameters
params.fasta = null
params.fastq1 = null
params.fastq2 = null
params.dot_bracket = null
params.samples_csv = null
params.output_dir = "results"
params.skip_fastqc = false
params.skip_trim_galore = false
// Tool-specific arguments (can be overridden via config file or CLI)
params.fastqc_args = ""  // Additional FastQC arguments (e.g., "--threads 4 --format fastq")
params.tg_q_cutoff = 20
params.tg_args = ""  // Additional Trim Galore arguments (e.g., "--length 20 --adapter AGATCGGAAGAGC")
params.bt2_alignment_args = "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12"
// Bit vector parameters
params.qscore_cutoff = 20
params.map_score_cutoff = 20
params.summary_output_only = false
// General options
params.overwrite = false
// Resource limits
params.max_cpus = 16
params.max_memory = "32 GB"
params.max_time = "24h"
params.account = null
params.partition = "normal"
// Parallel processing
params.split_fastq = false
params.chunk_size = 1000000  // Reads per chunk (1M reads default)
// Container options (for Singularity/Apptainer)
params.container_path = null  // Path to Singularity/Apptainer image (.sif file)

// Input channel for samples CSV
if (params.samples_csv) {
    Channel.fromPath(params.samples_csv, checkIfExists: true)
        .splitCsv(header: true, sep: ',')
        .map { row ->
            def sampleId = row.sample_id ?: "sample_${new File(row.fasta).getName().replaceAll(/\\.fasta.*/, '')}"
            def fastaFile = file(row.fasta, checkIfExists: true)
            def fastq1File = file(row.fastq1, checkIfExists: true)
            // Use null for optional files - will be handled in workflow
            def fastq2File = (row.fastq2 && row.fastq2.trim() && row.fastq2 != '') ? file(row.fastq2, checkIfExists: true) : null
            def dotBracketFile = (row.dot_bracket && row.dot_bracket.trim() && row.dot_bracket != '') ? file(row.dot_bracket, checkIfExists: true) : null
            [sampleId, fastaFile, fastq1File, fastq2File, dotBracketFile]
        }
        .set { samples_ch }
} else if (params.fasta && params.fastq1) {
    // Single sample input
    def fastaFile = file(params.fasta, checkIfExists: true)
    def fastq1File = file(params.fastq1, checkIfExists: true)
    def fastq2File = params.fastq2 ? file(params.fastq2, checkIfExists: true) : null
    def dotBracketFile = params.dot_bracket ? file(params.dot_bracket, checkIfExists: true) : null
    def sampleId = fastaFile.getName().replaceAll(/\\.fasta.*/, '')
    Channel.fromList([[sampleId, fastaFile, fastq1File, fastq2File, dotBracketFile]])
        .set { samples_ch }
} else {
    exit 1, "ERROR: Must provide either --fasta/--fastq1 or --samples_csv"
}

workflow {
    // Create placeholder files for optional inputs if needed
    samples_ch
        .map { sample_id, fasta, fastq1, fastq2, dot_bracket ->
            // Create unique placeholder files in a temp location
            def fastq2File = fastq2 ?: {
                def placeholder = file("${launchDir}/.empty_fastq2_${sample_id}")
                if (!placeholder.exists()) {
                    new File(placeholder.toString()).createNewFile()
                }
                placeholder
            }()
            def dotBracketFile = dot_bracket ?: {
                def placeholder = file("${launchDir}/.empty_db_${sample_id}")
                if (!placeholder.exists()) {
                    new File(placeholder.toString()).createNewFile()
                }
                placeholder
            }()
            [sample_id, fasta, fastq1, fastq2File, dotBracketFile]
        }
        .set { samples }
    
    // Run mapping subworkflow (with or without parallel splitting)
    if (params.split_fastq) {
        // Parallel processing: split → process chunks → join (bit vectors already generated)
        PARALLEL_MAPPING(
            samples,
            params.skip_fastqc,
            params.skip_trim_galore,
            params.fastqc_args,
            params.tg_q_cutoff,
            params.tg_args,
            params.bt2_alignment_args,
            params.chunk_size,
            params.qscore_cutoff,
            params.map_score_cutoff,
            params.summary_output_only
        )
        
        // Aggregate all workflow statistics at the end (parallel mode)
        // Collect from output directory (all files already published)
        PARALLEL_MAPPING.out.aligned
            .map { sample_id, sam, fasta, is_paired, dot_bracket ->
                def output_dir = file("${params.output_dir}/${sample_id}")
                [sample_id, output_dir]
            }
            .set { stats_input_ch }
        
        WORKFLOW_STATS(stats_input_ch)
        
        // Results already published by PARALLEL_MAPPING subworkflow
        PARALLEL_MAPPING.out.aligned
            .view { sample_id, sam, fasta, is_paired, dot_bracket ->
                "Sample ${sample_id}: Processing complete (parallel mode)"
            }
        
        WORKFLOW_STATS.out.stats
            .view { stats_file ->
                "Workflow statistics: ${stats_file}"
            }
    } else {
        // Standard processing: single pipeline
        MAPPING(
            samples,
            params.skip_fastqc,
            params.skip_trim_galore,
            params.fastqc_args,
            params.tg_q_cutoff,
            params.tg_args,
            params.bt2_alignment_args
        )
        
        // Generate bit vectors (Python)
        RNA_MAP_BIT_VECTORS(
            MAPPING.out.aligned,
            params.qscore_cutoff,
            params.map_score_cutoff,
            params.summary_output_only
        )
        
        // Aggregate all workflow statistics at the end
        // Collect from output directory (all files already published)
        RNA_MAP_BIT_VECTORS.out.summary
            .map { sample_id, summary_file ->
                def output_dir = file("${params.output_dir}/${sample_id}")
                [sample_id, output_dir]
            }
            .set { stats_input_ch }
        
        WORKFLOW_STATS(stats_input_ch)
        
        // Publish results
        RNA_MAP_BIT_VECTORS.out.summary
            .view { sample_id, summary_file ->
                "Sample ${sample_id}: ${summary_file}"
            }
        
        WORKFLOW_STATS.out.stats
            .view { stats_file ->
                "Workflow statistics: ${stats_file}"
            }
    }
}
