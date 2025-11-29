"""Statistical analysis functions for mutation histograms."""

from typing import Any

import pandas as pd

from .mutation_histogram import MutationHistogram


def get_dataframe(
    mut_histos: dict[str, MutationHistogram], data_cols: list[str]
) -> pd.DataFrame:
    """Get DataFrame from mutation histograms.

    Args:
        mut_histos: Dictionary of mutation histograms
        data_cols: List of column names to include

    Returns:
        DataFrame with requested columns

    Raises:
        ValueError: If invalid column name provided
    """
    data = []
    for _, mut_histo in mut_histos.items():
        data_row = [_get_column_value(mut_histo, dc) for dc in data_cols]
        data.append(data_row)
    return pd.DataFrame(data, columns=data_cols)


def _get_column_value(mut_histo: MutationHistogram, column: str) -> Any:
    """Get value for a specific column from mutation histogram.

    Args:
        mut_histo: MutationHistogram object
        column: Column name

    Returns:
        Column value

    Raises:
        ValueError: If invalid column name
    """
    if column == "name":
        return mut_histo.name
    if column == "sequence":
        return mut_histo.sequence
    if column == "structure":
        return mut_histo.structure
    if column in ("num_reads", "reads"):
        return mut_histo.num_reads
    if column == "num_aligned":
        return mut_histo.num_aligned
    if column == "aligned":
        return _calculate_aligned_percentage(mut_histo)
    if column == "num_of_mutations":
        return mut_histo.num_of_mutations
    if column in ("no_mut", "1_mut", "2_mut", "3_mut", "3plus_mut"):
        return _get_mutation_percentage(mut_histo, column)
    if column == "percent_mutations":
        return mut_histo.get_percent_mutations()
    if column in ("signal_to_noise", "sn"):
        return mut_histo.get_signal_to_noise()
    if column == "read_coverage":
        return mut_histo.get_read_coverage()
    if column == "pop_avg":
        return mut_histo.get_pop_avg()
    if column == "pop_avg_del":
        return mut_histo.get_pop_avg(inc_del=True)
    if column == "skips":
        return mut_histo.skips
    if column == "mod_bases":
        return mut_histo.mod_bases
    if column == "mut_bases":
        return mut_histo.mut_bases
    if column == "del_bases":
        return mut_histo.del_bases
    if column == "cov_bases":
        return mut_histo.cov_bases
    if column == "info_bases":
        return mut_histo.info_bases
    raise ValueError(f"Invalid data column: {column}")


def _calculate_aligned_percentage(mut_histo: MutationHistogram) -> float:
    """Calculate aligned percentage.

    Args:
        mut_histo: MutationHistogram object

    Returns:
        Aligned percentage (0.0 if division by zero)
    """
    try:
        return round(float(mut_histo.num_aligned) / float(mut_histo.num_reads) * 100, 2)
    except ZeroDivisionError:
        return 0.0


def _get_mutation_percentage(mut_histo: MutationHistogram, column: str) -> float:
    """Get mutation percentage for specific column.

    Args:
        mut_histo: MutationHistogram object
        column: Column name (no_mut, 1_mut, 2_mut, 3_mut, 3plus_mut)

    Returns:
        Mutation percentage
    """
    percentages = mut_histo.get_percent_mutations()
    index_map = {
        "no_mut": 0,
        "1_mut": 1,
        "2_mut": 2,
        "3_mut": 3,
        "3plus_mut": 4,
    }
    return percentages[index_map[column]]


def merge_mut_histo_dicts(
    left: dict[str, MutationHistogram], right: dict[str, MutationHistogram]
) -> None:
    """Merge two mutation histogram dictionaries.

    The "left" dictionary is updated with values from "right".

    Args:
        left: Dictionary to update (modified in place)
        right: Dictionary to merge from
    """
    for key in right:
        if key in left:
            left[key].merge(right[key])
        else:
            left[key] = right[key]


def merge_all_merge_mut_histo_dicts(
    mut_histos: list[dict[str, MutationHistogram]],
) -> dict[str, MutationHistogram]:
    """Merge all mutation histogram dictionaries.

    Args:
        mut_histos: List of mutation histogram dictionaries

    Returns:
        Merged mutation histogram dictionary
    """
    merged = mut_histos.pop(0)
    for mh in mut_histos:
        merge_mut_histo_dicts(merged, mh)
    return merged
