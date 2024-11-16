
from .piece import ChessPiece
from utils import parse_position
from .rook import Rook
from .knight import Knight
from .bishop import Bishop
from .queen import Queen

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return '♙' if self.color == 'white' else '♟'

    def is_valid_move(self, start, end, board, chessboard_instance=None):
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
            if chessboard_instance:
                en_passant_square = chessboard_instance.en_passant_square
                if en_passant_square and end == parse_position(en_passant_square):
                    # Remove the en-passant-captured pawn
                    board[end_x][start_y] = None
                    return True
        return False

    def promote_pawn(self, position, color, chessboard_instance):
        """Promote a pawn that reaches the final rank to a new piece chosen by the player."""
        x, y = position
        while True:
            choice = input("Promote pawn to (Q)ueen, (R)ook, (B)ishop, or (K)night: ").strip().upper()
            if choice == 'Q':
                chessboard_instance.board[x][y] = Queen(color)
                break
            elif choice == 'R':
                chessboard_instance.board[x][y] = Rook(color)
                break
            elif choice == 'B':
                chessboard_instance.board[x][y] = Bishop(color)
                break
            elif choice == 'K':
                chessboard_instance.board[x][y] = Knight(color)
                break
            else:
                print("Invalid choice. Please select Q, R, B, or K.")
        
        # Update pieces dictionary to reflect the promoted piece
        chessboard_instance.pieces[color][position] = chessboard_instance.board[x][y]
