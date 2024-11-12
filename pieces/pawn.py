# pieces/pawn.py

from .piece import ChessPiece
from utils import parse_position

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return '♙' if self.color == 'white' else '♟'

    def is_valid_move(self, start, end, board, board_instance=None):
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
            if board_instance:
                en_passant_square = board_instance.en_passant_square
                if en_passant_square and end == parse_position(en_passant_square):
                    # Remove the en-passant-captured pawn
                    opponent_color = 'black' if self.color == 'white' else 'white'
                    del board_instance.getPieces()[opponent_color][(end_x, start_y)]
                    board[end_x][start_y] = None
                    return True
        return False
