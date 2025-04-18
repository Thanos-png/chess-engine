
from typing import Optional, Dict, Tuple
from pieces.piece import ChessPiece
from pieces.pawn import Pawn
from pieces.king import King
from math import inf
from utils import to_square_notation
from board import ChessBoard
from polyglot import Polyglot


class PolyglotEngine:

    def __init__(self, book_path) -> None:
        """Initialize the Polyglot engine with the path to the opening book."""
        self.book_path = book_path
        self.polyglot = Polyglot(book_path)

    def find_move_from_book(self, board: ChessBoard) -> str:
        """Query the Polyglot book for the best move in the current position. 
        Returns the best move in (e.g., 'e2 e4') format, or None if no move found."""
        try:
            best_move: Optional[str] = None
            best_weight: float = -10

            # Change the format and unpack the variables
            pieces, pawns = board.changePiecesFormat(board.pieces)
            pieces: Dict[Tuple[int, int], Tuple[str, str]]
            pawns: Dict[Tuple[int, int], str]
            castling_rights: str = board.changeCastlingRightsFormat(board.castling_rights)
            ep_square: Tuple[int, int] = board.changeEnPassantSquareFormat(board.en_passant_square)

            for weight, uci_move in self.polyglot.reader(board, pieces, castling_rights, ep_square, board.turn, pawns):
                weight: float
                uci_move: str

                if weight > best_weight:
                    best_weight = weight
                    best_move = uci_move

            if best_move:
                return f"{best_move[:2]} {best_move[2:]}"  # Convert UCI 'e2e4' to 'e2 e4' format
            return None
        except FileNotFoundError:
            print(f"Error: The file '{self.book_path}' was not found.")
            return None
        except Exception as e:
            print(f"Error reading the Polyglot book: {e}")
            return None


