/*
 * Split FASTQ Files Process
 * 
 * Splits large FASTQ files into smaller chunks for parallel processing.
 * Handles both single-end and paired-end reads.
 * Uses Python for more reliable splitting.
 */

process SPLIT_FASTQ {
    tag "${sample_id}"
    label 'process_low'
    
    input:
    tuple val(sample_id), path(fasta), path(fastq1), path(fastq2), path(dot_bracket)
    val(chunk_size)  // Number of reads per chunk
    
    output:
    path("chunks/*.fastq*"), emit: chunk_files  // Matches both .fastq and .fastq.gz
    tuple val(sample_id), path(fasta), path(dot_bracket), emit: metadata
    
    script:
    def is_paired = (fastq2 && !fastq2.toString().contains(".empty"))
    def is_gz1 = fastq1.toString().endsWith(".gz")
    def is_gz2 = fastq2 && !fastq2.toString().contains(".empty") && fastq2.toString().endsWith(".gz")
    def is_paired_py = is_paired ? "True" : "False"
    def is_gz1_py = is_gz1 ? "True" : "False"
    def is_gz2_py = is_gz2 ? "True" : "False"
    """
    mkdir -p chunks
    
    python3 << 'PYTHON_SCRIPT'
    import sys
    import gzip
    from pathlib import Path
    
    fastq1 = Path("${fastq1}")
    fastq2 = Path("${fastq2}") if ${is_paired_py} else None
    chunk_size = ${chunk_size}
    chunks_dir = Path("chunks")
    is_gz1 = ${is_gz1_py}
    is_gz2 = ${is_gz2_py} if fastq2 else False
    
    def open_fastq(path, is_gz):
        return gzip.open(path, "rt") if is_gz else open(path, "r")
    
    def open_chunk(path, is_gz):
        return gzip.open(path, "wt") if is_gz else open(path, "w")
    
    def write_fastq_record(f_out, lines):
        for line in lines:
            f_out.write(line)
    
    chunk_num = 0
    read_count = 0
    
    if fastq2:
        # Paired-end
        with open_fastq(fastq1, is_gz1) as f1, open_fastq(fastq2, is_gz2) as f2:
            chunk_f1 = open_chunk(chunks_dir / f"chunk_{chunk_num}_1.fastq.gz" if is_gz1 else chunks_dir / f"chunk_{chunk_num}_1.fastq", is_gz1)
            chunk_f2 = open_chunk(chunks_dir / f"chunk_{chunk_num}_2.fastq.gz" if is_gz2 else chunks_dir / f"chunk_{chunk_num}_2.fastq", is_gz2)
            
            while True:
                # Read 4 lines from each file (one FASTQ record)
                lines1 = [f1.readline() for _ in range(4)]
                lines2 = [f2.readline() for _ in range(4)]
                
                if not lines1[0]:  # EOF
                    break
                
                if read_count >= chunk_size and read_count > 0:
                    chunk_f1.close()
                    chunk_f2.close()
                    chunk_num += 1
                    chunk_f1 = open_chunk(chunks_dir / f"chunk_{chunk_num}_1.fastq.gz" if is_gz1 else chunks_dir / f"chunk_{chunk_num}_1.fastq", is_gz1)
                    chunk_f2 = open_chunk(chunks_dir / f"chunk_{chunk_num}_2.fastq.gz" if is_gz2 else chunks_dir / f"chunk_{chunk_num}_2.fastq", is_gz2)
                    read_count = 0
                
                write_fastq_record(chunk_f1, lines1)
                write_fastq_record(chunk_f2, lines2)
                read_count += 1
            
            chunk_f1.close()
            chunk_f2.close()
    else:
        # Single-end
        with open_fastq(fastq1, is_gz1) as f1:
            chunk_f = open_chunk(chunks_dir / f"chunk_{chunk_num}.fastq.gz" if is_gz1 else chunks_dir / f"chunk_{chunk_num}.fastq", is_gz1)
            
            while True:
                lines = [f1.readline() for _ in range(4)]
                if not lines[0]:  # EOF
                    break
                
                if read_count >= chunk_size and read_count > 0:
                    chunk_f.close()
                    chunk_num += 1
                    chunk_f = open_chunk(chunks_dir / f"chunk_{chunk_num}.fastq.gz" if is_gz1 else chunks_dir / f"chunk_{chunk_num}.fastq", is_gz1)
                    read_count = 0
                
                write_fastq_record(chunk_f, lines)
                read_count += 1
            
            chunk_f.close()
    
    # Write chunk count
    chunk_count_file = Path("chunk_count.txt")
    with open(chunk_count_file, "w") as f:
        f.write(str(chunk_num + 1))
    
    print(f"Split into {chunk_num + 1} chunks")
    PYTHON_SCRIPT
    """
}
