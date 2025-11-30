"""Plotting functions for mutation data visualization."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

from typing import List

from rna_map.logger import get_logger

from .utils import colors_for_sequence

log = get_logger("VISUALIZATION")


def sequence_and_structure_x_axis(
    ax: plt.Axes, sequence: str, structure: str, x_delta: int = 1
) -> plt.Axes:
    """Set the x-axis of the given matplotlib Axes to display both the sequence and secondary structure.

    The x-axis tick labels will show each nucleotide in the sequence, with the corresponding
    secondary structure character below it (separated by a newline).

    Args:
        ax: The matplotlib Axes object to modify.
        sequence: The RNA or DNA sequence string.
        structure: The secondary structure string (e.g., dot-bracket notation),
            same length as sequence.
        x_delta: Delta value for x-axis limits.

    Returns:
        The modified matplotlib Axes object with updated x-axis tick labels.
    """
    x = list(range(len(sequence)))
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n{nt}" for s, nt in zip(sequence, structure, strict=True)])
    ax.set_xlim([-x_delta, len(sequence) + x_delta])
    return ax


def plot_read_coverage(
    nuc_pos: list[int], read_coverage: list[float], fname: str
) -> None:
    """Plot read coverage.

    Args:
        nuc_pos: List of nucleotide positions
        read_coverage: Coverage values
        fname: Output PNG file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(nuc_pos, read_coverage)
    ax.set_xlabel("Position")
    ax.set_ylabel("Coverage fraction")
    ax.set_title(f"Read coverage, Number of bit vectors: {max(read_coverage)}")
    ax.grid(True, alpha=0.3)
    fig.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_modified_bases(
    nuc_pos: list[int], mod_bases: dict[str, list[float]], fname: str
) -> None:
    """Plot modified bases.

    Args:
        nuc_pos: List of nucleotide positions (1-indexed)
        mod_bases: Dictionary of modified base counts by nucleotide (1-indexed arrays)
        fname: Output PNG file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = {"A": "red", "T": "green", "G": "orange", "C": "blue"}

    bottom = [0.0] * len(nuc_pos)
    for base in ["A", "C", "G", "T"]:
        if base in mod_bases:
            y_list = [mod_bases[base][pos] for pos in nuc_pos]
            ax.bar(nuc_pos, y_list, bottom=bottom, label=base, color=cmap[base])
            bottom = [b + y for b, y in zip(bottom, y_list, strict=True)]

    ax.set_xlabel("Position")
    ax.set_ylabel("Abundance")
    ax.set_title("DMS modifications")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_mutation_histogram(
    nuc_pos: list[int], num_of_mutations: list[int], fname: str
) -> None:
    """Plot mutation histogram.

    Args:
        nuc_pos: List of nucleotide positions
        num_of_mutations: Mutation counts
        fname: Output PNG file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(nuc_pos, num_of_mutations)
    ax.set_xlabel("Number of mutations per read")
    ax.set_ylabel("Abundance")
    ax.set_title("Mutations")
    ax.grid(True, alpha=0.3)
    fig.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_population_avg(
    df: pd.DataFrame, name: str, fname: str, plot_sequence: bool = False
) -> None:
    """Plot population average.

    Args:
        df: DataFrame with position, mismatches, and nuc columns
        name: Plot title
        fname: Output PNG file path
        plot_sequence: Whether to plot sequence and structure on x-axis
            (automatically disabled if no structure data available)
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = colors_for_sequence(df["nuc"])

    # Check if structure data is available
    has_structure = "structure" in df.columns and df["structure"].notna().any()
    
    if plot_sequence and not has_structure:
        log.warn(
            "plot_sequence=True but no structure data available "
            "(no dot-bracket file provided). Disabling sequence/structure x-axis."
        )
        plot_sequence = False

    if plot_sequence and has_structure:
        x_positions = list(range(len(df)))
        bars = ax.bar(
            x_positions,
            df["mismatches"],
            color=colors,
        )
        seqs = "".join(df["nuc"])
        db = "".join(df["structure"])
        if len(seqs) == len(db):
            sequence_and_structure_x_axis(ax, seqs, db)
        else:
            log.warn(
                f"Sequence length ({len(seqs)}) != structure length ({len(db)}), "
                "skipping sequence/structure x-axis"
            )
            ax.set_xticks(x_positions)
            ax.set_xlabel("Position")
    else:
        bars = ax.bar(
            df["position"],
            df["mismatches"],
            color=colors,
        )
        ax.set_xlabel("Position")

    ax.set_ylabel("Fraction")
    ax.set_title(name)
    ax.set_ylim(0, 0.1)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_axisbelow(True)

    fig.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close(fig)
