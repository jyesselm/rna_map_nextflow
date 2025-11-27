"""Plotting functions for mutation data visualization."""

import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.io as pio

from rna_map.logger import get_logger

from .utils import colors_for_sequence

log = get_logger("VISUALIZATION")


# Global variable for Kaleido support
def _get_kaleido_exists() -> bool:
    """Check if Kaleido is available.

    Returns:
        True if Kaleido is available, False otherwise
    """
    try:
        pio.kaleido.scope.chromium_args += ("--single-process",)
        return True
    except:
        return False


_kaleido_exists = _get_kaleido_exists()


def plot_read_coverage(
    nuc_pos: list[int], read_coverage: list[float], fname: str
) -> None:
    """Plot read coverage.

    Args:
        nuc_pos: List of nucleotide positions
        read_coverage: Coverage values
        fname: Output file path
    """
    cov_trace = go.Bar(x=nuc_pos, y=read_coverage)
    cov_layout = go.Layout(
        title="Read coverage: " + ", Number of bit vectors: " + str(max(read_coverage)),
        xaxis=dict(title="Position"),
        yaxis=dict(title="Coverage fraction"),
    )
    cov_fig = go.Figure(data=[cov_trace], layout=cov_layout)
    plotly.offline.plot(cov_fig, filename=fname, auto_open=False)


def plot_modified_bases(
    nuc_pos: list[int], mod_bases: dict[str, list[float]], fname: str
) -> None:
    """Plot modified bases.

    Args:
        nuc_pos: List of nucleotide positions
        mod_bases: Dictionary of modified base counts by nucleotide
        fname: Output file path
    """
    modbases_data = []
    cmap = {"A": "red", "T": "green", "G": "orange", "C": "blue"}
    for base in cmap:
        y_list = [mod_bases[base][pos] for pos in nuc_pos]
        trace = go.Bar(x=nuc_pos, y=y_list, name=base, marker_color=cmap[base])
        modbases_data.append(trace)
    modbases_layout = go.Layout(
        title="DMS modifications: ",
        xaxis=dict(title="Position"),
        yaxis=dict(title="Abundance"),
        barmode="stack",
    )
    modbases_fig = go.Figure(data=modbases_data, layout=modbases_layout)
    plotly.offline.plot(modbases_fig, filename=fname, auto_open=False)


def plot_mutation_histogram(
    nuc_pos: list[int], num_of_mutations: list[int], fname: str
) -> None:
    """Plot mutation histogram.

    Args:
        nuc_pos: List of nucleotide positions
        num_of_mutations: Mutation counts
        fname: Output file path
    """
    mut_hist_data = go.Bar(x=nuc_pos, y=num_of_mutations)
    mut_hist_layout = go.Layout(
        title="Mutations: ",
        xaxis=dict(title="Number of mutations per read"),
        yaxis=dict(title="Abundance"),
    )
    mut_hist_fig = go.Figure(data=mut_hist_data, layout=mut_hist_layout)
    plotly.offline.plot(mut_hist_fig, filename=fname, auto_open=False)


def plot_population_avg(
    df: pd.DataFrame, name: str, fname: str, plot_sequence: bool = False
) -> None:
    """Plot population average.

    Args:
        df: DataFrame with position, mismatches, and nuc columns
        name: Plot title
        fname: Output file path
        plot_sequence: Whether to plot sequence on x-axis
    """
    colors = colors_for_sequence(df["nuc"])
    mut_trace = go.Bar(
        x=list(df["position"]),
        y=list(df["mismatches"]),
        text=list(df["nuc"]),
        marker=dict(color=colors),
        showlegend=False,
    )
    mut_fig_layout = go.Layout(
        title=name,
        xaxis=dict(title="Position"),
        yaxis=dict(title="Fraction", range=[0, 0.1]),
        plot_bgcolor="white",
    )
    mut_fig = go.Figure(data=mut_trace, layout=mut_fig_layout)
    seqs = list(df["nuc"])
    db = list(df["structure"]) if "structure" in df.columns else [" "] * len(seqs)
    mut_fig.update_yaxes(
        gridcolor="lightgray", linewidth=1, linecolor="black", mirror=True
    )
    mut_fig.update_xaxes(linewidth=1, linecolor="black", mirror=True)
    if plot_sequence:
        mut_fig.update_xaxes(
            tickvals=list(df["position"]),
            ticktext=[f"{x}<br>{y}" for (x, y) in zip(seqs, db, strict=True)],
            tickangle=0,
        )
    plotly.offline.plot(mut_fig, filename=fname, auto_open=False)
    if _kaleido_exists:
        file_path = fname[:-5] + ".png"
        mut_fig.write_image(file_path, height=400, width=1000)
    else:
        log.warn("Kaleido not installed, skipping output to png")
