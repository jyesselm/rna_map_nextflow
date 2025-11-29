"""Mutation histogram module - I/O and analysis functions.

The MutationHistogram class has been moved to rna_map.analysis.mutation_histogram.
Statistical functions have been moved to rna_map.analysis.statistics.
Plotting functions have been moved to rna_map.visualization.
This file maintains backward compatibility.
"""

import json
import pickle

# Import from new modules
from rna_map.analysis.mutation_histogram import MutationHistogram
from rna_map.analysis.statistics import (
    get_dataframe,
    merge_all_merge_mut_histo_dicts,
    merge_mut_histo_dicts,
)
from rna_map.visualization import (
    colors_for_sequence,
    plot_modified_bases,
    plot_mutation_histogram,
    plot_population_avg,
    plot_read_coverage,
)

# Re-export for backward compatibility
__all__ = [
    "MutationHistogram",
    "get_dataframe",
    "merge_mut_histo_dicts",
    "merge_all_merge_mut_histo_dicts",
    "write_mut_histos_to_json_file",
    "write_mut_histos_to_pickle_file",
    "get_mut_histos_from_json_file",
    "get_mut_histos_from_pickle_file",
    "convert_dreem_mut_histos_to_mutation_histogram",
    "colors_for_sequence",
    "plot_read_coverage",
    "plot_modified_bases",
    "plot_mutation_histogram",
    "plot_population_avg",
    "merge_mut_histo_files",
]


def convert_dreem_mut_histos_to_mutation_histogram(mhs) -> dict[str, MutationHistogram]:
    """Convert DREEM mutation histograms to MutationHistogram format.

    Args:
        mhs: Dictionary of DREEM mutation histograms

    Returns:
        Dictionary of MutationHistogram objects
    """
    new_mhs = {}
    for name, mh in mhs.items():
        new_mh = MutationHistogram(name, mh.sequence, mh.data_type)
        new_mh.structure = mh.structure
        new_mh.num_reads = mh.num_reads
        new_mh.num_aligned = mh.num_aligned
        new_mh.skips = mh.skips
        new_mh.num_of_mutations = mh.num_of_mutations
        new_mh.mut_bases = mh.mut_bases
        new_mh.info_bases = mh.info_bases
        new_mh.del_bases = mh.del_bases
        new_mh.ins_bases = mh.ins_bases
        new_mh.cov_bases = mh.cov_bases
        new_mh.mod_bases["A"] = mh.mod_bases["A"]
        new_mh.mod_bases["C"] = mh.mod_bases["C"]
        new_mh.mod_bases["G"] = mh.mod_bases["G"]
        new_mh.mod_bases["T"] = mh.mod_bases["T"]
        new_mhs[name] = new_mh
    return new_mhs


def write_mut_histos_to_json_file(
    mut_histos: dict[str, MutationHistogram], fname: str
) -> None:
    """Write mutation histograms to JSON file.

    Args:
        mut_histos: Dictionary of mutation histograms
        fname: Output file path
    """
    with open(fname, "w", encoding="utf8") as f:
        json.dump({k: v.get_dict() for k, v in mut_histos.items()}, f)


def write_mut_histos_to_pickle_file(
    mut_histos: dict[str, MutationHistogram], fname: str
) -> None:
    """Write mutation histograms to pickle file.

    Args:
        mut_histos: Dictionary of mutation histograms
        fname: Output file path
    """
    with open(fname, "wb") as f:
        pickle.dump(mut_histos, f)


def get_mut_histos_from_json_file(fname: str) -> dict[str, MutationHistogram]:
    """Load mutation histograms from JSON file.

    Args:
        fname: Input file path

    Returns:
        Dictionary of mutation histograms
    """
    with open(fname) as f:
        data = json.load(f)
    return {k: MutationHistogram.from_dict(v) for k, v in data.items()}


def get_mut_histos_from_pickle_file(fname: str) -> dict[str, MutationHistogram]:
    """Load mutation histograms from pickle file.

    Args:
        fname: Input file path

    Returns:
        Dictionary of mutation histograms
    """
    with open(fname, "rb") as f:
        data = pickle.load(f)
    return data


def merge_mut_histo_files(mh_files, outdir, kind="pickle") -> None:
    """Merge mutation histogram files.

    Args:
        mh_files: List of mutation histogram file paths
        outdir: Output directory
        kind: File type ("pickle" or "json")
    """
    mut_histos = []
    for mh_file in mh_files:
        if kind == "pickle":
            mut_histos.append(get_mut_histos_from_pickle_file(mh_file))
        else:
            mut_histos.append(get_mut_histos_from_json_file(mh_files))
    merged = merge_all_merge_mut_histo_dicts(mut_histos)
    write_mut_histos_to_pickle_file(merged, outdir + "mutation_histos.p")
    write_mut_histos_to_json_file(merged, outdir + "mutation_histos.json")
