
from .piece import ChessPiece

class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return '♔' if self.color == 'white' else '♚'

    def is_valid_move(self, start, end, board, board_instance=None):
        """A king can move one square in any direction. It can also castle if certain conditions are met."""
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])

        # Normal king move
        if (max(dx, dy) == 1):
            return True

        # Castling move
        if dx == 2 and dy == 0 and not self.has_moved:
            row = start[1]

            # Kingside castling
            if end[0] == 6:
                if isinstance(board[7][row], Rook) and not board[7][row].has_moved and board_instance:  # Check if rook is there and hasn't moved
                    # Check if path is clear and safe (f1 and g1 for white, f8 and g8 for black)
                    if (board[5][row] is None and board[6][row] is None and
                        not board_instance.is_square_under_attack((5, row), self.color) and
                        not board_instance.is_square_under_attack((6, row), self.color)):
                        return True
            
            # Queenside castling
            elif end[0] == 2:
                if isinstance(board[0][row], Rook) and not board[0][row].has_moved and board_instance:  # Check if rook is there and hasn't moved
                    # Check if path is clear and safe (d1, c1, and b1 for white; d8, c8, and b8 for black)
                    if (board[1][row] is None and board[2][row] is None and board[3][row] is None and
                        not board_instance.is_square_under_attack((2, row), self.color) and
                        not board_instance.is_square_under_attack((3, row), self.color)):
                        return True
        return False
