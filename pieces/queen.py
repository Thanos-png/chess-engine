
from .piece import ChessPiece

class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __name__(self):
        return 'Queen'

    def __str__(self):
        return '♕' if self.color == 'white' else '♛'

    def is_valid_move(self, start, end, board):
        """A queen can move horizontally, vertically, or diagonally as long as the path is clear."""
        start_x, start_y = start
        end_x, end_y = end

        # Horizontal or vertical movement (like a Rook)
        if start_x == end_x or start_y == end_y:
            return self.is_path_clear(start, end, board)

        # Diagonal movement (like a Bishop)
        if abs(start_x - end_x) == abs(start_y - end_y):
            return self.is_path_clear(start, end, board)

        return False

    def is_path_clear(self, start, end, board):
        """Helper function to check if all squares between start and end are empty."""
        x, y = start
        x2, y2 = end
        dx = int((x2 - x) / max(1, abs(x2 - x)))  # Direction along x-axis (1, 0, or -1)
        dy = int((y2 - y) / max(1, abs(y2 - y)))  # Direction along y-axis (1, 0, or -1)
        x, y = x + dx, y + dy  # Initialize the next position

        # Move along the path to the end, checking for obstacles
        while (x, y) != (x2, y2):
            if board[x][y] is not None:
                return False  # Found an obstacle
            x, y = x + dx, y + dy  # Move to the next square
        return True

    def legal_moves(self, position, color):
        """Generate all the posible legal moves for a queen in a given position."""
        x, y = position
        moves = []

        # Rook-like moves (horizontal and vertical)
        for new_x in range(8):
            moves.append((new_x, y))
        for new_y in range(8):
            moves.append((x, new_y))

        # Bishop-like moves (diagonals)
        for offset in range(1, 8):
            if x + offset < 8 and y + offset < 8:
                moves.append((x + offset, y + offset))  # Bottom-right diagonal
            if x - offset >= 0 and y - offset >= 0:
                moves.append((x - offset, y - offset))  # Top-left diagonal
            if x + offset < 8 and y - offset >= 0:
                moves.append((x + offset, y - offset))  # Top-right diagonal
            if x - offset >= 0 and y + offset < 8:
                moves.append((x - offset, y + offset))  # Bottom-left diagonal

        return moves
