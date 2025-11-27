/*
 * FastQC Quality Control Process
 * 
 * Reusable process for running FastQC on FASTQ files.
 * Can be used in any Nextflow workflow that needs quality control.
 */

process FASTQC {
    tag "${sample_id}"
    label 'process_low'
    
    publishDir "${params.output_dir}/${sample_id}/Mapping_Files/fastqc",
        mode: 'copy',
        pattern: '*.html',
        saveAs: { filename -> filename }
    publishDir "${params.output_dir}/${sample_id}/Mapping_Files/fastqc",
        mode: 'copy',
        pattern: '*.zip',
        saveAs: { filename -> filename }
    
    input:
    tuple val(sample_id), path(fasta), path(fastq1), path(fastq2), path(dot_bracket)
    val(skip)
    val(fastqc_args)
    
    output:
    tuple val(sample_id), path(fasta), path(fastq1), path(fastq2), path(dot_bracket), emit: out
    
    script:
    if (skip) {
        """
        # Skip FastQC, just pass through
        """
    } else {
        def fastq2_arg = (fastq2 && !fastq2.toString().contains(".empty")) ? fastq2 : ""
        def fastqc_args_str = fastqc_args ? fastqc_args : ""
        """
        mkdir -p fastqc
        fastqc ${fastqc_args_str} ${fastq1} ${fastq2_arg} -o fastqc || true
        """
    }
}