class ChessEngine:
    """Evaluate a chess board using a heuristic evaluation and perform Minimax with Alpha-Beta Pruning."""

    def __init__(self) -> None:
        self.numberOfFinishNodes = 0
        self.polyFlag = True  # Should the engine look up the book

        # Assign static values to pieces for the heuristic
        self.piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3.5,
            'rook': 5,
            'queen': 9,
            'king': 10000  # King is invaluable for evaluation
        }

        # Piece-tables. They ensure a quick evaluation of a piece's position
        self.positional_values = {
            'pawn': [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [1, 1, 2, 2.5, 2.5, 2, 1, 1],
                [0.5, 0.5, 1, 2, 2, 1, 0.5, 0.5],
                [0, 0, 0, 1.5, 1.5, 0, 0, 0],
                [0.8, 0.7, 0.5, -0.5, -0.5, -1, 0.7, 0.8],
                [0.7, 1, 1, -2, -2, 1, 1, 0.7],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            'knight': [
                [-5, -4, -3, -3, -3, -3, -4, -5],
                [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
                [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
                [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
                [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
                [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
                [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
                [-5, -4, -3, -3, -3, -3, -4, -5]
            ],
            'bishop': [
                [-2, -1, -1, -1, -1, -1, -1, -2],
                [-1.5, 0, 0, 0, 0, 0, 0, -1.5],
                [-1.5, 0, 0.5, 1, 1, 0.5, 0, -1.5],
                [-1.5, 1, 0.5, 1, 1, 0.5, 1, -1.5],
                [-1.5, 0, 1, 1, 1, 1, 0, -1.5],
                [-1.5, 1, 1, 1, 1, 1, 1, -1.5],
                [-1, 1, 0, 0, 0, 0, 1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1]
            ],
            'rook': [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0.7, 1, 1, 1, 1, 1, 1, 0.7],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [0, 0, 0.2, 0.5, 0.5, 0.2, 0, 0]
            ],
            'queen': [
                [-2, -1, -0.5, -0.5, -0.5, -0.5, -1, -2],
                [-1, 0, 0, 0, 0, 0, 0, -1],
                [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
                [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
                [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
                [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
                [-1, 0, 0.5, 0, 0, 0, 0, -1],
                [-2, -1, -0.5, -0.5, -0.5, -0.5, -1, -2]
            ],
            'king': [
                [-3, -4, -4, -5, -5, -4, -4, -3],
                [-3, -4, -4, -5, -5, -4, -4, -3],
                [-3, -4, -4, -5, -5, -4, -4, -3],
                [-3, -4, -4, -5, -5, -4, -4, -3],
                [-2, -3, -3, -4, -4, -3, -3, -2],
                [-1, -2, -2, -2, -2, -2, -2, -1],
                [1.5, 1.5, -0.3, -0.3, -0.3, -0.3, 1.5, 1.5],
                [2, 3, 3, -0.3, 0, 0.5, 3, 2]
            ]
        }

    def evaluate_board(self, board: ChessBoard) -> float:
        """Evaluate the board state based on material advantage and return the evaluation 
        score where positive values favor white and negative values favor black."""
        white_score = 0
        black_score = 0

        # Iterate over all pieces
        board.pieces: Dict[str, Dict[Tuple[int, int], ChessPiece]]
        for pos, piece in board.pieces['white'].items():
            pos: Tuple[int, int]
            piece: ChessPiece

            white_score += self.evaluate_piece(piece, pos, 'white', board)

        for pos, piece in board.pieces['black'].items():
            pos: Tuple[int, int]
            piece: ChessPiece

            black_score += self.evaluate_piece(piece, pos, 'black', board)

        self.numberOfFinishNodes += 1
        # Positive score favors white, negative score favors black
        return white_score - black_score

    def evaluate_piece(self, piece: ChessPiece, position: Tuple[int, int], color: str, board: ChessBoard) -> float:
        """Evaluate the value of a single piece, including material, position, and special rules."""
        piece_type: str = type(piece).__name__.lower()
        # Add material value
        value = 3 * self.piece_values[piece_type]

        # Add positional value
        value += 0.1 * self.evaluate_position(piece_type, position, color)

        # Special considerations for pawns
        if piece_type == 'pawn':
            value += self.evaluate_pawn_structure(position, color, board)

        # Add penalties for king safety
        if piece_type == 'king':
            value += 0.001 * self.evaluate_king_safety(position, color, board)

        return round(value, 4)

    def evaluate_position(self, piece_type: str, position: Tuple[int, int], color: str) -> float:
        """Evaluate the positional value with bonuses/penalties based on piece-tables."""
        x, y = position

        # Get the positional value from the piece's table
        positional_value = self.positional_values[piece_type][y][x]

        # Variables to determine the importance of which piece the engine should move each time
        if (piece_type == "Pawn"):
            positional_value *= 0.8
        elif (piece_type == "Knight"):
            positional_value *= 0.7
        elif (piece_type == "Bishop"):
            positional_value *= 1.2
        elif (piece_type == "Queen"):
            positional_value *= 1.4

        return positional_value

    def evaluate_pawn_structure(self, position: Tuple[int, int], color: str, board: ChessBoard) -> float:
        """Evaluate the pawn structure for penalties like doubled, isolated."""
        x, y = position
        penalty = 0
        isolated = True

        # Check for doubled pawns
        for i in range(1, 4):
            board.pieces[color]: Dict[Tuple[int, int], ChessPiece]

            if (x, y + i) in board.pieces[color] and isinstance(board.pieces[color][(x, y + i)], Pawn):
                penalty -= 0.5  # Doubled pawns are a weakness

        # Check for isolated pawns
        for pos, piece_type in board.pieces[color].items():
            pos: Tuple[int, int]
            piece_type: ChessPiece

            if isinstance(piece_type, Pawn):
                if (pos[1] - 1, pos[0]) in board.pieces[color] or (pos[1] + 1, pos[0]) in board.pieces[color]:
                    isolated = False
        if isolated:
            penalty -= 0.3  # Isolated pawns have no support and must be punished

        return penalty

    def evaluate_king_safety(self, position: Tuple[int, int], color: str, board: ChessBoard) -> float:
        """Evaluate the king's safety by making sure that he is covered."""
        x , y = position
        penalty = 0

        # Calculate king safety from the king's table
        positional_value = self.positional_values['king'][y][x] * 0.6

        king: King = board.board[x][y]
        if king.is_in_check(color, board):
            penalty -= 0.4

        return penalty + positional_value

    def restoreBoardState(self, board: ChessBoard, original_board: ChessBoard) -> None:
        """Restores every value of the chess board."""
        board.board: list[list[Optional[ChessPiece]]] = original_board.board
        board.pieces: Dict[str, Dict[Tuple[int, int], ChessPiece]] = original_board.pieces
        board.white_king_position: Tuple[int, int] = original_board.white_king_position
        board.black_king_position: Tuple[int, int] = original_board.black_king_position
        board.turn: str = original_board.turn
        board.castling_rights: Dict[str, bool] = original_board.castling_rights
        board.en_passant_square: str = original_board.en_passant_square
        board.halfmove_clock: int = original_board.halfmove_clock
        board.fullmove_number: int = original_board.fullmove_number
        board.repetition_count: Dict[int, int] = original_board.repetition_count
        board.fen_stack: list[str] = original_board.fen_stack
        board.stalemate: bool = original_board.stalemate

    def minimax(self, board: ChessBoard, depth: int, alpha: float, beta: float, maximizing_player: str, original_board: ChessBoard) -> float:
        """Perform the Minimax algorithm with alpha-beta pruning and return the 
        evaluation score of the best move for the current player."""
        # Game is solved
        if (board.has_legal_moves(board.turn, True) is False and board.stalemate == False):
            # Restore the board state
            self.restoreBoardState(board, original_board)

            mate_value = 1000000000 if board.turn == 'white' else -1000000000
            return mate_value
        elif (board.has_legal_moves(board.turn, True) is False and board.stalemate == True):
            # Restore the board state
            self.restoreBoardState(board, original_board)

            return 0  # The game is a draw by stalemate
        if board.checkFiftyMoveRule(True):
            # Restore the board state
            self.restoreBoardState(board, original_board)

            return 0  # The game is a draw by fifty-move rule
        if board.checkThreefoldRepetition(True):
            # Restore the board state
            self.restoreBoardState(board, original_board)

            return 0  # The game is a draw by threefold repetition

        # Final tree node
        if (depth == 0):
            evaluation = self.evaluate_board(board)

            # Restore the board state
            self.restoreBoardState(board, original_board)

            return evaluation

        if maximizing_player == 'white':
            max_eval = -inf
            legal_moves = board.generate_legal_moves('white', True)
            for move in legal_moves:
                move: Dict[str, Tuple[int, int]]

                # Save the board state before making the move
                original_board = board.clone()

                # Make the move on the board
                piece: ChessPiece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
                target_piece: Optional[ChessPiece] = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
                board.move_piece(move['start'], move['end'], 'white', False, True)

                # Update the turn, en passant square, FEN stack and evaluate the state
                board.updateTurn()
                last_move = (move['start'], move['end'], piece)
                board.updateEnPassantSquare(board.turn, last_move)
                board.updateFENstack()
                evaluation: float = self.minimax(board, depth - 1, alpha, beta, 'black', original_board)

                # Restore the board state
                self.restoreBoardState(board, original_board)

                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = inf
            legal_moves = board.generate_legal_moves('black', True)
            for move in legal_moves:
                move: Dict[str, Tuple[int, int]]

                # Save the board state before making the move
                original_board = board.clone()

                # Make the move on the board
                piece: ChessPiece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
                target_piece: Optional[ChessPiece] = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
                board.move_piece(move['start'], move['end'], 'black', False, True)

                # Update the turn, en passant square, FEN stack and evaluate the state
                board.updateTurn()
                last_move = (move['start'], move['end'], piece)
                board.updateEnPassantSquare(board.turn, last_move)
                board.updateFENstack()
                evaluation: float = self.minimax(board, depth - 1, alpha, beta, 'white', original_board)

                # Restore the board state
                self.restoreBoardState(board, original_board)

                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def find_best_move(self, board: ChessBoard, depth: int) -> str:
        """Find the best move for the current player using the Polyglot book if possible 
        otherwise fallback to Minimax with Alpha-Beta Pruning and return the best move 
        for the current player in the format "e2 e4"."""
        if self.polyFlag:
            polyglot_engine = PolyglotEngine("opening-book/baron30.bin")
            move: str = polyglot_engine.find_move_from_book(board)

            if move:
                return move
            else:
                self.polyFlag = False

        best_move = None
        best_value = -inf if board.turn == 'white' else inf

        legal_moves = board.generate_legal_moves(board.turn, True)
        for move in legal_moves:
            move: Dict[str, Tuple[int, int]]

            # Save the board state before making the move
            original_board = board.clone()

            # Make the move on the board
            piece: ChessPiece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
            target_piece: Optional[ChessPiece] = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
            board.move_piece(move['start'], move['end'], board.turn, False, True)

            # Update the turn, en passant square, FEN stack and evaluate the state
            board.updateTurn()
            last_move = (move['start'], move['end'], piece)
            board.updateEnPassantSquare(board.turn, last_move)
            board.updateFENstack()
            board.stalemate = False
            evaluation: float = self.minimax(board, depth - 1, -inf, inf, board.turn, original_board)

            # Restore the board state
            self.restoreBoardState(board, original_board)

            # Update the best move based on evaluation
            if board.turn == 'white':
                if evaluation > best_value:
                    best_value = evaluation
                    best_move = move
            else:
                if evaluation < best_value:
                    best_value = evaluation
                    best_move = move

        # Convert the best move to the "e2 e4" format
        if best_move:
            # print("Nodes: ", self.numberOfFinishNodes)  # Debugging

            start_square = to_square_notation(best_move['start'])
            end_square = to_square_notation(best_move['end'])
            return f"{start_square} {end_square}"

        # No valid moves available
        return None
