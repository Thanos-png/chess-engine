
from typing import Optional, Dict, Tuple
from .piece import ChessPiece
from .pawn import Pawn
from .rook import Rook
from .knight import Knight
from .bishop import Bishop
from .queen import Queen

class King(ChessPiece):
    def __init__(self, color: str) -> None:
        super().__init__(color)
        self.has_moved = False

    def __name__(self) -> str:
        return 'King'

    def __str__(self) -> str:
        return '♚' if self.color == 'white' else '♔'

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: list[list[Optional[ChessPiece]]], board_instance=None) -> bool:
        """A king can move one square in any direction. It can also castle if certain conditions are met."""
        dx: int = abs(start[0] - end[0])
        dy: int = abs(start[1] - end[1])

        # Normal king move
        if (max(dx, dy) == 1):
            return True

        # Castling move
        if dx == 2 and dy == 0 and not self.has_moved:
            row: int = start[1]

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

    def is_in_check(self, color: str, chessboard_instance: 'ChessBoard') -> bool:
        """Determine if the king of the given color is in check."""
        king_position = chessboard_instance.white_king_position if color == 'white' else chessboard_instance.black_king_position
        opponent_color = 'black' if color == 'white' else 'white'

        # Check if any of the opponent's pieces can move to the king's position
        for pos, piece in chessboard_instance.pieces[opponent_color].items():
            if piece.is_valid_move(pos, king_position, chessboard_instance.board):
                return True  # King is in check
        return False

    def get_blocking_squares(self, king_position: Tuple[int, int], checking_position: Tuple[int, int]) -> list[Tuple[int, int]]:
        """Return a list of squares between the king and the checking piece that could potentially block the check."""
        blocking_squares = []
        king_x, king_y = king_position
        check_x, check_y = checking_position
        dx: int = (check_x - king_x) // max(1, abs(check_x - king_x))  # Direction along x-axis
        dy: int = (check_y - king_y) // max(1, abs(check_y - king_y))  # Direction along y-axis

        x, y = king_x + dx, king_y + dy
        while 0 <= x <= 7 and 0 <= y <= 7 and (x, y) != (check_x, check_y) and (x, y) != king_position:
            blocking_squares.append((x, y))
            x += dx
            y += dy
        return blocking_squares

    def get_checking_piece(self, king_position: Tuple[int, int], opponent_color: str, chessboard_instance: 'ChessBoard') -> Tuple[Optional[Tuple[int, int]], Optional[ChessPiece]]:
        """Return the position and piece that is checking the king, if any."""
        for pos, piece in chessboard_instance.pieces[opponent_color].items():
            pos: Tuple[int, int]
            piece: ChessPiece
            if not isinstance(piece, King) and piece.is_valid_move(pos, king_position, chessboard_instance.board):
                return pos, piece
        return None, None

    def legal_moves(self, position: Tuple[int, int], color: str) -> list[Tuple[int, int]]:
        """Generate all the possible legal moves for a king in a given position."""
        x, y = position
        moves = []
    
        # All possible king moves
        potential_moves = [
            (x + 1, y), (x - 1, y),
            (x, y + 1), (x, y - 1),
            (x + 1, y + 1), (x + 1, y - 1),
            (x - 1, y + 1), (x - 1, y - 1),
            (2, 0), (6, 0), (2, 7), (6, 7)  # Castling moves
        ]
    
        # Filter moves within the board
        moves = [(new_x, new_y) for new_x, new_y in potential_moves if 0 <= new_x < 8 and 0 <= new_y < 8]
    
        return moves
