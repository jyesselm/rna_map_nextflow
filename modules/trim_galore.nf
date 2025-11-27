/*
 * Trim Galore Adapter Trimming Process
 * 
 * Reusable process for running Trim Galore on FASTQ files.
 * Handles both single-end and paired-end reads.
 */

process TRIM_GALORE {
    tag "${sample_id}"
    label 'process_medium'
    
    input:
    tuple val(sample_id), path(fasta), path(fastq1), path(fastq2), path(dot_bracket)
    val(skip)
    val(q_cutoff)
    val(tg_args)
    
    output:
    tuple val(sample_id), path(fasta), path("trimmed_1.fq*"), path("trimmed_2.fq*"), path(dot_bracket), emit: out
    
    script:
    def is_paired = (fastq2 && !fastq2.toString().contains(".empty"))
    def fastq2_arg = is_paired ? fastq2 : ""
    def is_gz = fastq1.toString().endsWith(".gz")
    def ext = is_gz ? "fq.gz" : "fq"
    def is_paired_str = is_paired ? "true" : "false"
    def gzip_flag = is_gz ? "--gzip" : ""
    def tg_args_str = tg_args ? tg_args : ""
    
    if (skip) {
        """
        # Skip trimming, just copy files (preserve compression)
        if [ "${is_paired_str}" == "true" ]; then
            cp ${fastq1} trimmed_1.${ext}
            cp ${fastq2} trimmed_2.${ext}
        else
            cp ${fastq1} trimmed_1.${ext}
            touch trimmed_2.${ext}  # Create empty file for single-end
        fi
        """
    } else {
        if (is_paired) {
            """
            trim_galore --quality ${q_cutoff} --fastqc ${gzip_flag} --paired ${tg_args_str} ${fastq1} ${fastq2} -o .
            # Rename output files to expected names
            for f in *_val_1.${ext}; do mv "\$f" trimmed_1.${ext}; done
            for f in *_val_2.${ext}; do mv "\$f" trimmed_2.${ext}; done
            """
        } else {
            """
            trim_galore --quality ${q_cutoff} --fastqc ${gzip_flag} ${tg_args_str} ${fastq1} -o .
            # Rename output file to expected name
            for f in *_trimmed.${ext}; do mv "\$f" trimmed_1.${ext}; done
            touch trimmed_2.${ext}  # Create empty file for single-end
            """
        }
    }
}

