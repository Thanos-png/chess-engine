# Description: Contains utility functions for the chess game.

def parse_position(pos):
    """Returns the x and y position in the board in the form of a tuple(x, y) with 0 <= x <= 7 and 0 <= y <= 7."""
    col, row = pos
    return ord(col) - ord('a'), int(row) - 1

def to_square_notation(position):
    """Convert (x, y) board coordinates to chess notation, e.g. (4, 4) -> 'e5'."""
    col, row = position
    return f"{chr(col + ord('a'))}{row + 1}"
