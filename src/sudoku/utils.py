"""
Utility functions.
"""
from typing import Callable, TypeVar

T = TypeVar("T")


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp a value to a range."""
    return max(min_val, min(max_val, value))


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        m, s = divmod(int(seconds), 60)
        return f"{m}m {s}s"
    else:
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h}h {m}m"


def box_index(row: int, col: int) -> int:
    """Get the 3x3 box index (0-8) for a cell."""
    return (row // 3) * 3 + (col // 3)


def is_same_box(r1: int, c1: int, r2: int, c2: int) -> bool:
    """Check if two cells are in the same 3x3 box."""
    return box_index(r1, c1) == box_index(r2, c2)
