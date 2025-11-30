"""Visualization module for RNA-MAP.

This module contains functions for plotting mutation data,
including population averages, read coverage, and mutation histograms.
"""

from .plots import (
    plot_modified_bases,
    plot_mutation_histogram,
    plot_population_avg,
    plot_read_coverage,
)
from .utils import colors_for_sequence

__all__ = [
    "plot_read_coverage",
    "plot_modified_bases",
    "plot_mutation_histogram",
    "plot_population_avg",
    "colors_for_sequence",
]

