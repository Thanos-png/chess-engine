# Contains utility functions for the chess game.

from typing import Optional, Dict, Tuple

def parse_position(pos: str) -> Tuple[int, int]:
    """Returns the x and y position in the board in the form of a tuple(x, y) with 0 <= x <= 7 and 0 <= y <= 7."""
    col, row = pos
    return ord(col) - ord('a'), int(row) - 1

def to_square_notation(pos: Tuple[int, int]) -> str:
    """Convert (x, y) board coordinates to chess notation, e.g. (4, 4) -> 'e5'."""
    col, row = pos
    return f"{chr(col + ord('a'))}{row + 1}"
