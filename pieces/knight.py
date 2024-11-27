
from .piece import ChessPiece

class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __name__(self):
        return 'Knight'

    def __str__(self):
        return '♘' if self.color == 'white' else '♞'

    def is_valid_move(self, start, end, board):
        """A knight can move 2 squares in one direction and 1 square in a perpendicular direction."""
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])
        return (dx, dy) in [(1, 2), (2, 1)]

    def legal_moves(self, position, color):
        """Generate all the possible legal moves for a knight in a given position."""
        x, y = position
        moves = []

        # All possible L-shaped moves
        potential_moves = [
            (x + 2, y + 1), (x + 2, y - 1),
            (x - 2, y + 1), (x - 2, y - 1),
            (x + 1, y + 2), (x + 1, y - 2),
            (x - 1, y + 2), (x - 1, y - 2),
        ]

        # Filter moves within the board
        moves = [(new_x, new_y) for new_x, new_y in potential_moves if 0 <= new_x < 8 and 0 <= new_y < 8]

        return moves
