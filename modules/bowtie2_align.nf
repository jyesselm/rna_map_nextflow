/*
 * Bowtie2 Alignment Process
 * 
 * Reusable process for running Bowtie2 alignment.
 * Handles both single-end and paired-end reads.
 */

process BOWTIE2_ALIGN {
    tag "${sample_id}"
    label 'process_high'
    publishDir "${params.output_dir}/${sample_id}/Mapping_Files",
        mode: 'copy',
        pattern: 'aligned.sam',
        saveAs: { filename -> 'aligned.sam' }
    
    input:
    tuple val(sample_id), path(fasta), path(index1), path(index2), path(index3), path(index4), path(index_rev1), path(index_rev2), path(trimmed_fq1), path(trimmed_fq2), path(dot_bracket)
    val(bt2_args)
    
    output:
    tuple val(sample_id), path("aligned.sam"), path(fasta), path("is_paired.txt"), path(dot_bracket)
    
    script:
    def index_name = fasta.baseName
    // Check if trimmed_fq2 exists and is not empty placeholder
    def is_paired = (trimmed_fq2 && trimmed_fq2.toString().contains("trimmed_2"))
    def fastq_args = is_paired ? "-1 ${trimmed_fq1} -2 ${trimmed_fq2}" : "-U ${trimmed_fq1}"
    def is_paired_val = is_paired ? "True" : "False"
    // Convert semicolon-separated args to space-separated, add -p if not present
    def bt2_args_list = bt2_args.split(';').findAll { it.trim() }
    if (!bt2_args_list.any { it.startsWith('-p') }) {
        bt2_args_list << "-p ${task.cpus}"
    }
    def bt2_cmd = bt2_args_list.join(' ')
    """
    echo "${is_paired_val}" > is_paired.txt
    bowtie2 ${bt2_cmd} -x ${index_name} -S aligned.sam ${fastq_args}
    """
}

