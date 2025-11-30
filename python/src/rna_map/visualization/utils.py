"""Visualization utilities."""


def colors_for_sequence(seq: str) -> list[str]:
    """Get colors for sequence plotting.

    Args:
        seq: Sequence string

    Returns:
        List of colors (A=red, C=blue, G=orange, T/G=green)
    """
    colors = []
    for e in seq:
        if e == "A":
            colors.append("red")
        elif e == "C":
            colors.append("blue")
        elif e == "G":
            colors.append("orange")
        else:
            colors.append("green")
    return colors

