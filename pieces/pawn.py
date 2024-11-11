# pieces/pawn.py

from .piece import ChessPiece

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return '♙' if self.color == 'white' else '♟'

    def is_valid_move(self, start, end, board, last_move=None):
        """A pawn can move forward one square, or two squares from its starting position. It captures diagonally."""
        direction = 1 if self.color == 'white' else -1
        start_x, start_y = start
        end_x, end_y = end

        # Standard single move forward
        if start_x == end_x and start_y + direction == end_y and board[end_x][end_y] is None:
            return True
        # Initial double move forward
        if start_x == end_x and start_y + 2 * direction == end_y and ((self.color == 'white' and start_y == 1) or (self.color == 'black' and start_y == 6)) and board[end_x][end_y] is None:
            return True
        # Capture one square diagonally
        if abs(start_x - end_x) == 1 and start_y + direction == end_y:
            # Standard capture
            if board[end_x][end_y] is not None:
                return True
            # En passant capture
            if last_move and isinstance(last_move[2], Pawn):
                last_start, last_end, last_piece = last_move
                if last_end == (end_x, start_y) and abs(last_start[1] - last_end[1]) == 2:
                    board[last_end[0]][last_end[1]] = None
                    return True
        return False
