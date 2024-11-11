
from .piece import ChessPiece

class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return '♘' if self.color == 'white' else '♞'

    def is_valid_move(self, start, end, board):
        """A knight can move 2 squares in one direction and 1 square in a perpendicular direction."""
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])
        return (dx, dy) in [(1, 2), (2, 1)]
