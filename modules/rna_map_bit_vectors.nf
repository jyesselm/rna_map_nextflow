/*
 * RNA MAP Bit Vector Generation Process
 * 
 * Process for generating bit vectors from SAM files using rna_map Python package.
 * This is specific to RNA MAP analysis but can be reused in other workflows.
 */

process RNA_MAP_BIT_VECTORS {
    tag "${sample_id ?: 'single_sample'}"
    label 'process_high'
    
    input:
    tuple val(sample_id), path(sam), path(fasta), val(is_paired), path(dot_bracket)
    val(qscore_cutoff)
    val(map_score_cutoff)
    val(summary_output_only)
    val(plot_sequence)
    
    output:
    tuple val(sample_id), path("summary.csv"), emit: summary
    tuple val(sample_id), path("BitVector_Files/**"), emit: bitvector_files
    
    publishDir { sample_id ? "${params.output_dir}/${sample_id}/BitVector_Files" : "${params.output_dir}/BitVector_Files" },
        mode: 'copy',
        pattern: 'summary.csv',
        saveAs: { _filename -> 'summary.csv' }
    publishDir { sample_id ? "${params.output_dir}/${sample_id}/BitVector_Files" : "${params.output_dir}/BitVector_Files" },
        mode: 'copy',
        pattern: 'BitVector_Files/**',
        saveAs: { filename -> filename.replace('BitVector_Files/', '') }
    publishDir { sample_id ? "${params.output_dir}/${sample_id}/BitVector_Files" : "${params.output_dir}/BitVector_Files" },
        mode: 'copy',
        pattern: '*.png',
        saveAs: { filename -> filename }
    
    script:
    def dot_bracket_val = (dot_bracket && !dot_bracket.toString().contains(".empty") && dot_bracket.toString() != "") ? dot_bracket.toString() : ""
    def is_paired_py = (is_paired == "True") ? "True" : "False"
    def summary_only_py = summary_output_only ? "True" : "False"
    def plot_sequence_py = plot_sequence ? "True" : "False"
    // Use conda Python if available, otherwise use system python3
    def python_cmd = System.getenv('CONDA_PREFIX') ? "${System.getenv('CONDA_PREFIX')}/bin/python3" : "python3"
    """
    ${python_cmd} << 'PYTHON_SCRIPT'
    import sys
    from pathlib import Path
    from rna_map.pipeline.functions import generate_bit_vectors
    from rna_map.core.config import BitVectorConfig
    
    sam_path = Path("${sam}")
    fasta_path = Path("${fasta}")
    dot_bracket_path = Path("${dot_bracket_val}") if "${dot_bracket_val}" else None
    is_paired = ${is_paired_py}
    
    config = BitVectorConfig(
        qscore_cutoff=${qscore_cutoff},
        map_score_cutoff=${map_score_cutoff},
        summary_output_only=${summary_only_py},
        plot_sequence=${plot_sequence_py}
    )
    
    result = generate_bit_vectors(
        sam_path=sam_path,
        fasta=fasta_path,
        output_dir=Path("."),
        config=config,
        csv_file=dot_bracket_path,
        paired=is_paired
    )
    
    import shutil
    import sys
    if result.summary_path.exists():
        shutil.copy(result.summary_path, "summary.csv")
        print(f"Copied summary to summary.csv from {result.summary_path}")
    else:
        print(f"ERROR: Summary file not found at {result.summary_path}", file=sys.stderr)
        sys.exit(1)
    PYTHON_SCRIPT
    """
}

