#!/usr/bin/env python3

######################################## Missing implementation for the case that the piece is pinned to the king ########################################
class ChessPiece:
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, start, end, board):
        raise NotImplementedError("This method should be implemented by subclasses.")


class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return 'P' if self.color == 'white' else 'p'

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
                    return True
        return False


class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return 'R' if self.color == 'white' else 'r'

    def is_valid_move(self, start, end, board):
        """A rook can move horizontally or vertically as long as the path is clear."""
        start_x, start_y = start
        end_x, end_y = end
        if start_x == end_x or start_y == end_y:
            if self.is_path_clear(start, end, board):
                self.has_moved = True
                return True
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


class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return 'N' if self.color == 'white' else 'n'

    def is_valid_move(self, start, end, board):
        """A knight can move 2 squares in one direction and 1 square in a perpendicular direction."""
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])
        return (dx, dy) in [(1, 2), (2, 1)]


class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return 'B' if self.color == 'white' else 'b'

    def is_valid_move(self, start, end, board):
        """A bishop can move diagonally as long as the path is clear."""
        start_x, start_y = start
        end_x, end_y = end
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


class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return 'Q' if self.color == 'white' else 'q'

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


class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return 'K' if self.color == 'white' else 'k'

    ######################################## Missing implementation for the case that the squares are under enemy control ########################################
    def is_valid_move(self, start, end, board):
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
            if end[0] == 6 and isinstance(board[7][row], Rook) and not board[7][row].has_moved:  # Check if rook is there and hasn't moved
                return board[5][row] is None and board[6][row] is None
            # Queenside castling
            elif end[0] == 2 and isinstance(board[0][row], Rook) and not board[0][row].has_moved:  # Check if rook is there and hasn't moved
                return board[1][row] is None and board[2][row] is None and board[3][row] is None
        return False


class ChessBoard:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.setup_board()

    def setup_board(self):
        """Sets up the chess board with pieces in their initial positions."""
        for i in range(8):
            self.board[i][1] = Pawn('white')
            self.board[i][6] = Pawn('black')

        placements = [
            Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
        ]
        for i, piece in enumerate(placements):
            self.board[i][0] = piece('white')
            self.board[i][7] = piece('black')

    def display(self):
        """Prints the chess board after every move."""
        print("  a b c d e f g h")
        for y in range(7, -1, -1):
            print(f"{y+1} ", end="")
            for x in range(8):
                piece = self.board[x][y]
                print(str(piece) if piece else '.', end=" ")
            print(f"{y+1}")
        print("  a b c d e f g h\n")

    def move_piece(self, start, end, color):
        """Moves a piece from the start position to the end position if it is a valid move."""
        if (start == end):
            return False

        start_x, start_y = start
        end_x, end_y = end

        if start_x < 0 or start_x > 7 or start_y < 0 or start_y > 7 or end_x < 0 or end_x > 7 or end_y < 0 or end_y > 7:
            return False

        piece = self.board[start_x][start_y]

        if piece and piece.color == color:
            if isinstance(piece, King):
                piece.is_valid_move(start, end, self.board)

                self.has_moved = True
                # Castling move
                if abs(start[0] - end[0]) == 2:
                    row = start[1]
                    if end[0] == 6:  # Kingside
                        self.board[5][row] = self.board[7][row]
                        self.board[7][row] = None
                    elif end[0] == 2:  # Queenside
                        self.board[3][row] = self.board[0][row]
                        self.board[0][row] = None
                self.board[end_x][end_y] = piece
                self.board[start_x][start_y] = None
                return True
            if piece.is_valid_move(start, end, self.board):
                self.board[end_x][end_y] = piece
                self.board[start_x][start_y] = None
                return True
        return False


def parse_position(pos):
    """Returns the x and y position in the board in the form of a tuple(x, y) with 0=<x=<7 and 0=<y=<7."""
    col, row = pos
    return ord(col) - ord('a'), int(row) - 1


def main():
    board = ChessBoard()
    turn = 'white'
    last_move = None  # To track last move for en passant
    
    while True:
        board.display()
        print(f"{turn.capitalize()}'s move")
        move = input("Enter your move: ").strip().lower()

        try:
            start_str, end_str = move.split()
            start = parse_position(start_str)
            end = parse_position(end_str)
            piece = board.board[start[0]][start[1]]

            if piece and piece.color == turn:
                if board.move_piece(start, end, turn):
                    last_move = (start, end, piece)
                    turn = 'black' if turn == 'white' else 'white'
                else:
                    print("Invalid move, try again.")
            else:
                print("No valid piece to move at that position.")
        except (ValueError, IndexError):
            print("Invalid input, format should be 'e2 e4'.")

if __name__ == "__main__":
    main()
