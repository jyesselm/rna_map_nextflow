/*
 * Bowtie2 Index Building Process
 * 
 * Reusable process for building Bowtie2 indices from FASTA files.
 */

process BOWTIE2_BUILD {
    tag "${sample_id}"
    label 'process_low'
    
    input:
    tuple val(sample_id), path(fasta), path(trimmed_fq1), path(trimmed_fq2), path(dot_bracket)
    
    output:
    tuple val(sample_id), path(fasta), path("${fasta.baseName}.1.bt2"), path("${fasta.baseName}.2.bt2"), path("${fasta.baseName}.3.bt2"), path("${fasta.baseName}.4.bt2"), path("${fasta.baseName}.rev.1.bt2"), path("${fasta.baseName}.rev.2.bt2"), path(trimmed_fq1), path(trimmed_fq2), path(dot_bracket), emit: out
    
    script:
    def index_name = fasta.baseName
    """
    bowtie2-build ${fasta} ${index_name}
    """
}

