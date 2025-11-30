/*
 * Join Mutation Histograms Process
 * 
 * Merges mutation histogram files from parallel processing into a single file.
 * Handles both pickle (.p) and JSON formats.
 */

process JOIN_MUTATION_HISTOS {
    tag "${sample_id ?: 'single_sample'}"
    label 'process_low'
    
    input:
    tuple val(sample_id), val(mut_histo_p_str), val(mut_histo_json_str), path(fasta), val(is_paired), path(dot_bracket)
    
    output:
    tuple val(sample_id), path("aligned.sam"), path(fasta), val(is_paired), path(dot_bracket), emit: out
    path("mutation_histos.p"), emit: pickle_file
    path("mutation_histos.json"), emit: json_file
    
    publishDir { sample_id ? "${params.output_dir}/${sample_id}/BitVector_Files" : "${params.output_dir}/BitVector_Files" },
        mode: 'copy',
        pattern: 'mutation_histos.*',
        saveAs: { filename -> filename }
    
    script:
    """
    # Create dummy aligned.sam (not used, but required for channel compatibility)
    touch aligned.sam
    
    python3 << 'PYTHON_SCRIPT'
    import sys
    import pickle
    import json
    from pathlib import Path
    
    # mut_histo_p_str and mut_histo_json_str are comma-separated strings of file paths
    mut_histo_p_str = "${mut_histo_p_str}"
    mut_histo_json_str = "${mut_histo_json_str}"
    
    # Split by comma and clean up paths
    pickle_files = [Path(f.strip().strip("'").strip('"')) for f in mut_histo_p_str.split(',') if f.strip()]
    
    # Filter to only existing files
    pickle_files = [f for f in pickle_files if f.exists() and f.suffix == '.p']
    
    if not pickle_files:
        print("WARNING: No mutation histogram pickle files found", file=sys.stderr)
        # Create empty files
        with open("mutation_histos.p", "wb") as f:
            pickle.dump({}, f)
        with open("mutation_histos.json", "w") as f:
            json.dump({}, f)
        sys.exit(0)
    
    # Load and merge all mutation histograms
    from rna_map.analysis.statistics import merge_all_merge_mut_histo_dicts
    
    all_mut_histos = []
    for pickle_file in pickle_files:
        pickle_path = Path(pickle_file)
        if pickle_path.exists():
            with open(pickle_path, "rb") as f:
                mut_histos = pickle.load(f)
                all_mut_histos.append(mut_histos)
    
    if not all_mut_histos:
        print("WARNING: No mutation histograms loaded", file=sys.stderr)
        with open("mutation_histos.p", "wb") as f:
            pickle.dump({}, f)
        with open("mutation_histos.json", "w") as f:
            json.dump({}, f)
        sys.exit(0)
    
    # Merge all mutation histograms
    merged_histos = merge_all_merge_mut_histo_dicts(all_mut_histos)
    
    # Save merged pickle file
    with open("mutation_histos.p", "wb") as f:
        pickle.dump(merged_histos, f)
    
    # Save merged JSON file
    from rna_map.mutation_histogram import write_mut_histos_to_json_file
    write_mut_histos_to_json_file(merged_histos, "mutation_histos.json")
    
    print(f"Merged {len(all_mut_histos)} mutation histogram files")
    print(f"Total sequences: {len(merged_histos)}")
    PYTHON_SCRIPT
    """
}

