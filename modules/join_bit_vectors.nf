/*
 * Join Bit Vector Files Process
 * 
 * Merges bit vector files from parallel processing into a single file.
 * Handles both text and JSON formats.
 */

process JOIN_BIT_VECTORS {
    tag "${sample_id}"
    label 'process_low'
    publishDir "${params.output_dir}/${sample_id}/BitVector_Files",
        mode: 'copy',
        pattern: '*_bitvectors.*',
        saveAs: { filename -> filename }
    
    input:
    tuple val(sample_id), val(bitvector_files_str), path(fasta), val(is_paired), path(dot_bracket)
    
    output:
    path("*_bitvectors.*"), emit: bitvector_files
    
    script:
    """
    python3 << 'PYTHON_SCRIPT'
    import sys
    import shutil
    import json
    from pathlib import Path
    from collections import defaultdict
    
    # bitvector_files_str is a comma-separated string of bit vector file paths
    bitvector_files_str = "${bitvector_files_str}"
    
    # Split by comma and clean up paths
    bitvector_files = [Path(f.strip().strip("'").strip('"')) for f in bitvector_files_str.split(',') if f.strip()]
    
    # Filter to only existing files that match bitvector pattern
    bitvector_files = [f for f in bitvector_files if f.exists() and ('_bitvectors.txt' in str(f) or '_bitvectors.json' in str(f))]
    
    if not bitvector_files:
        print(f"WARNING: No bit vector files found. Input was: {bitvector_files_str}", file=sys.stderr)
        sys.exit(0)
    
    # Group files by reference name (extract from filename)
    # Filename format: <ref_name>_bitvectors.txt (e.g., "mttr-6-alt-h3_bitvectors.txt")
    files_by_ref = defaultdict(list)
    for bv_file in bitvector_files:
        bv_path = Path(bv_file)
        # Extract reference name by removing "_bitvectors" suffix
        stem = bv_path.stem
        if stem.endswith('_bitvectors'):
            ref_name = stem[:-11]  # Remove "_bitvectors" (11 characters)
        else:
            # Fallback: use first part before underscore
            ref_name = stem.split('_')[0]
        files_by_ref[ref_name].append(bv_path)
    
    # Merge files for each reference
    # Since all files for a reference should be merged together, we don't need complex sorting
    # Just sort by filename for consistency
    for ref_name, files in files_by_ref.items():
        files_sorted = sorted(files, key=lambda x: str(x))
        
        # Determine format from first file
        first_file = files_sorted[0]
        is_json = first_file.suffix == '.json'
        
        if is_json:
            # Merge JSON files
            merged_data = []
            for json_file in files_sorted:
                if json_file.exists():
                    with open(json_file) as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            merged_data.extend(data)
                        else:
                            merged_data.append(data)
            
            # Write merged JSON
            output_file = f"{ref_name}_bitvectors.json"
            with open(output_file, "w") as f:
                json.dump(merged_data, f)
        else:
            # Merge text files (concatenate, skipping headers after first)
            output_file = f"{ref_name}_bitvectors.txt"
            with open(output_file, "w") as f_out:
                for i, txt_file in enumerate(files_sorted):
                    if txt_file.exists():
                        with open(txt_file) as f_in:
                            lines = f_in.readlines()
                            if i == 0:
                                # Write all lines from first file (may have header)
                                f_out.writelines(lines)
                            else:
                                # Skip header line if present, write rest
                                start_idx = 1 if lines and lines[0].startswith('#') else 0
                                f_out.writelines(lines[start_idx:])
    
    print(f"Merged bit vector files for {len(files_by_ref)} references")
    PYTHON_SCRIPT
    """
}

