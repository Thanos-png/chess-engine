
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King

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

    def is_square_under_attack(self, square, color):
        """Check if a square is under attack by any piece of the opponent's color."""
        opponent_color = 'black' if color == 'white' else 'white'
        x, y = square

        # Iterate over all opponent's pieces to check if any can move to the target square
        for pos, piece in self.pieces[opponent_color].items():
            if piece.is_valid_move(pos, (x, y), self.board):
                return True
        return False

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
                if piece.is_valid_move(start, end, self.board, self):
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
        for pos, piece in self.pieces[opponent_color].items():
            if piece.is_valid_move(pos, king_position, self.board):
                return True  # King is in check
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
            if not isinstance(piece, King) and piece.is_valid_move(pos, king_position, self.board):
                return pos, piece
        return None, None

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
