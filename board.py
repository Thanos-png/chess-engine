
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King
from utils import to_square_notation

class ChessBoard:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.pieces = {'white': {}, 'black': {}}  # Track all pieces by color and position
        self.setup_board()
        self.white_king_position = (4, 0)
        self.black_king_position = (4, 7)
        self.turn = 'white'
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_square = None  # Square where an en passant capture is possible
        self.halfmove_clock = 0  # Number of halfmoves since the last capture or pawn advance
        self.fullmove_number = 1  #How many turns have been played
        self.board_history = {}  # Dictionary to store FEN and their counts for threefold repetition draw

    # Getter for pieces
    def getPieces(self):
        return self.pieces

    # Setter for turn
    def setTurn(self, turn):
        if turn in ('white', 'black'):
            self.turn = turn
        else:
            raise ValueError("Turn must be 'white' or 'black'.")

    # Setter for castling rights
    def setCastlingRights(self, castling_rights):
        valid_keys = {'K', 'Q', 'k', 'q'}
        if all(key in valid_keys for key in castling_rights.keys()):
            self.castling_rights = castling_rights
        else:
            raise ValueError("Invalid castling rights keys.")

    # Setter for en passant square
    def setEnPassantSquare(self, square):
        if square is None or isinstance(square, str):
            self.en_passant_square = square
        else:
            raise ValueError("En passant square must be None or a valid square string.")

    # Setter for halfmove clock
    def setHalfMoveClock(self, count):
        if isinstance(count, int) and count >= 0:
            self.halfmove_clock = count
        else:
            raise ValueError("Halfmove clock must be a non-negative integer.")

    # Setter for fullmove number
    def setFullMoveNumber(self, number):
        if isinstance(number, int) and number > 0:
            self.fullmove_number = number
        else:
            raise ValueError("Fullmove number must be a positive integer.")

    def updateTurn(self):
        """Update the turn after a move is made."""
        self.turn = 'black' if self.turn == 'white' else 'white'
        return self.turn

    def updateCastlingRights(self, color, start, end):
        """Update castling rights if the king is moved or a rook is moved or captured."""
        prev_castling_rights = self.castling_rights.copy()
        if color == 'white':
            # Check if the white king or a white rook is moved
            if start == (4, 0):
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            elif start == (0, 0):
                self.castling_rights['Q'] = False
            elif start == (7, 0):
                self.castling_rights['K'] = False

            # Check if a black rook is captured
            if end == (0, 7):
                self.castling_rights['q'] = False
            elif end == (7, 7):
                self.castling_rights['k'] = False
        else:
            # Check if the black king or a black rook is moved
            if start == (4, 7):
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
            elif start == (0, 7):
                self.castling_rights['q'] = False
            elif start == (7, 7):
                self.castling_rights['k'] = False

            # Check if a white rook is captured
            if end == (0, 0):
                self.castling_rights['Q'] = False
            elif end == (7, 0):
                self.castling_rights['K'] = False

        # Clear board history if castling rights change
        if prev_castling_rights != self.castling_rights:
            self.board_history.clear()

    def updateEnPassantSquare(self, color, last_move):
        """Update en_passant_square based on the last move."""
        if last_move and isinstance(last_move[2], Pawn):
            # Check if the last move was a double pawn push
            if abs(last_move[0][1] - last_move[1][1]) == 2:
                # Check if the pawn that moved two squares forward has any neighboring (left and right) pawns
                for dx in [-1, 1]:
                    neighbor_x = last_move[1][0] + dx
                    if 0 <= neighbor_x < 8:
                        neighbor_piece = self.board[neighbor_x][last_move[1][1]]
                        if isinstance(neighbor_piece, Pawn) and neighbor_piece.color == color:
                            self.setEnPassantSquare(to_square_notation((last_move[1][0], (last_move[0][1] + last_move[1][1]) // 2)))
                            return
        self.setEnPassantSquare(None)

    def updateHalfMoveClock(self):
        """Increment the halfmove clock if a non-capturing or non-pawn move is made."""
        self.halfmove_clock += 1

    def updateFullMoveNumber(self):
        """Increment the fullmove number after blacks's move."""
        self.fullmove_number += 1

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

    def setup_board(self):
        """Sets up the chess board with pieces in their initial positions."""
        for i in range(8):
            self.board[i][1] = Pawn('white')
            self.pieces['white'][(i, 1)] = self.board[i][1]
            self.board[i][6] = Pawn('black')
            self.pieces['black'][(i, 6)] = self.board[i][6]

        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece in enumerate(placements):
            self.board[i][0] = piece('white')
            self.pieces['white'][(i, 0)] = self.board[i][0]
            self.board[i][7] = piece('black')
            self.pieces['black'][(i, 7)] = self.board[i][7]

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

    def checkThreefoldRepetition(self):
        """Check if the current board state has occurred three times."""
        current_state = self.to_fen().rsplit(' ', 2)[0]  # Update the current state of the board without halfmove_clock and fullmove_number
        self.board_history[current_state] = self.board_history.get(current_state, 0) + 1  # Update board history
        if self.board_history.get(current_state, 0) >= 3:
            print("Draw by threefold repetition.")
            return True
        return False

    def checkFiftyMoveRule(self):
        """Check if the game has reached a draw by the fifty-move rule."""
        if self.halfmove_clock >= 50:
            print("Draw by fifty-move rule.")
            return True
        return False

    def to_fen(self):
        """Convert the current board state to FEN notation."""
        fen = []

        # Iterate over each row from top (rank 8) to bottom (rank 1)
        for y in range(7, -1, -1):
            empty_count = 0
            row_fen = ''

            # Iterate over each column within the current row
            for x in range(8):
                piece = self.board[x][y]  # Access each "row" as a column in column-major order

                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_fen += str(empty_count)
                        empty_count = 0
                    row_fen += self.create_piece_for_fen(piece)

            # If there were empty squares at the end of the row, add the count
            if empty_count > 0:
                row_fen += str(empty_count)
            fen.append(row_fen)  # Append the row's FEN representation to the overall FEN
        fen = '/'.join(fen)  # Join the rows with '/' to separate them

        # Turn
        fen += ' w ' if self.turn == 'white' else ' b '

        # Castling rights
        castling = ''.join([k for k, v in self.castling_rights.items() if v])
        fen += (castling if castling else '-')

        # En passant target square
        fen += ' ' + (self.en_passant_square if self.en_passant_square else '-') + ' '

        # Halfmove clock
        fen += f'{self.halfmove_clock} '

        # Fullmove number
        fen += f'{self.fullmove_number}'

        return fen

    def from_fen(self, fen):
        """Initialize the board from a FEN notation string."""
        parts = fen.split()

        # Piece positions
        rows = parts[0].split('/')
        self.board = [[None] * 8 for _ in range(8)]  # Reset the board
        self.pieces = {'white': {}, 'black': {}}  # Reset the pieces dictionary

        for y, row in enumerate(rows):
            x = 0
            for char in row:
                if char.isdigit():
                    x += int(char)
                else:
                    piece = self.create_piece_from_fen(char)
                    self.board[x][7 - y] = piece
                    if piece:
                        self.pieces[piece.color][(x, 7 - y)] = piece  # Add the piece to the pieces dictionary
                        if isinstance(piece, King):
                            if piece.color == 'white':
                                self.white_king_position = (x, 7 - y)
                            else:
                                self.black_king_position = (x, 7 - y)
                    x += 1

        # Turn
        self.turn = 'white' if parts[1] == 'w' else 'black'

        # Castling rights
        castling_rights = parts[2]
        self.castling_rights = {
            'K': 'K' in castling_rights,
            'Q': 'Q' in castling_rights,
            'k': 'k' in castling_rights,
            'q': 'q' in castling_rights
        }

        # En passant target square
        self.en_passant_square = parts[3] if parts[3] != '-' else None

        # Halfmove clock
        self.halfmove_clock = int(parts[4])

        # Fullmove number
        self.fullmove_number = int(parts[5])

    def create_piece_for_fen(self, piece):
        """Create the piece character representation for a FEN."""
        char = None
        if isinstance(piece, Pawn):
            char = 'p'
        elif isinstance(piece, Rook):
            char = 'r'
        elif isinstance(piece, Knight):
            char = 'n'
        elif isinstance(piece, Bishop):
            char = 'b'
        elif isinstance(piece, Queen):
            char = 'q'
        elif isinstance(piece, King):
            char = 'k'
        
        if piece and piece.color == 'white':
            char = char.upper()
        return char

    def create_piece_from_fen(self, char):
        """Create a piece from a FEN character."""
        color = 'white' if char.isupper() else 'black'
        char = char.lower()

        if char == 'p':
            return Pawn(color)
        elif char == 'r':
            return Rook(color)
        elif char == 'n':
            return Knight(color)
        elif char == 'b':
            return Bishop(color)
        elif char == 'q':
            return Queen(color)
        elif char == 'k':
            return King(color)
        return None

    def is_square_under_attack(self, square, color):
        """Check if a square is under attack by any piece of the opponent's color."""
        opponent_color = 'black' if color == 'white' else 'white'
        x, y = square

        # Iterate over all opponent's pieces to check if any can move to the target square
        for pos, piece in self.pieces[opponent_color].items():
            if piece.is_valid_move(pos, (x, y), self.board):
                return True
        return False

    def move_piece(self, start, end, color):
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

                        # Update fullmove number
                        if color == 'black':
                            self.updateFullMoveNumber()
                        self.updateHalfMoveClock()  # Increment halfmove clock
                        self.updateCastlingRights(color, start, end)  # Update castling rights because the king moved
                        return True
                return False
            # Check for en passant capture
            en_passant_target_pawn = self.board[end_x][start_y]  # Pawn that can be captured en passant if any
            if self.en_passant_square and isinstance(piece, Pawn) and piece.is_valid_move(start, end, self.board, self):
                if self.move_piece_helper(start, end, self.board, color):
                    # Remove the captured pawn from the pieces dictionary
                    opponent_color = 'black' if color == 'white' else 'white'
                    del board_instance.getPieces()[opponent_color][(end_x, start_y)]

                    # Update fullmove number
                    if color == 'black':
                        self.updateFullMoveNumber()

                    # Reset halfmove clock because a pawn was moved
                    self.halfmove_clock = 0

                    # Clear board history after an en passant capture
                    self.board_history.clear()
                    return True
                # Restore the enemy pawn that was captured en passant
                self.board[end_x][start_y] = en_passant_target_pawn
                return False
            if piece.is_valid_move(start, end, self.board):
                if self.move_piece_helper(start, end, self.board, color):
                    self.updateHalfMoveClock()  # Increment halfmove clock

                    # Check for pawn promotion
                    if isinstance(piece, Pawn):
                        # Clear board history after a pawn move
                        self.board_history.clear()

                        # Reset halfmove clock because a pawn was moved
                        self.halfmove_clock = 0
                        if (color == 'white' and end_y == 7) or (color == 'black' and end_y == 0):
                            piece.promote_pawn((end_x, end_y), color, self)

                    # Update fullmove number
                    if color == 'black':
                        self.updateFullMoveNumber()

                    # Update castling rights because a rook moved or was captured
                    if isinstance(piece, Rook) or end == (0, 0) or end == (7, 0) or end == (0, 7) or end == (7, 7):
                        self.updateCastlingRights(color, start, end)
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
        if isinstance(piece, King):
            king_position = (end_x, end_y)
        else:
            king_position = self.white_king_position if color == 'white' else self.black_king_position
        self.board[start_x][start_y] = None
        
        # Get the king instance for the current player
        king = self.board[king_position[0]][king_position[1]]

        # Ensure the king is correctly retrieved
        if not isinstance(king, King):
            raise ValueError(f"Expected a King at position {king_position} but found {type(king).__name__}")

        # Check if this move leaves the king in check
        if king.is_in_check(color, self):
            # Revert move if it results in check
            self.board[start_x][start_y] = piece
            self.board[end_x][end_y] = target_piece
            return False

        # Reset halfmove clock because a piece is captured
        if target_piece and target_piece.color != color:
            self.halfmove_clock = 0
        self.update_piece_position(start, end)
        return True

    def has_legal_moves(self, color):
        """Determine if the player has any legal moves remaining.
        If the king is in check, check if there is a way to escape check (either by moving the king,
        blocking the check, or capturing the checking piece). If no escape is possible, declare checkmate.
        If the player has no legal moves but isn't in check, declare stalemate."""
        # Get the king instance for the current player
        king_position = self.white_king_position if color == 'white' else self.black_king_position
        king = self.board[king_position[0]][king_position[1]]
        opponent_color = 'black' if color == 'white' else 'white'

        # Ensure the king is correctly retrieved
        if not isinstance(king, King):
            raise ValueError(f"Expected a King at position {king_position} but found {type(king).__name__}")

        # Check if the king is currently in check 
        in_check = king.is_in_check(color, self)
        protected_piece = False  # Flag to check if the piece that is checking the king is protected

        # Check if the king can escape check by moving to a different square
        if in_check:
            # Identify the piece that is checking the king
            checking_position, checking_piece = king.get_checking_piece(king_position, opponent_color, self)

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

                        # Check if this move takes the king out of check
                        if not king.is_in_check(color, self):
                            # Undo the move and return True (legal escape found)
                            self.board[king_x][king_y] = self.board[new_x][new_y]
                            self.board[new_x][new_y] = piece

                            king_position = king_x, king_y
                            if (color == "white"):
                                self.white_king_position = king_position
                            else:
                                self.black_king_position = king_position

                            print(f"{color.capitalize()} is in check.")
                            return True

                        # Undo the move
                        self.board[king_x][king_y] = self.board[new_x][new_y]
                        self.board[new_x][new_y] = piece
                        king_position = king_x, king_y
                        if (color == "white"):
                            self.white_king_position = king_position
                        else:
                            self.black_king_position = king_position

            # Check if we can capture the checking piece
            for pos, piece in self.pieces[color].items():
                if piece.is_valid_move(pos, checking_position, self.board):
                    # Temporarily make the capture
                    captured_piece = self.board[checking_position[0]][checking_position[1]]
                    self.board[checking_position[0]][checking_position[1]] = piece
                    self.board[pos[0]][pos[1]] = None
                    del self.pieces[opponent_color][checking_position]

                    if not king.is_in_check(color, self):
                        # Undo move and return True (legal move found)
                        self.board[pos[0]][pos[1]] = piece
                        self.board[checking_position[0]][checking_position[1]] = captured_piece
                        self.pieces[opponent_color][checking_position] = captured_piece

                        print(f"{color.capitalize()} is in check.")
                        return True

                    # Undo the move
                    self.board[pos[0]][pos[1]] = piece
                    self.board[checking_position[0]][checking_position[1]] = captured_piece
                    self.pieces[opponent_color][checking_position] = captured_piece

            # Check if we can block the check by moving a piece between the king and the checking piece
            if isinstance(checking_piece, (Rook, Bishop, Queen)):
                blocking_squares = king.get_blocking_squares(king_position, checking_position)
                for pos, piece in self.pieces[color].items():
                    for square in blocking_squares:
                        if not isinstance(piece, King) and piece.is_valid_move(pos, square, self.board):
                            # Temporarily make the block
                            original_piece = self.board[square[0]][square[1]]
                            self.board[square[0]][square[1]] = piece
                            self.board[pos[0]][pos[1]] = None

                            if not king.is_in_check(color, self):
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
                        if target_piece:
                            del self.pieces[opponent_color][(dx, dy)]

                        # Check if this move leaves the king in check
                        if not king.is_in_check(color, self):
                            # Undo the move and return True (legal move found)
                            self.board[pos[0]][pos[1]] = piece
                            self.board[dx][dy] = target_piece
                            if target_piece:
                                self.pieces[opponent_color][(dx, dy)] = target_piece

                            return True

                        # Undo the move
                        self.board[pos[0]][pos[1]] = piece
                        self.board[dx][dy] = target_piece
                        if target_piece:
                            self.pieces[opponent_color][(dx, dy)] = target_piece

        # No legal moves were found and the king is not in check, so it's stalemate
        print("Stalemate! The game is a draw.")
        return False
