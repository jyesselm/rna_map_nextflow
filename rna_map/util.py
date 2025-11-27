"""Utility functions for RNA MAP (backward compatibility).

This module re-exports functions from the new io module for backward compatibility.
"""

from pathlib import Path

# Re-export from new io module for backward compatibility


def get_filename(path):
    """Get the filename from a path
    :param path: the path
    :return: the filename
    """
    path = Path(Path(path).stem)
    return str(path).rstrip("".join(path.suffixes))
