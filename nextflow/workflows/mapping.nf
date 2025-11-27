/*
 * Mapping Subworkflow
 * 
 * Reusable subworkflow that chains FastQC, Trim Galore, Bowtie2 build, and alignment.
 * Can be used in other workflows that need read mapping.
 */

// Include required modules
include { FASTQC } from '../modules/fastqc.nf'
include { TRIM_GALORE } from '../modules/trim_galore.nf'
include { BOWTIE2_BUILD } from '../modules/bowtie2_build.nf'
include { BOWTIE2_ALIGN } from '../modules/bowtie2_align.nf'

workflow MAPPING {
    take:
    samples_ch  // channel: [sample_id, fasta, fastq1, fastq2, dot_bracket]
    skip_fastqc
    skip_trim_galore
    fastqc_args
    tg_q_cutoff
    tg_args
    bt2_alignment_args
    
    main:
    // Step 1: FastQC (optional)
    FASTQC(samples_ch, skip_fastqc, fastqc_args)
    
    // Step 2: Trim Galore (optional)
    TRIM_GALORE(FASTQC.out, skip_trim_galore, tg_q_cutoff, tg_args)
    
    // Step 3: Build Bowtie2 index
    BOWTIE2_BUILD(TRIM_GALORE.out)
    
    // Step 4: Bowtie2 alignment
    // BOWTIE2_ALIGN expects: tuple with [sample_id, fasta, index_files, trimmed_fq1, trimmed_fq2, dot_bracket], bt2_args
    // BOWTIE2_BUILD.out has: [sample_id, fasta, index_files, trimmed_fq1, trimmed_fq2, dot_bracket]
    BOWTIE2_ALIGN(BOWTIE2_BUILD.out, bt2_alignment_args)
    
    emit:
    aligned = BOWTIE2_ALIGN.out
        .map { sample_id, sam, fasta, is_paired_file, dot_bracket ->
            def is_paired = is_paired_file.text.trim()
            [sample_id, sam, fasta, is_paired, dot_bracket]
        }  // [sample_id, sam, fasta, is_paired, dot_bracket]
}

