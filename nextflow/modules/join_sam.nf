/*
 * Join SAM Files Process
 * 
 * Merges multiple SAM files from parallel processing into a single SAM file.
 * Handles SAM headers correctly (keeps header from first file, merges alignments).
 */

process JOIN_SAM {
    tag "${sample_id}"
    label 'process_medium'
    publishDir "${params.output_dir}/${sample_id}/Mapping_Files",
        mode: 'copy',
        pattern: 'aligned.sam',
        saveAs: { filename -> 'aligned.sam' }
    
    input:
    tuple val(sample_id), val(sam_files_paths), path(fasta), val(is_paired), path(dot_bracket)
    
    // Note: sam_files_paths is a list of SAM file path strings
    // We pass them as values to avoid file collision, then access them directly in the script
    
    output:
    tuple val(sample_id), path("aligned.sam"), path(fasta), val(is_paired), path(dot_bracket)
    
    script:
    """
    python3 << 'PYTHON_SCRIPT'
    import sys
    import shutil
    from pathlib import Path
    
    # sam_files_paths is a comma-separated string of file paths from Nextflow
    sam_files_str = "${sam_files_paths}"
    
    # Split by comma and clean up paths
    sam_files_list = [f.strip().strip("'").strip('"') for f in sam_files_str.split(',') if f.strip()]
    
    # Convert to list of Path objects
    sam_files = [Path(f) for f in sam_files_list if f]
    
    if not sam_files or len(sam_files) == 0:
        print(f"ERROR: No SAM files found. Input was: {sam_files_list}", file=sys.stderr)
        sys.exit(1)
    
    # Copy files to a temporary directory with unique names to avoid collisions
    import tempfile
    temp_dir = Path("chunks")
    temp_dir.mkdir(exist_ok=True)
    
    # Copy each file with a unique name based on its index
    copied_files = []
    for idx, sam_file in enumerate(sam_files):
        if not sam_file.exists():
            print(f"WARNING: SAM file does not exist: {sam_file}", file=sys.stderr)
            continue
        dest_file = temp_dir / f"chunk_{idx}.sam"
        shutil.copy(sam_file, dest_file)
        copied_files.append(dest_file)
        print(f"Copied {sam_file} to {dest_file}", file=sys.stderr)
    
    if not copied_files:
        print(f"ERROR: No SAM files were successfully copied", file=sys.stderr)
        sys.exit(1)
    
    sam_files = copied_files
    
    sam_files_sorted = sam_files  # Already sorted by chunk number
    
    # Extract header from first SAM file
    first_sam = Path(sam_files_sorted[0])
    with open(first_sam) as f_in, open("aligned.sam", "w") as f_out:
        # Write header
        for line in f_in:
            if line.startswith('@'):
                f_out.write(line)
            else:
                break
    
    # Append all alignment lines from all SAM files
    with open("aligned.sam", "a") as f_out:
        for sam_file in sam_files_sorted:
            sam_path = Path(sam_file)
            if sam_path.exists():
                with open(sam_path) as f_in:
                    for line in f_in:
                        if not line.startswith('@'):
                            f_out.write(line)
    
    print(f"Joined {len(sam_files_sorted)} SAM files into aligned.sam")
    
    # Verify output file was created
    output_file = Path("aligned.sam")
    if not output_file.exists():
        print(f"ERROR: aligned.sam was not created", file=sys.stderr)
        sys.exit(1)
    
    print(f"Output file created: {output_file.absolute()} ({output_file.stat().st_size} bytes)")
    PYTHON_SCRIPT
    """
}

