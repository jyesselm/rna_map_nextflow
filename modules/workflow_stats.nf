/*
 * Workflow Statistics Aggregation Process
 * 
 * Collects and aggregates critical statistics from all workflow steps
 * into a single JSON file for easy analysis and reporting.
 * 
 * This process runs at the end and collects:
 * - Bowtie2 alignment statistics
 * - Bit vector generation statistics
 * - Overall workflow summary
 */

process WORKFLOW_STATS {
    tag "${sample_id ?: 'single_sample'}"
    label 'process_low'
    
    input:
    tuple val(sample_id), path(output_dir)
    
    output:
    path("workflow_stats.json"), emit: stats
    
    publishDir { sample_id ? "${params.output_dir}/${sample_id}" : "${params.output_dir}" },
        mode: 'copy',
        pattern: 'workflow_stats.json',
        saveAs: { _filename -> 'workflow_stats.json' }
    
    script:
    """
    python3 << 'PYTHON_SCRIPT'
    import json
    import csv
    from pathlib import Path
    from datetime import datetime
    
    output_dir = Path("${output_dir}")
    sample_id = "${sample_id}"
    
    stats = {
        "sample_id": sample_id,
        "timestamp": datetime.now().isoformat(),
        "workflow_version": "0.4.1",
        "alignment": {},
        "bit_vectors": {},
        "summary": {}
    }
    
    # Load alignment statistics from Mapping_Files
    # Handle both single file (non-parallel) and multiple chunk files (parallel)
    mapping_dir = output_dir / "Mapping_Files"
    alignment_stats_files = []
    
    # Check for single alignment_stats.json (non-parallel mode)
    single_stats_file = mapping_dir / "alignment_stats.json"
    if single_stats_file.exists():
        alignment_stats_files = [single_stats_file]
    else:
        # Check for chunk-based stats files (parallel mode)
        # Look for pattern: <sample_id>_chunk*/Mapping_Files/alignment_stats.json
        parent_dir = output_dir.parent
        if parent_dir.exists():
            # Find all chunk directories
            chunk_dirs = [d for d in parent_dir.iterdir() 
                         if d.is_dir() and sample_id in d.name and "_chunk" in d.name]
            for chunk_dir in chunk_dirs:
                chunk_stats = chunk_dir / "Mapping_Files" / "alignment_stats.json"
                if chunk_stats.exists():
                    alignment_stats_files.append(chunk_stats)
    
    # Aggregate alignment statistics from all files
    if alignment_stats_files:
        total_reads = 0
        total_aligned = 0
        total_unaligned = 0
        total_unique = 0
        total_multiple = 0
        chunk_stats_list = []
        
        for stats_file in alignment_stats_files:
            try:
                with open(stats_file) as f:
                    chunk_data = json.load(f)
                    chunk_alignment = chunk_data.get("alignment", {})
                    chunk_stats_list.append(chunk_alignment)
                    
                    # Sum up totals
                    if "total_reads" in chunk_alignment:
                        total_reads += chunk_alignment["total_reads"]
                    if "aligned_count" in chunk_alignment:
                        total_aligned += chunk_alignment["aligned_count"]
                    elif "total_reads" in chunk_alignment and "unaligned_count" in chunk_alignment:
                        total_aligned += (chunk_alignment["total_reads"] - chunk_alignment["unaligned_count"])
                    if "unaligned_count" in chunk_alignment:
                        total_unaligned += chunk_alignment["unaligned_count"]
                    if "unique_alignments" in chunk_alignment:
                        total_unique += chunk_alignment["unique_alignments"]
                    if "multiple_alignments" in chunk_alignment:
                        total_multiple += chunk_alignment["multiple_alignments"]
                    
                    # Get metadata from first file
                    if not stats.get("reference"):
                        stats["reference"] = chunk_data.get("reference", "")
                        stats["is_paired_end"] = chunk_data.get("is_paired_end", False)
                        stats["alignment"]["bowtie2_args"] = chunk_data.get("bowtie2_args", "")
            except Exception as e:
                stats["alignment"]["error"] = f"Could not load alignment stats from {stats_file}: {str(e)}"
        
        # Store aggregated statistics
        if total_reads > 0:
            stats["alignment"]["total_reads"] = total_reads
            stats["alignment"]["aligned_count"] = total_aligned
            stats["alignment"]["unaligned_count"] = total_unaligned
            stats["alignment"]["overall_alignment_rate"] = (total_aligned / total_reads * 100) if total_reads > 0 else 0
            if total_unique > 0:
                stats["alignment"]["unique_alignments"] = total_unique
                stats["alignment"]["unique_percent"] = (total_unique / total_reads * 100) if total_reads > 0 else 0
            if total_multiple > 0:
                stats["alignment"]["multiple_alignments"] = total_multiple
                stats["alignment"]["multiple_percent"] = (total_multiple / total_reads * 100) if total_reads > 0 else 0
        
        # Store chunk count for parallel mode
        if len(alignment_stats_files) > 1:
            stats["alignment"]["chunks_processed"] = len(alignment_stats_files)
            stats["alignment"]["parallel_mode"] = True
    
    # Load bit vector summary statistics from BitVector_Files
    summary_file = output_dir / "BitVector_Files" / "summary.csv"
    if summary_file.exists():
        try:
            with open(summary_file) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    # Aggregate bit vector statistics
                    total_sequences = len(rows)
                    stats["bit_vectors"]["total_sequences"] = total_sequences
                    
                    # Calculate averages for numeric columns
                    numeric_cols = ["num_reads", "num_mutations", "coverage"]
                    for col in numeric_cols:
                        if col in rows[0]:
                            values = []
                            for row in rows:
                                val = row.get(col, "").strip()
                                if val and val != "NA" and val != "":
                                    try:
                                        values.append(float(val))
                                    except ValueError:
                                        pass
                            if values:
                                stats["bit_vectors"][f"avg_{col}"] = sum(values) / len(values)
                                stats["bit_vectors"][f"min_{col}"] = min(values)
                                stats["bit_vectors"][f"max_{col}"] = max(values)
                                stats["bit_vectors"][f"total_{col}"] = sum(values)
                    
                    # Count sequences with mutations
                    if "num_mutations" in rows[0]:
                        mutated = 0
                        for row in rows:
                            mut_val = row.get("num_mutations", "0").strip()
                            if mut_val and mut_val != "0" and mut_val != "NA":
                                try:
                                    if float(mut_val) > 0:
                                        mutated += 1
                                except ValueError:
                                    pass
                        stats["bit_vectors"]["sequences_with_mutations"] = mutated
                        stats["bit_vectors"]["mutation_rate"] = (mutated / total_sequences * 100) if total_sequences > 0 else 0
                    
                    # Get sequence names if available
                    if "sequence" in rows[0]:
                        stats["bit_vectors"]["sequences"] = [row["sequence"] for row in rows]
        except Exception as e:
            stats["bit_vectors"]["error"] = f"Could not parse summary CSV: {str(e)}"
    
    # Calculate overall summary statistics
    if "total_reads" in stats["alignment"]:
        total_reads = stats["alignment"]["total_reads"]
        aligned_reads = stats["alignment"].get("aligned_count", 0)
        
        stats["summary"]["total_reads"] = total_reads
        stats["summary"]["aligned_reads"] = aligned_reads
        stats["summary"]["alignment_rate"] = stats["alignment"].get("overall_alignment_rate", 0)
        
        if "total_sequences" in stats["bit_vectors"]:
            stats["summary"]["sequences_analyzed"] = stats["bit_vectors"]["total_sequences"]
        
        if "total_num_reads" in stats["bit_vectors"]:
            stats["summary"]["reads_in_bit_vectors"] = int(stats["bit_vectors"]["total_num_reads"])
    
    # Add file paths for reference
    alignment_stats_path = None
    if alignment_stats_files:
        alignment_stats_path = str(alignment_stats_files[0])
    elif single_stats_file.exists():
        alignment_stats_path = str(single_stats_file)
    
    stats["files"] = {
        "alignment_stats": alignment_stats_path,
        "bitvector_summary": str(summary_file) if summary_file.exists() else None,
        "sam_file": str(output_dir / "Mapping_Files" / "aligned.sam") if (output_dir / "Mapping_Files" / "aligned.sam").exists() else None
    }
    
    # Write aggregated statistics
    with open("workflow_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Workflow statistics saved to workflow_stats.json")
    print(f"  - Alignment rate: {stats['summary'].get('alignment_rate', 'N/A')}%")
    print(f"  - Sequences analyzed: {stats['bit_vectors'].get('total_sequences', 'N/A')}")
    PYTHON_SCRIPT
    """
}

