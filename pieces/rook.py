
from typing import Optional, Dict, Tuple
from .piece import ChessPiece

class Rook(ChessPiece):
    def __init__(self, color: str) -> None:
        super().__init__(color)
        self.has_moved = False

    def __name__(self) -> str:
        return 'Rook'

    def __str__(self) -> str:
        return '♜' if self.color == 'white' else '♖'

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: list[list[Optional[ChessPiece]]]) -> bool:
        """A rook can move horizontally or vertically as long as the path is clear."""
        start_x, start_y = start
        end_x, end_y = end
        if start_x == end_x or start_y == end_y:
            if self.is_path_clear(start, end, board):
                return True
        return False

    def is_path_clear(self, start: Tuple[int, int], end: Tuple[int, int], board: list[list[Optional[ChessPiece]]]) -> bool:
        """Helper function to check if all squares between start and end are empty."""
        x, y = start
        x2, y2 = end
        dx: int = int((x2 - x) / max(1, abs(x2 - x)))  # Direction along x-axis (1, 0, or -1)
        dy: int = int((y2 - y) / max(1, abs(y2 - y)))  # Direction along y-axis (1, 0, or -1)
        x, y = x + dx, y + dy  # Initialize the next position

        # Move along the path to the end, checking for obstacles
        while (x, y) != (x2, y2):
            if board[x][y] is not None:
                return False  # Found an obstacle
            x, y = x + dx, y + dy  # Move to the next square
        return True

    def legal_moves(self, position: Tuple[int, int], color: str) -> list[Tuple[int, int]]:
        """Generate all the posible legal moves for a rook in a given position."""
        x, y = position
        moves = []

        # Horizontal moves
        for new_x in range(8):
            moves.append((new_x, y))

        # Vertical moves
        for new_y in range(8):
            moves.append((x, new_y))

        return moves
