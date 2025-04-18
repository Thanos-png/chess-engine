
from typing import Optional, Dict, Tuple
from pieces.piece import ChessPiece
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King
from utils import parse_position, to_square_notation
from polyglot import Polyglot
from copy import deepcopy


class ChessBoard:
    def __init__(self) -> None:
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
        self.repetition_count = {}  # Hash map to track board state frequencies
        self.polyglotObj = Polyglot()  # Polyglot object to call zobristHash() to check for threefold repetition draw
        self.fen_stack = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]  # Stack to store FEN strings for undoing moves
        self.stalemate = False  # Flag that checks if the current position is a stalemate

    def clone(self) -> 'ChessBoard':
        """Create a deep copy of the chess board."""
        new_board = ChessBoard()
        new_board.board = [row[:] for row in self.board]
        new_board.pieces = {color: pieces.copy() for color, pieces in self.pieces.items()}
        new_board.white_king_position = self.white_king_position
        new_board.black_king_position = self.black_king_position
        new_board.turn = self.turn
        new_board.castling_rights = self.castling_rights.copy()
        new_board.en_passant_square = self.en_passant_square
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.repetition_count = self.repetition_count.copy()
        new_board.fen_stack = self.fen_stack[:]
        new_board.stalemate = self.stalemate
        return new_board

    # Getter for pieces
    def getPieces(self) -> Dict[str, Dict[Tuple[int, int], ChessPiece]]:
        return self.pieces

    # Setter for castling rights
    def setCastlingRights(self, castling_rights: Dict[str, bool]) -> None:
        valid_keys = {'K', 'Q', 'k', 'q'}
        if all(key in valid_keys for key in castling_rights.keys()):
            key: str
            self.castling_rights = castling_rights
        else:
            raise ValueError("Invalid castling rights keys.")

    # Setter for en passant square
    def setEnPassantSquare(self, square: str) -> None:
        if square is None or isinstance(square, str):
            self.en_passant_square = square
        else:
            raise ValueError("En passant square must be None or a valid square string.")

    # Setter for halfmove clock
    def setHalfMoveClock(self, count: int) -> None:
        if (isinstance(count, int) and count >= 0):
            self.halfmove_clock = count
        else:
            raise ValueError("Halfmove clock must be a non-negative integer.")

    # Setter for fullmove number
    def setFullMoveNumber(self, number: int) -> None:
        if (isinstance(number, int) and number > 0):
            self.fullmove_number = number
        else:
            raise ValueError("Fullmove number must be a positive integer.")

    def updateTurn(self) -> str:
        """Update the turn after a move is made."""
        self.turn = 'black' if self.turn == 'white' else 'white'
        return self.turn

    def updateCastlingRights(self, color: str, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Update castling rights if the king is moved or a rook is moved or captured."""
        prev_castling_rights: Dict[str, bool] = self.castling_rights.copy()
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

        # Clear repetition count history if castling rights change
        if (prev_castling_rights != self.castling_rights):
            self.repetition_count.clear()

    def updateEnPassantSquare(self, color: str, last_move: Tuple[Tuple[int, int], Tuple[int, int], ChessPiece]) -> None:
        """Update en_passant_square based on the last move."""
        if last_move and isinstance(last_move[2], Pawn):
            # Check if the last move was a double pawn push
            if (abs(last_move[0][1] - last_move[1][1]) == 2):
                # Check if the pawn that moved two squares forward has any neighboring (left and right) pawns
                for dx in [-1, 1]:
                    neighbor_x: int = last_move[1][0] + dx
                    if (0 <= neighbor_x < 8):
                        neighbor_piece: ChessPiece = self.board[neighbor_x][last_move[1][1]]
                        if (isinstance(neighbor_piece, Pawn) and neighbor_piece.color == color):
                            self.setEnPassantSquare(to_square_notation((last_move[1][0], (last_move[0][1] + last_move[1][1]) // 2)))
                            return
        self.setEnPassantSquare(None)

    def updateHalfMoveClock(self) -> None:
        """Increment the halfmove clock if a non-capturing or non-pawn move is made."""
        self.halfmove_clock += 1

    def updateFullMoveNumber(self) -> None:
        """Increment the fullmove number after blacks's move."""
        self.fullmove_number += 1

    def update_piece_position(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Update the pieces dictionary after a move."""
        piece: ChessPiece = self.board[end[0]][end[1]]
        color: str = piece.color
        if start in self.pieces[color]:
            del self.pieces[color][start]
        self.pieces[color][end] = piece

        # Remove captured piece from the opponent's dictionary, if any
        opponent_color = 'black' if color == 'white' else 'white'
        if end in self.pieces[opponent_color]:
            del self.pieces[opponent_color][end]

    def updateFENstack(self) -> None:
        """Save the current state to the FEN stack."""
        current_fen: str = self.to_fen()
        self.fen_stack.append(current_fen)

    def changePiecesFormat(self, pieces: Dict[str, Dict[Tuple[int, int], ChessPiece]]) -> Dict[Tuple[int, int], Tuple[str, str]]:
        """Change the self.pieces format to map positions to (piece_type, color) and 
        create a new pawns dictionairy that maps squares to color."""
        result = {}
        pawns = {}

        for color, piece_positions in pieces.items():
            color: str
            piece_positions: Dict[Tuple[int, int], ChessPiece]

            for position, piece in piece_positions.items():
                position: Tuple[int, int]
                piece: ChessPiece

                if isinstance(piece, Pawn):
                    pawns[position] = color

                piece_type: str = type(piece).__name__.lower()
                result[position] = (piece_type, color)

        return result, pawns

    def changeCastlingRightsFormat(self, castling_rights: Dict[str, bool]) -> str:
        """Change the self.castling_rights format to a string representation."""
        result = ''.join(flag for flag, available in castling_rights.items() if available)
        return result if result else '-'  # If there are no castling rights then return '-'

    def changeEnPassantSquareFormat(self, en_passant_square: str) -> Tuple[int, int]:
        """Change the self.en_passant_square format to a string representation."""
        return parse_position(en_passant_square) if en_passant_square else None

    def setup_board(self) -> None:
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

    def display(self) -> None:
        """Prints the chess board after every move."""
        print("\n  a b c d e f g h")
        for y in range(7, -1, -1):
            print(f"{y+1} ", end="")
            for x in range(8):
                piece: ChessPiece = self.board[x][y]
                print(str(piece) if piece else '.', end=" ")
            print(f"{y+1}")
        print("  a b c d e f g h\n")

    def checkThreefoldRepetition(self, engineFlag=False) -> bool:
        """Check if the current board state has occurred three times."""
        # Change the format and unpack the variables
        pieces, pawns = self.changePiecesFormat(self.pieces)
        pieces: Dict[Tuple[int, int], Tuple[str, str]]
        pawns: Dict[Tuple[int, int], str]
        castling_rights: str = self.changeCastlingRightsFormat(self.castling_rights)
        ep_square: Tuple[int, int] = self.changeEnPassantSquareFormat(self.en_passant_square)
        current_state: int = self.polyglotObj.zobristHash(self.board, pieces, castling_rights, ep_square, self.turn, pawns)  # Unique int value representing the board state

        # Update the Hash map
        if current_state in self.repetition_count:
            self.repetition_count[current_state] += 1
        else:
            self.repetition_count[current_state] = 1

        # Check if this is the third time this position occurres
        if self.repetition_count.get(current_state, 0) >= 3:
            if not engineFlag:
                print("Draw by threefold repetition.")
            return True
        return False

    def checkFiftyMoveRule(self, engineFlag=False) -> bool:
        """Check if the game has reached a draw by the fifty-move rule."""
        if (self.halfmove_clock >= 50):
            if not engineFlag:
                print("Draw by fifty-move rule.")
            return True
        return False

    def checkInsufficientMaterial(self) -> None:
        """Check if the game is a draw due to insufficient material."""
        bishopsWhite = []
        bishopsBlack = []
        bishopsCountWhite = 0
        bishopsCountBlack = 0
        knightsWhite = []
        knightsBlack = []
        knightsCountWhite = 0
        knightsCountBlack = 0

        # Iterate over the dictionary to count pieces
        for position, piece in self.pieces[self.turn].items():
            position: Tuple[int, int]
            piece: ChessPiece

            if isinstance(piece, Bishop):
                if (piece.color == 'white'):
                    bishopsWhite.append(position)  # Track White bishops for same color square check
                    bishopsCountWhite += 1
                else:
                    bishopsBlack.append(position)  # Track Black bishops for same color square check
                    bishopsCountBlack += 1
            elif isinstance(piece, Knight):
                if (piece.color == 'white'):
                    knightsCountWhite += 1
                else:
                    knightsCountBlack += 1
            elif not isinstance(piece, King):
                # Any pawns, rooks, or queens means no insufficient material
                return False

        opponent_color = 'black' if self.turn == 'white' else 'white'
        for position, piece in self.pieces[opponent_color].items():
            position: Tuple[int, int]
            piece: ChessPiece

            if isinstance(piece, Bishop):
                if (piece.color == 'white'):
                    bishopsWhite.append(position)  # Track White bishops for same color square check
                    bishopsCountWhite += 1
                else:
                    bishopsBlack.append(position)  # Track Black bishops for same color square check
                    bishopsCountBlack += 1
            elif isinstance(piece, Knight):
                if (piece.color == 'white'):
                    knightsCountWhite += 1
                else:
                    knightsCountBlack += 1
            elif not isinstance(piece, King):
                # Any pawns, rooks, or queens means no insufficient material
                return False

        # Basic insufficient material checks
        canWhiteWin: bool = not ((bishopsCountWhite <= 1 and knightsCountWhite == 0) or (knightsCountWhite <= 2 and not bishopsWhite) or not (bishopsWhite == 2 and knightsCountWhite == 0))
        canBlackWin: bool = not ((bishopsCountBlack <= 1 and knightsCountBlack == 0) or (knightsCountBlack <= 2 and not bishopsBlack) or not (bishopsBlack == 2 and knightsCountBlack == 0))
        if (not canWhiteWin) and (not canBlackWin):
            return True

        if (bishopsWhite == 2 and knightsCountWhite == 0) and (bishopsBlack == 2 and knightsCountBlack == 0):
            # Check if all bishops are on the same color squares
            white_bishops_same_color: bool = all((pos[0] + pos[1]) % 2 == (bishopsWhite[0][0] + bishopsWhite[0][1]) % 2 for pos in bishopsWhite)
            black_bishops_same_color: bool = all((pos[0] + pos[1]) % 2 == (bishopsBlack[0][0] + bishopsBlack[0][1]) % 2 for pos in bishopsBlack)
            pos: Tuple[int, int]
            if (white_bishops_same_color or black_bishops_same_color):
                return True
        return False

    def to_fen(self) -> str:
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
                    if (empty_count > 0):
                        row_fen += str(empty_count)
                        empty_count = 0
                    row_fen += self.create_piece_for_fen(piece)

            # If there were empty squares at the end of the row, add the count
            if (empty_count > 0):
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

    def from_fen(self, fen: str) -> None:
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
                    piece: ChessPiece = self.create_piece_from_fen(char)
                    self.board[x][7 - y] = piece
                    if piece:
                        self.pieces[piece.color][(x, 7 - y)] = piece  # Add the piece to the pieces dictionary
                        if isinstance(piece, King):
                            if (piece.color == 'white'):
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

    def create_piece_for_fen(self, piece: ChessPiece) -> str:
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
        
        if (piece and piece.color == 'white'):
            char = char.upper()
        return char

    def create_piece_from_fen(self, char: str) -> ChessPiece:
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

    def is_square_under_attack(self, square: Tuple[int, int], color: str) -> bool:
        """Check if a square is under attack by any piece of the opponent's color."""
        opponent_color = 'black' if color == 'white' else 'white'
        x, y = square

        # Iterate over all opponent's pieces to check if any can move to the target square
        for pos, piece in self.pieces[opponent_color].items():
            pos: Tuple[int, int]
            piece: ChessPiece

            if piece.is_valid_move(pos, (x, y), self.board):
                return True
        return False

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int], color: str, flag=False, engineFlag=False) -> bool:
        """Moves a piece from the start position to the end position if it is a valid move.
        flag: is used to check if the move is valid before playing it (for the generate_legal_moves()).
        engineFlag: is used to check if the move is made by the engine (in case pawn promotion needed)."""
        if (start == end):
            return False

        start_x, start_y = start
        end_x, end_y = end

        if (start_x < 0 or start_x > 7 or start_y < 0 or start_y > 7 or end_x < 0 or end_x > 7 or end_y < 0 or end_y > 7):
            return False

        piece: ChessPiece = self.board[start_x][start_y]  # Piece at the start square
        target_piece: ChessPiece = self.board[end_x][end_y]  # Piece at the target square(if any)

        # Check if the destination square contains a piece of the same color
        if (target_piece and target_piece.color == color):
            return False

        # Check if the piece at the start square is of the correct color
        if (piece and piece.color == color):
            if isinstance(piece, King):
                if piece.is_valid_move(start, end, self.board, self):
                    if self.move_piece_helper(start, end, self.board, color, flag, engineFlag):
                        if not flag:
                            # Update fullmove number
                            if (color == 'black'):
                                self.updateFullMoveNumber()
                            self.updateHalfMoveClock()  # Increment halfmove clock
                            self.updateCastlingRights(color, start, end)  # Update castling rights because the king moved
                        return True
                return False
            # Check for en passant capture
            en_passant_target_pawn: ChessPiece = self.board[end_x][start_y]  # Pawn that can be captured en passant (if any)
            if (self.en_passant_square and isinstance(piece, Pawn) and self.en_passant_square == to_square_notation(end) and piece.is_valid_move(start, end, self.board, self)):
                if self.move_piece_helper(start, end, self.board, color, flag, engineFlag):
                    if flag:
                        # Restore the enemy pawn that was captured en passant
                        self.board[end_x][start_y] = en_passant_target_pawn
                    else:
                        # Remove the captured pawn from the pieces dictionary
                        opponent_color = 'black' if color == 'white' else 'white'
                        del self.getPieces()[opponent_color][(end_x, start_y)]

                        # Update fullmove number
                        if (color == 'black'):
                            self.updateFullMoveNumber()

                        # Reset halfmove clock because a pawn was moved
                        self.halfmove_clock = 0

                        # Clear repetition count history after an en passant capture
                        self.repetition_count.clear()
                    return True
                # Restore the enemy pawn that was captured en passant
                self.board[end_x][start_y] = en_passant_target_pawn
                return False
            if piece.is_valid_move(start, end, self.board):
                if self.move_piece_helper(start, end, self.board, color, flag, engineFlag):
                    if not flag:
                        self.updateHalfMoveClock()  # Increment halfmove clock

                        # Check for pawn promotion
                        if isinstance(piece, Pawn):
                            # Clear repetition count history after a pawn move
                            self.repetition_count.clear()

                            # Reset halfmove clock because a pawn was moved
                            self.halfmove_clock = 0
                            if (color == 'white' and end_y == 7) or (color == 'black' and end_y == 0):
                                if engineFlag:
                                    self.board[end_x][end_y] = Queen(color)
                                    self.pieces[color][end] = self.board[end_x][end_y]
                                else:
                                    piece.promote_pawn((end_x, end_y), color, self)

                        # Update fullmove number
                        if (color == 'black'):
                            self.updateFullMoveNumber()

                        # Update castling rights because a rook moved or was captured
                        if (isinstance(piece, Rook) or end == (0, 0) or end == (7, 0) or end == (0, 7) or end == (7, 7)):
                            self.updateCastlingRights(color, start, end)
                    return True
        return False

    def move_piece_helper(self, start: Tuple[int, int], end: Tuple[int, int], board: list[list[Optional[ChessPiece]]], color: str, flag: bool, engineFlag: bool) -> bool:
        """Check if a move is legal before playing it and update the board accordingly."""
        opponent_color = 'black' if color == 'white' else 'white'
        start_x, start_y = start
        end_x, end_y = end
        piece: ChessPiece = self.board[start_x][start_y]  # Piece at the start square
        target_piece: ChessPiece = self.board[end_x][end_y]  # Piece at the target square(if any)

        # Save the state of the board for check validation
        if isinstance(piece, King):
            king_position: Tuple[int, int] = (end_x, end_y)
            king_positionPrev: Tuple[int, int] = self.white_king_position if color == 'white' else self.black_king_position
            if color == 'white':
                self.white_king_position = king_position
            else:
                self.black_king_position = king_position
        else:
            king_position: Tuple[int, int] = self.white_king_position if color == 'white' else self.black_king_position

        # Change the board and pieces(temporarily)
        self.board[end_x][end_y] = piece
        self.board[start_x][start_y] = None
        del self.pieces[color][start]
        self.pieces[color][end] = piece
        
        # Get the king instance for the current player
        king: King = self.board[king_position[0]][king_position[1]]

        # Ensure the king is correctly retrieved
        if not isinstance(king, King):
            raise ValueError(f"Expected a King at position {king_position} but found {type(king).__name__}")

        # Check if this move leaves the king in check
        if (target_piece and target_piece.color != color):
            del self.pieces[opponent_color][end]
        if king.is_in_check(color, self):
            # Revert move if it results in check
            self.board[start_x][start_y] = piece
            self.board[end_x][end_y] = target_piece
            self.pieces[color][start] = piece
            del self.pieces[color][end]
            if (target_piece and target_piece.color != color):
                self.pieces[opponent_color][end] = target_piece
            if isinstance(piece, King):
                if color == 'white':
                    self.white_king_position = king_positionPrev
                else:
                    self.black_king_position = king_positionPrev
            return False

        if flag:
            self.board[start_x][start_y] = piece
            self.board[end_x][end_y] = target_piece
            self.pieces[color][start] = piece
            del self.pieces[color][end]
            if (target_piece and target_piece.color != color):
                self.pieces[opponent_color][end] = target_piece
            if isinstance(piece, King):
                if color == 'white':
                    self.white_king_position = king_positionPrev
                else:
                    self.black_king_position = king_positionPrev
        else:
            # Update the has_move atributes for the player's color in case the player played a move
            # Engine's has_move atributes are been updated inside the game loop in the main() function
            if (isinstance(piece, King)):
                if not engineFlag:
                    piece.has_moved = True
                # Castling move
                if abs(start[0] - end[0]) == 2:
                    row = start[1]
                    if end[0] == 6:  # Kingside
                        self.board[5][row] = self.board[7][row]
                        self.board[7][row] = None
                        if (color == 'white'):
                            rook: Rook = self.pieces[color][(7, 0)]
                            del self.pieces[color][(7, 0)]
                            self.pieces[color][(5, 0)] = rook
                        else:
                            rook: Rook = self.pieces[color][(7, 7)]
                            del self.pieces[color][(7, 7)]
                            self.pieces[color][(5, 7)] = rook
                    elif end[0] == 2:  # Queenside
                        self.board[3][row] = self.board[0][row]
                        self.board[0][row] = None
                        if (color == 'white'):
                            rook: Rook = self.pieces[color][(0, 0)]
                            del self.pieces[color][(0, 0)]
                            self.pieces[color][(3, 0)] = rook
                        else:
                            rook: Rook = self.pieces[color][(0, 7)]
                            del self.pieces[color][(0, 7)]
                            self.pieces[color][(3, 7)] = rook
                    if not engineFlag:
                        rook.has_moved = True
            if (isinstance(piece, Rook) and not engineFlag):
                piece.has_moved = True

            # Reset halfmove clock because a piece is captured
            if (target_piece and target_piece.color != color):
                self.halfmove_clock = 0
            self.update_piece_position(start, end)
        return True

    def has_legal_moves(self, color: str, engineFlag=False) -> bool:
        """Determine if the player has any legal moves remaining.
        If the king is in check, check if there is a way to escape check (either by moving the king,
        blocking the check, or capturing the checking piece). If no escape is possible, declare checkmate.
        If the player has no legal moves but isn't in check, declare stalemate."""
        # Get the king instance for the current player
        king_position: Tuple[int, int] = self.white_king_position if color == 'white' else self.black_king_position
        king: King = self.board[king_position[0]][king_position[1]]
        opponent_color = 'black' if color == 'white' else 'white'

        # Ensure the king is correctly retrieved
        if not isinstance(king, King):
            self.display()
            raise ValueError(f"Expected a King at position {king_position} but found {type(king).__name__}")

        # Check if the king is currently in check 
        in_check: bool = king.is_in_check(color, self)
        protected_piece = False  # Flag to check if the piece that is checking the king is protected

        # Check if the king can escape check by moving to a different square
        if in_check:
            # Identify the piece that is checking the king
            checking_position, checking_piece = king.get_checking_piece(king_position, opponent_color, self)
            checking_position: Tuple[int, int]
            checking_piece: ChessPiece

            # Generate all possible moves for the king (1 square in each direction)
            king_x, king_y = king_position
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                new_x, new_y = king_x + dx, king_y + dy
                # Check if the square that the king is trying to move to is inside the board
                if (0 <= new_x <= 7 and 0 <= new_y <= 7):
                    # Checks if the square that the king is trying to move to is blocked
                    if self.board[new_x][new_y] is None or self.board[new_x][new_y].color == opponent_color:
                        # Move the king to that square temporarily
                        piece: ChessPiece = self.board[new_x][new_y]
                        self.board[new_x][new_y] = self.board[king_x][king_y]
                        self.board[king_x][king_y] = None

                        # Temporarily update the king position
                        king_position: Tuple[int, int] = new_x, new_y
                        if (color == 'white'):
                            self.white_king_position = king_position
                        else:
                            self.black_king_position = king_position

                        # Check if this move takes the king out of check
                        if not king.is_in_check(color, self):
                            # Undo the move and return True (legal escape found)
                            self.board[king_x][king_y] = self.board[new_x][new_y]
                            self.board[new_x][new_y] = piece

                            # Change the king position back to the original value
                            king_position = king_x, king_y
                            if (color == 'white'):
                                self.white_king_position = king_position
                            else:
                                self.black_king_position = king_position

                            if not engineFlag:
                                print(f"{color.capitalize()} is in check.")
                            return True

                        # Undo the move
                        self.board[king_x][king_y] = self.board[new_x][new_y]
                        self.board[new_x][new_y] = piece

                        # Change the king position back to the original value
                        king_position = king_x, king_y
                        if (color == 'white'):
                            self.white_king_position = king_position
                        else:
                            self.black_king_position = king_position

            # Check if we can capture the checking piece
            for pos, piece in self.pieces[color].items():
                pos: Tuple[int, int]
                piece: ChessPiece

                if piece.is_valid_move(pos, checking_position, self.board):
                    # Temporarily update the king position
                    if isinstance(piece, King):
                        king_positionPrev: Tuple[int, int] = self.white_king_position if color == 'white' else self.black_king_position
                        if (color == 'white'):
                            self.white_king_position = checking_position
                        else:
                            self.black_king_position = checking_position

                    # Temporarily make the capture
                    captured_piece: ChessPiece = self.board[checking_position[0]][checking_position[1]]
                    self.board[checking_position[0]][checking_position[1]] = piece
                    self.board[pos[0]][pos[1]] = None
                    del self.pieces[opponent_color][checking_position]

                    if not king.is_in_check(color, self):
                        # Undo move and return True (legal move found)
                        self.board[pos[0]][pos[1]] = piece
                        self.board[checking_position[0]][checking_position[1]] = captured_piece
                        self.pieces[opponent_color][checking_position] = captured_piece

                        # Change the king position back to the original value
                        if isinstance(piece, King):
                            if (color == 'white'):
                                self.white_king_position = king_positionPrev
                            else:
                                self.black_king_position = king_positionPrev

                        if not engineFlag:
                            print(f"{color.capitalize()} is in check.")
                        return True

                    # Undo the move
                    self.board[pos[0]][pos[1]] = piece
                    self.board[checking_position[0]][checking_position[1]] = captured_piece
                    self.pieces[opponent_color][checking_position] = captured_piece

                    # Change the king position back to the original value
                    if isinstance(piece, King):
                        if (color == 'white'):
                            self.white_king_position = king_positionPrev
                        else:
                            self.black_king_position = king_positionPrev

            # Check if we can block the check by moving a piece between the king and the checking piece
            if isinstance(checking_piece, (Rook, Bishop, Queen)):
                blocking_squares: list[Tuple[int, int]] = king.get_blocking_squares(king_position, checking_position)
                for pos, piece in self.pieces[color].items():
                    pos: Tuple[int, int]
                    piece: ChessPiece

                    for square in blocking_squares:
                        square: Tuple[int, int]

                        if not isinstance(piece, King) and piece.is_valid_move(pos, square, self.board):
                            # Temporarily make the block
                            original_piece: ChessPiece = self.board[square[0]][square[1]]
                            self.board[square[0]][square[1]] = piece
                            self.board[pos[0]][pos[1]] = None

                            if not king.is_in_check(color, self):
                                # Undo move and return True (legal move found)
                                self.board[pos[0]][pos[1]] = piece
                                self.board[square[0]][square[1]] = original_piece

                                if not engineFlag:
                                    print(f"{color.capitalize()} is in check.")
                                return True

                            # Undo the move
                            self.board[pos[0]][pos[1]] = piece
                            self.board[square[0]][square[1]] = original_piece

            # No legal moves were found and the king is in check, so it's checkmate
            if not engineFlag:
                print(f"Checkmate! {('Black' if color == 'white' else 'White')} wins!")
            return False

        # If not in check, check for any legal moves (stalemate)
        for pos, piece in self.pieces[color].items():
            pos: Tuple[int, int]
            piece: ChessPiece

            for dx in range(8):
                for dy in range(8):
                    if piece.is_valid_move(pos, (dx, dy), self.board):
                        # Temporarily update the king position
                        if isinstance(piece, King):
                            king_positionPrev: Tuple[int, int] = self.white_king_position if color == 'white' else self.black_king_position
                            if (color == 'white'):
                                self.white_king_position = (dx, dy)
                            else:
                                self.black_king_position = (dx, dy)

                        # Temporarily make the move
                        target_piece: ChessPiece = self.board[dx][dy]
                        self.board[dx][dy] = piece
                        self.board[pos[0]][pos[1]] = None
                        if (target_piece and target_piece.color == opponent_color and not isinstance(target_piece, King)):
                            del self.pieces[opponent_color][(dx, dy)]

                        # Check if this move leaves the king in check
                        if not king.is_in_check(color, self):
                            # Undo the move and return True (legal move found)
                            self.board[pos[0]][pos[1]] = piece
                            self.board[dx][dy] = target_piece
                            if target_piece and target_piece.color == opponent_color and not isinstance(target_piece, King):
                                self.pieces[opponent_color][(dx, dy)] = target_piece
                            
                            # Change the king position back to the original value
                            if isinstance(piece, King):
                                if (color == 'white'):
                                    self.white_king_position = king_positionPrev
                                else:
                                    self.black_king_position = king_positionPrev
                            return True

                        # Undo the move
                        self.board[pos[0]][pos[1]] = piece
                        self.board[dx][dy] = target_piece
                        if (target_piece and target_piece.color == opponent_color and not isinstance(target_piece, King)):
                            self.pieces[opponent_color][(dx, dy)] = target_piece

                        # Change the king position back to the original value
                        if isinstance(piece, King):
                            if (color == 'white'):
                                self.white_king_position = king_positionPrev
                            else:
                                self.black_king_position = king_positionPrev

        # No legal moves were found and the king is not in check, so it's stalemate
        if not engineFlag:
            print("Stalemate! The game is a draw.")
        if engineFlag:
            self.stalemate = True
        return False

    def generate_legal_moves(self, color: str, flag=False) -> list[Dict[str, Tuple[int, int]]]:
        """Generate all legal moves for the given color and returns them 
        as a list in the format {'start': (x1, y1), 'end': (x2, y2)}."""
        legal_moves = []

        # Determine the active pieces for the color and create a deep copy of them to avoid modifications during the loop
        active_pieces: Dict[Tuple[int, int], ChessPiece] = deepcopy(self.pieces['white'] if color == 'white' else self.pieces['black'])

        # Iterate over each piece type and their positions
        for pos, piece in active_pieces.items():
            pos: Tuple[int, int]
            piece: ChessPiece

            if not piece:
                continue

            # Check all the possible moves for the each piece type
            for move in piece.legal_moves(pos, color):
                move: Tuple[int, int]

                # Make the move temporarily to check for legality
                if self.move_piece(pos, move, color, True):
                    legal_moves.append({'start': pos, 'end': move})
        return legal_moves

    def undo_move(self, start: Tuple[int, int], end: Tuple[int, int], color: str, target_piece: Optional[ChessPiece]) -> None:
        """Undo a move that was made."""
        start_x, start_y = start
        end_x, end_y = end
        piece: ChessPiece = self.board[end_x][end_y]
        self.board[end_x][end_y] = None
        self.board[start_x][start_y] = piece

        # Check if the was a piece at the end square
        if target_piece:
            self.board[end_x][end_y] = target_piece

        # Check for castling move
        if isinstance(piece, King) and abs(start_x - end_x) == 2 and start_y == end_y:
            # Kingside castling
            if (end_x == 6):
                self.board[7][start_y] = self.board[5][start_y]
                self.board[5][start_y] = None
            # Queenside castling
            elif (end_x == 2):
                self.board[0][start_y] = self.board[3][start_y]
                self.board[3][start_y] = None

        # Check for en passant move
        if (isinstance(piece, Pawn) and start_x != end_x and not target_piece):
            opponent_color = 'black' if color == 'white' else 'white'
            self.board[end_x][start_y] = Pawn(opponent_color)

    def undo_moves(self) -> None:
        """This method restores the board to its previous states using the FEN stack. It's slower than undo_move."""
        if not self.fen_stack:
            raise ValueError("No moves to undo.")

        # Pop the last FEN string and restore the board state
        last_fen: str = self.fen_stack.pop()
        self.from_fen(last_fen)
 