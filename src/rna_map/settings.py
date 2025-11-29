"""Settings module for RNA MAP package."""

from pathlib import Path


def get_py_path() -> Path:
    """Get the path to the rna_map package directory.
    
    Returns:
        Path to the rna_map package directory containing resources
    """
    return Path(__file__).parent

