/*
 * Parallel Mapping Subworkflow
 * 
 * Splits FASTQ files into chunks, processes each chunk in parallel,
 * then joins the results. Useful for very large FASTQ files.
 */

// Include required modules
include { SPLIT_FASTQ } from '../modules/split_fastq.nf'
include { FASTQC } from '../modules/fastqc.nf'
include { TRIM_GALORE } from '../modules/trim_galore.nf'
include { BOWTIE2_BUILD } from '../modules/bowtie2_build.nf'
include { BOWTIE2_ALIGN } from '../modules/bowtie2_align.nf'
include { RNA_MAP_BIT_VECTORS } from '../modules/rna_map_bit_vectors.nf'
include { JOIN_SAM } from '../modules/join_sam.nf'
include { JOIN_MUTATION_HISTOS } from '../modules/join_mutation_histos.nf'
include { JOIN_BIT_VECTORS } from '../modules/join_bit_vectors.nf'

workflow PARALLEL_MAPPING {
    take:
    samples_ch  // channel: [sample_id, fasta, fastq1, fastq2, dot_bracket]
    skip_fastqc
    skip_trim_galore
    fastqc_args
    tg_q_cutoff
    tg_args
    bt2_alignment_args
    chunk_size  // Number of reads per chunk
    qscore_cutoff
    map_score_cutoff
    summary_output_only
    
    main:
    // Step 1: Split FASTQ files into chunks
    SPLIT_FASTQ(samples_ch, chunk_size)
    
    // Step 2: FastQC on original files (optional, before splitting)
    if (!skip_fastqc) {
        FASTQC(samples_ch, skip_fastqc, fastqc_args)
    }
    
    // Step 3: Get metadata and chunk files
    SPLIT_FASTQ.out.metadata.first().set { sample_metadata }
    
    // Create channel of individual chunks with metadata
    SPLIT_FASTQ.out.chunk_files
        .flatten()
        .map { chunk_file ->
            def filename = chunk_file.getName()
            def chunk_num = filename.replaceAll(/.*chunk_([0-9]+).*/, '$1')
            def is_r1 = filename.contains("_1.fastq") || (!filename.contains("_2.fastq") && !filename.contains("_1.fastq"))
            def is_gz = filename.endsWith(".gz")
            [chunk_num, chunk_file, is_r1, is_gz]
        }
        .groupTuple(by: 0)  // Group by chunk number
        .map { chunk_num, files, flags, gz_flags ->
            def r1 = files.find { it.toString().contains("_1.fastq") || (!it.toString().contains("_2.fastq") && !it.toString().contains("_1.fastq")) }
            def r2 = files.find { it.toString().contains("_2.fastq") }
            if (!r2) {
                // Single-end or missing R2 - create placeholder (preserve compression)
                def is_gz = r1.toString().endsWith(".gz")
                r2 = file("${workDir}/.empty_chunk_${chunk_num}_2.fastq${is_gz ? '.gz' : ''}")
            }
            [chunk_num, r1, r2]
        }
        .combine(sample_metadata)
        .map { chunk_num, chunk_fq1, chunk_fq2, sample_id, fasta, dot_bracket ->
            def chunk_id = "${sample_id}_chunk${chunk_num}"
            [chunk_id, fasta, chunk_fq1, chunk_fq2, dot_bracket]
        }
        .set { chunk_samples }
    
    // Step 4: Build index first (use original sample, not chunks)
    // This needs to complete before we can align chunks
    samples_ch.first()
        .map { sample_id, fasta, fastq1, fastq2, dot_bracket ->
            [sample_id, fasta, fastq1, fastq2, dot_bracket]
        }
        .set { index_input }
    
    BOWTIE2_BUILD(index_input)
    
    // Step 5: Process each chunk in parallel
    // Trim each chunk
    TRIM_GALORE(chunk_samples, skip_trim_galore, tg_q_cutoff, tg_args)
    
    // Step 6: Align each chunk (in parallel)
    // Use combine() without 'by' to create cartesian product (like cross())
    // This will pair each trimmed chunk with the index
    BOWTIE2_BUILD.out
        .map { sample_id, fasta, idx1, idx2, idx3, idx4, idx_rev1, idx_rev2, t1, t2, db -> 
            [idx1, idx2, idx3, idx4, idx_rev1, idx_rev2]
        }
        .set { index_ch }
    
    // Use combine() without 'by' - creates cartesian product: each trimmed chunk × index
    TRIM_GALORE.out
        .combine(index_ch)
        .map { chunk_id, fasta, trimmed_fq1, trimmed_fq2, dot_bracket, idx1, idx2, idx3, idx4, idx_rev1, idx_rev2 ->
            [chunk_id, fasta, idx1, idx2, idx3, idx4, idx_rev1, idx_rev2, trimmed_fq1, trimmed_fq2, dot_bracket]
        }
        .set { align_input }
    
    BOWTIE2_ALIGN(align_input, bt2_alignment_args)
    
    // Step 5: Generate bit vectors on each chunk (in parallel)
    // Access the aligned output channel (not stats)
    RNA_MAP_BIT_VECTORS(BOWTIE2_ALIGN.out.aligned, qscore_cutoff, map_score_cutoff, summary_output_only)
    
    // Step 6: Join results from all chunks
    // Group by original sample_id
    RNA_MAP_BIT_VECTORS.out.summary
        .map { chunk_id, summary ->
            def sample_id = chunk_id.replaceAll(/^(.*)_chunk[0-9]+$/, '$1')
            [sample_id, chunk_id]
        }
        .groupTuple(by: 0)
        .set { chunk_summaries }
    
    RNA_MAP_BIT_VECTORS.out.bitvector_files
        .map { chunk_id, bv_files ->
            def sample_id = chunk_id.replaceAll(/^(.*)_chunk[0-9]+$/, '$1')
            // Extract parent directory from first bitvector file
            def bv_dir = bv_files instanceof List ? file(bv_files[0].toString()).parent : file(bv_files.toString()).parent
            [sample_id, bv_dir]
        }
        .groupTuple(by: 0)
        .set { chunk_bv_files }
    
    // Get metadata for joining
    BOWTIE2_ALIGN.out.aligned
        .map { chunk_id, sam, fasta, is_paired_file, dot_bracket ->
            def sample_id = chunk_id.replaceAll(/^(.*)_chunk[0-9]+$/, '$1')
            def is_paired = is_paired_file.text.trim()
            [sample_id, sam, fasta, is_paired, dot_bracket]
        }
        .groupTuple(by: 0)
        .map { sample_id, sam_list, fasta_list, is_paired_list, dot_bracket_list ->
            // Convert sam_list to a string representation for passing to Python
            def sam_list_str = sam_list.collect { it.toString() }.join(',')
            [sample_id, sam_list_str, fasta_list[0], is_paired_list[0], dot_bracket_list[0]]
        }
        .set { sam_metadata }
    
    // Join SAM files
    JOIN_SAM(sam_metadata)
    
    // Join mutation histograms (from bit vector output directories)
    // Get mutation histogram files directly from RNA_MAP_BIT_VECTORS output
    RNA_MAP_BIT_VECTORS.out.bitvector_files
        .map { chunk_id, bv_files ->
            def sample_id = chunk_id.replaceAll(/^(.*)_chunk[0-9]+$/, '$1')
            // Extract parent directory from first bitvector file to find mutation_histos.p
            def bv_files_list = bv_files instanceof List ? bv_files : [bv_files]
            def bv_dir = file(bv_files_list[0].toString()).parent
            def mut_histo_p = file("${bv_dir}/mutation_histos.p")
            def mut_histo_json = file("${bv_dir}/mutation_histos.json")
            [sample_id, mut_histo_p, mut_histo_json]
        }
        .groupTuple(by: 0)
        .combine(sam_metadata, by: 0)
        .map { sample_id, mut_histo_p_list, mut_histo_json_list, sam_list, fasta, is_paired, dot_bracket ->
            // Convert lists to comma-separated strings
            def mut_histo_p_str = mut_histo_p_list.collect { it.toString() }.join(',')
            def mut_histo_json_str = mut_histo_json_list.collect { it.toString() }.join(',')
            [sample_id, mut_histo_p_str, mut_histo_json_str, fasta, is_paired, dot_bracket]
        }
        .set { mut_histo_input }
    
    JOIN_MUTATION_HISTOS(mut_histo_input)
    
    // Join bit vector files
    // Get bit vector files directly from RNA_MAP_BIT_VECTORS output
    RNA_MAP_BIT_VECTORS.out.bitvector_files
        .map { chunk_id, bv_files ->
            def sample_id = chunk_id.replaceAll(/^(.*)_chunk[0-9]+$/, '$1')
            [sample_id, bv_files]
        }
        .groupTuple(by: 0)
        .combine(sam_metadata, by: 0)
        .map { sample_id, bv_files_list, sam_list, fasta, is_paired, dot_bracket ->
            // Convert bv_files_list (list of file lists) to a flat list of file paths
            def all_bv_files = bv_files_list.flatten().collect { it.toString() }
            def bv_files_str = all_bv_files.join(',')
            [sample_id, bv_files_str, fasta, is_paired, dot_bracket]
        }
        .set { bv_join_input }
    
    JOIN_BIT_VECTORS(bv_join_input)
    
    // Create final aligned channel (from joined SAM - mutation histos already joined)
    JOIN_SAM.out
        .set { final_aligned }
    
    emit:
    aligned = final_aligned  // [sample_id, sam, fasta, is_paired, dot_bracket]
}
