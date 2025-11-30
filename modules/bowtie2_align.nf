/*
 * Bowtie2 Alignment Process
 * 
 * Reusable process for running Bowtie2 alignment.
 * Handles both single-end and paired-end reads.
 * Captures alignment statistics in JSON format.
 */

process BOWTIE2_ALIGN {
    tag "${sample_id}"
    label 'process_high'
    publishDir "${params.output_dir}/${sample_id}/Mapping_Files",
        mode: 'copy',
        pattern: 'aligned.sam',
        saveAs: { _filename -> 'aligned.sam' }
    publishDir "${params.output_dir}/${sample_id}/Mapping_Files",
        mode: 'copy',
        pattern: 'alignment_stats.json',
        saveAs: { _filename -> 'alignment_stats.json' }
    
    input:
    tuple val(sample_id), path(fasta), path(index1), path(index2), path(index3), path(index4), path(index_rev1), path(index_rev2), path(trimmed_fq1), path(trimmed_fq2), path(dot_bracket)
    val(bt2_args)
    
    output:
    tuple val(sample_id), path("aligned.sam"), path(fasta), path("is_paired.txt"), path(dot_bracket), emit: aligned
    path("alignment_stats.json"), emit: stats
    
    script:
    def index_name = fasta.baseName
    // Check if trimmed_fq2 exists and is not empty placeholder
    def is_paired = (trimmed_fq2 && trimmed_fq2.toString().contains("trimmed_2"))
    def fastq_args = is_paired ? "-1 ${trimmed_fq1} -2 ${trimmed_fq2}" : "-U ${trimmed_fq1}"
    def is_paired_val = is_paired ? "True" : "False"
    // Convert semicolon-separated args to space-separated, add -p if not present
    def bt2_args_list = bt2_args.split(';').findAll { str -> str.trim() }
    if (!bt2_args_list.any { arg -> arg.startsWith('-p') }) {
        bt2_args_list << "-p ${task.cpus}"
    }
    def bt2_cmd = bt2_args_list.join(' ')
    """
    echo "${is_paired_val}" > is_paired.txt
    
    # Run Bowtie2 and capture stderr (alignment statistics)
    bowtie2 ${bt2_cmd} -x ${index_name} -S aligned.sam ${fastq_args} 2> bowtie2_stderr.txt
    
    # Parse Bowtie2 statistics and create JSON
    python3 << 'PYTHON_SCRIPT'
    import json
    import re
    from pathlib import Path
    from datetime import datetime
    
    stats = {
        "sample_id": "${sample_id}",
        "reference": "${fasta.getName()}",
        "is_paired_end": ${is_paired_val},
        "timestamp": datetime.now().isoformat(),
        "bowtie2_args": "${bt2_cmd}",
        "alignment": {}
    }
    
    # Read Bowtie2 stderr output
    stderr_file = Path("bowtie2_stderr.txt")
    if stderr_file.exists():
        stderr_text = stderr_file.read_text()
        
        # Parse alignment statistics from Bowtie2 output
        # Example: "1000000 reads; of these:"
        reads_pattern = r'(\\d+) reads; of these:'
        reads_match = re.search(reads_pattern, stderr_text)
        if reads_match:
            stats["alignment"]["total_reads"] = int(reads_match.group(1))
        
        # Example: "500000 (50.00%) aligned 0 times"
        unaligned_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned 0 times'
        unaligned_match = re.search(unaligned_pattern, stderr_text)
        if unaligned_match:
            stats["alignment"]["unaligned_count"] = int(unaligned_match.group(1))
            stats["alignment"]["unaligned_percent"] = float(unaligned_match.group(2))
        
        # Example: "300000 (30.00%) aligned exactly 1 time"
        unique_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned exactly 1 time'
        unique_match = re.search(unique_pattern, stderr_text)
        if unique_match:
            stats["alignment"]["unique_alignments"] = int(unique_match.group(1))
            stats["alignment"]["unique_percent"] = float(unique_match.group(2))
        
        # Example: "200000 (20.00%) aligned >1 times"
        multiple_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned >1 times'
        multiple_match = re.search(multiple_pattern, stderr_text)
        if multiple_match:
            stats["alignment"]["multiple_alignments"] = int(multiple_match.group(1))
            stats["alignment"]["multiple_percent"] = float(multiple_match.group(2))
        
        # Example: "50.00% overall alignment rate"
        overall_pattern = r'([\\d.]+)% overall alignment rate'
        overall_match = re.search(overall_pattern, stderr_text)
        if overall_match:
            stats["alignment"]["overall_alignment_rate"] = float(overall_match.group(1))
        
        # For paired-end: extract concordant alignment stats
        if ${is_paired_val}:
            # Example: "400000 (40.00%) aligned concordantly 0 times"
            concordant_0_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned concordantly 0 times'
            concordant_0_match = re.search(concordant_0_pattern, stderr_text)
            if concordant_0_match:
                stats["alignment"]["concordant_0_times"] = int(concordant_0_match.group(1))
                stats["alignment"]["concordant_0_percent"] = float(concordant_0_match.group(2))
            
            # Example: "300000 (30.00%) aligned concordantly exactly 1 time"
            concordant_1_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned concordantly exactly 1 time'
            concordant_1_match = re.search(concordant_1_pattern, stderr_text)
            if concordant_1_match:
                stats["alignment"]["concordant_1_time"] = int(concordant_1_match.group(1))
                stats["alignment"]["concordant_1_percent"] = float(concordant_1_match.group(2))
            
            # Example: "200000 (20.00%) aligned concordantly >1 times"
            concordant_multi_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned concordantly >1 times'
            concordant_multi_match = re.search(concordant_multi_pattern, stderr_text)
            if concordant_multi_match:
                stats["alignment"]["concordant_multiple"] = int(concordant_multi_match.group(1))
                stats["alignment"]["concordant_multiple_percent"] = float(concordant_multi_match.group(2))
            
            # Example: "100000 (10.00%) aligned discordantly 1 time"
            discordant_pattern = r'(\\d+) \\(([\\d.]+)%\\) aligned discordantly 1 time'
            discordant_match = re.search(discordant_pattern, stderr_text)
            if discordant_match:
                stats["alignment"]["discordant_alignments"] = int(discordant_match.group(1))
                stats["alignment"]["discordant_percent"] = float(discordant_match.group(2))
    
    # Calculate derived statistics
    if "total_reads" in stats["alignment"]:
        total = stats["alignment"]["total_reads"]
        if "unaligned_count" in stats["alignment"]:
            aligned_count = total - stats["alignment"]["unaligned_count"]
            stats["alignment"]["aligned_count"] = aligned_count
            if total > 0:
                stats["alignment"]["aligned_percent"] = (aligned_count / total) * 100
    
    # Write JSON file
    with open("alignment_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Alignment statistics saved to alignment_stats.json")
    PYTHON_SCRIPT
    """
}
