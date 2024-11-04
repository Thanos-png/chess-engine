#!/usr/bin/env python3

class ChessPiece:
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, start, end, board):
        raise NotImplementedError("This method should be implemented by subclasses.")


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


class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return '♖' if self.color == 'white' else '♜'

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
        return '♘' if self.color == 'white' else '♞'

    def is_valid_move(self, start, end, board):
        """A knight can move 2 squares in one direction and 1 square in a perpendicular direction."""
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])
        return (dx, dy) in [(1, 2), (2, 1)]


class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        return '♗' if self.color == 'white' else '♝'

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


class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def __str__(self):
        return '♔' if self.color == 'white' else '♚'

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
        self.pieces = {'white': {}, 'black': {}}  # Track all pieces by color and position
        self.setup_board()
        self.white_king_position = (4, 0)
        self.black_king_position = (4, 7)

    def setup_board(self):
        """Sets up the chess board with pieces in their initial positions."""
        for i in range(8):
            self.board[i][1] = Pawn('white')
            self.pieces['white'][(i, 1)] = self.board[i][1]
            self.board[i][6] = Pawn('black')
            self.pieces['black'][(i, 6)] = self.board[i][6]

        placements = [
            Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
        ]
        for i, piece in enumerate(placements):
            self.board[i][0] = piece('white')
            self.pieces['white'][(i, 0)] = self.board[i][0]
            self.board[i][7] = piece('black')
            self.pieces['black'][(i, 7)] = self.board[i][7]

    def update_piece_position(self, start, end):
        """Update the pieces dictionary after a move."""
        piece = self.board[end[0]][end[1]]
        color = piece.color
        if start in self.pieces[color]:
            del self.pieces[color][start]
        self.pieces[color][end] = piece

        # Remove captured piece from the opponent's dictionary, if any
        opponent_color = 'black' if color == 'white' else 'white'
        if end in self.pieces[opponent_color]:
            del self.pieces[opponent_color][end]

    def display(self):
        """Prints the chess board after every move."""
        print("\n  a b c d e f g h")
        for y in range(7, -1, -1):
            print(f"{y+1} ", end="")
            for x in range(8):
                piece = self.board[x][y]
                print(str(piece) if piece else '.', end=" ")
            print(f"{y+1}")
        print("  a b c d e f g h\n")

    def promote_pawn(self, position, color):
        """Promote a pawn that reaches the final rank to a new piece chosen by the player."""
        x, y = position
        while True:
            choice = input("Promote pawn to (Q)ueen, (R)ook, (B)ishop, or (K)night: ").strip().upper()
            if choice == 'Q':
                self.board[x][y] = Queen(color)
                break
            elif choice == 'R':
                self.board[x][y] = Rook(color)
                break
            elif choice == 'B':
                self.board[x][y] = Bishop(color)
                break
            elif choice == 'K':
                self.board[x][y] = Knight(color)
                break
            else:
                print("Invalid choice. Please select Q, R, B, or K.")
        
        # Update pieces dictionary to reflect the promoted piece
        self.pieces[color][position] = self.board[x][y]

    def move_piece(self, start, end, color, last_move):
        """Moves a piece from the start position to the end position if it is a valid move."""
        if (start == end):
            return False

        start_x, start_y = start
        end_x, end_y = end

        if start_x < 0 or start_x > 7 or start_y < 0 or start_y > 7 or end_x < 0 or end_x > 7 or end_y < 0 or end_y > 7:
            return False

        piece = self.board[start_x][start_y]  # Piece at the start square
        target_piece = self.board[end_x][end_y]  # Piece at the target square(if any)

        # Check if the destination square contains a piece of the same color
        if target_piece and target_piece.color == color:
            return False

        # Check if the piece at the start square is of the correct color
        if piece and piece.color == color:
            if isinstance(piece, King):
                if piece.is_valid_move(start, end, self.board):
                    if self.move_piece_helper(start, end, self.board, color):
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
                        if (color == "white"):
                            self.white_king_position = (end_x, end_y)
                        else:
                            self.black_king_position = (end_x, end_y)
                        return True
                    return False
            if isinstance(piece, Pawn) and last_move and isinstance(last_move[2], Pawn) and piece.is_valid_move(start, end, self.board, last_move):
                if self.move_piece_helper(start, end, self.board, color):
                    # Check for pawn promotion
                    if (color == 'white' and end_y == 7) or (color == 'black' and end_y == 0):
                        self.promote_pawn((end_x, end_y), color)
                    return True
            if piece.is_valid_move(start, end, self.board):
                if self.move_piece_helper(start, end, self.board, color):
                    # Check for pawn promotion
                    if (color == 'white' and end_y == 7) or (color == 'black' and end_y == 0):
                        self.promote_pawn((end_x, end_y), color)
                    return True
        return False

    def move_piece_helper(self, start, end, board, color):
        """Check if a move is legal before playing it and update the board accordingly."""
        start_x, start_y = start
        end_x, end_y = end
        piece = self.board[start_x][start_y]  # Piece at the start square
        target_piece = self.board[end_x][end_y]  # Piece at the target square(if any)

        # Save the state of the board for check validation
        self.board[end_x][end_y] = piece
        self.board[start_x][start_y] = None
        
        # Check if this move leaves the king in check
        if self.is_in_check(color):
            # Revert move if it results in check
            self.board[start_x][start_y] = piece
            self.board[end_x][end_y] = target_piece
            return False

        self.update_piece_position(start, end)
        return True

    def is_in_check(self, color):
        """Determine if the king of the given color is in check."""
        king_position = self.white_king_position if color == 'white' else self.black_king_position
        opponent_color = 'black' if color == 'white' else 'white'

        # Check if any of the opponent's pieces can move to the king's position
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece and piece.color == opponent_color:
                    if piece.is_valid_move((x, y), king_position, self.board):
                        return True
        return False

    def get_blocking_squares(self, king_position, checking_position):
        """Return a list of squares between the king and the checking piece that could potentially block the check."""
        blocking_squares = []
        king_x, king_y = king_position
        check_x, check_y = checking_position
        dx = (check_x - king_x) // max(1, abs(check_x - king_x))  # Direction along x-axis
        dy = (check_y - king_y) // max(1, abs(check_y - king_y))  # Direction along y-axis

        x, y = king_x + dx, king_y + dy
        while 0 <= x <= 7 and 0 <= y <= 7 and (x, y) != (check_x, check_y) and (x, y) != king_position:
            blocking_squares.append((x, y))
            x += dx
            y += dy
        return blocking_squares

    def get_checking_piece(self, king_position, opponent_color):
        """Return the position and piece that is checking the king, if any."""
        for pos, piece in self.pieces[opponent_color].items():
            if piece.is_valid_move(pos, king_position, self.board):
                return pos, piece
        return None, None

    # def has_legal_moves(self, color, in_check=None):   # Sometimes we already know the king is in check
    def has_legal_moves(self, color):
        """Determine if the player has any legal moves remaining.
        If the king is in check, check if there is a way to escape check (either by moving the king,
        blocking the check, or capturing the checking piece). If no escape is possible, declare checkmate.
        If the player has no legal moves but isn't in check, declare stalemate."""
        king_position = self.white_king_position if color == 'white' else self.black_king_position
        opponent_color = 'black' if color == 'white' else 'white'

        # Check if the king is currently in check 
        in_check = self.is_in_check(color)
        protected_piece = False  # Flag to check if the piece that is checking the king is protected

        # Check if the king can escape check by moving to a different square
        if in_check:
            # Identify the piece that is checking the king
            checking_position, checking_piece = self.get_checking_piece(king_position, opponent_color)

            # Generate all possible moves for the king (1 square in each direction)
            king_x, king_y = king_position
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                new_x, new_y = king_x + dx, king_y + dy
                # Check if the square that the king is trying to move to is inside the board
                if 0 <= new_x <= 7 and 0 <= new_y <= 7:
                    # Checks if the square that the king is trying to move to is blocked
                    if self.board[new_x][new_y] is None or self.board[new_x][new_y].color == opponent_color:
                        # Move the king to that square temporarily
                        piece = self.board[new_x][new_y]
                        self.board[new_x][new_y] = self.board[king_x][king_y]
                        self.board[king_x][king_y] = None
                        king_position = new_x, new_y
                        if (color == "white"):
                            self.white_king_position = king_position
                        else:
                            self.black_king_position = king_position

                        # Check if the piece that the king is trying to capture is protected is protected
                        if (not self.get_checking_piece(king_position, opponent_color) == (None, None)):
                            protected_piece = True

                        # Check if this move takes the king out of check
                        if not self.is_in_check(color):
                            # Undo the move and return True (legal escape found)
                            self.board[king_x][king_y] = self.board[new_x][new_y]
                            self.board[new_x][new_y] = piece
                            print(f"{color.capitalize()} is in check.")
                            king_position = king_x, king_y
                            if (color == "white"):
                                self.white_king_position = king_position
                            else:
                                self.black_king_position = king_position
                            return True

                        # Undo the move
                        self.board[king_x][king_y] = self.board[new_x][new_y]
                        self.board[new_x][new_y] = piece
                        king_position = king_x, king_y
                        if (color == "white"):
                            self.white_king_position = king_position
                        else:
                            self.black_king_position = king_position

            if (not protected_piece):
                # Check if we can capture the checking piece
                for pos, piece in self.pieces[color].items():
                    if piece.is_valid_move(pos, checking_position, self.board):
                        # Temporarily make the capture
                        captured_piece = self.board[checking_position[0]][checking_position[1]]
                        self.board[checking_position[0]][checking_position[1]] = piece
                        self.board[pos[0]][pos[1]] = None

                        if not self.is_in_check(color):
                            # Undo move and return True (legal move found)
                            self.board[pos[0]][pos[1]] = piece
                            self.board[checking_position[0]][checking_position[1]] = captured_piece
                            print(f"{color.capitalize()} is in check.")
                            return True

                        # Undo the move
                        self.board[pos[0]][pos[1]] = piece
                        self.board[checking_position[0]][checking_position[1]] = captured_piece

            # Check if we can block the check by moving a piece between the king and the checking piece
            if isinstance(checking_piece, (Rook, Bishop, Queen)):
                blocking_squares = self.get_blocking_squares(king_position, checking_position)
                for pos, piece in self.pieces[color].items():
                    for square in blocking_squares:
                        if not isinstance(piece, King) and piece.is_valid_move(pos, square, self.board):
                            # Temporarily make the block
                            original_piece = self.board[square[0]][square[1]]
                            self.board[square[0]][square[1]] = piece
                            self.board[pos[0]][pos[1]] = None

                            if not self.is_in_check(color):
                                # Undo move and return True (legal move found)
                                self.board[pos[0]][pos[1]] = piece
                                self.board[square[0]][square[1]] = original_piece
                                print(f"{color.capitalize()} is in check.")
                                return True

                            # Undo the move
                            self.board[pos[0]][pos[1]] = piece
                            self.board[square[0]][square[1]] = original_piece

            # No legal moves were found and the king is in check, so it's checkmate
            print(f"Checkmate! {('Black' if color == 'white' else 'White')} wins!")
            return False

        # If not in check, check for any legal moves (stalemate)
        for pos, piece in self.pieces[color].items():
            for dx in range(8):
                for dy in range(8):
                    if piece.is_valid_move(pos, (dx, dy), self.board):
                        # Temporarily make the move
                        target_piece = self.board[dx][dy]
                        self.board[dx][dy] = piece
                        self.board[pos[0]][pos[1]] = None

                        # Check if this move leaves the king in check
                        if not self.is_in_check(color):
                            # Undo the move and return True (legal move found)
                            self.board[pos[0]][pos[1]] = piece
                            self.board[dx][dy] = target_piece
                            return True

                        # Undo the move
                        self.board[pos[0]][pos[1]] = piece
                        self.board[dx][dy] = target_piece

        # No legal moves were found and the king is not in check, so it's stalemate
        print("Stalemate! The game is a draw.")
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

        # Check for checkmate or stalemate
        if not board.has_legal_moves(turn):
            break

        move = input("Enter your move: ").strip().lower()

        try:
            start_str, end_str = move.split()
            start = parse_position(start_str)
            end = parse_position(end_str)
            piece = board.board[start[0]][start[1]]

            if piece and piece.color == turn:
                if board.move_piece(start, end, turn, last_move):
                    last_move = (start, end, piece)
                    turn = 'black' if turn == 'white' else 'white'
                else:
                    print("""
Invalid move, try again.
                    """)
            else:
                print("""
No valid piece to move at that position.
                """)
        except (ValueError, IndexError):
            print("""
Invalid input, format should be 'e2 e4'.
            """)

if __name__ == "__main__":
    main()
