
from pieces.pawn import Pawn
from pieces.king import King
from math import inf
from utils import to_square_notation

class ChessEngine:
    """Evaluate a chess board using a heuristic evaluation and perform Minimax with Alpha-Beta Pruning."""

    def __init__(self):
        # Assign static values to pieces for the heuristic
        self.piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3.5,
            'rook': 5,
            'queen': 9,
            'king': 1000  # King is invaluable for evaluation
        }

        self.position_values = {
            'pawn': [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
                [0, 0, 0, 2, 2, 0, 0, 0],
                [0.5, -0.5, -1, -0.5, -0.5, -1, -0.5, 0.5],
                [0.5, 1, 1, -2, -2, 1, 1, 0.5],
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
                [0.5, 1, 1, 1, 1, 1, 1, 0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                [0, 0, 0, 0.5, 0.5, 0, 0, 0]
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
                [1.5, 1.5, 0, 0, 0, 0, 1.5, 1.5],
                [2, 3, 1.5, 0, 0, 1, 3, 2]
            ]
        }

    def evaluate_board(self, board):
        """Evaluate the board state based on material advantage and return the evaluation 
        score where positive values favor white and negative values favor black."""
        white_score = 0
        black_score = 0

        # Iterate over all pieces
        for pos, piece in board.pieces['white'].items():
            white_score += self.evaluate_piece(piece, pos, 'white', board)

        for pos, piece in board.pieces['black'].items():
            black_score += self.evaluate_piece(piece, pos, 'black', board)

        # Positive score favors white, negative score favors black
        return white_score - black_score

    def evaluate_piece(self, piece, position, color, board):
        """Evaluate the value of a single piece, including material, position, and special rules."""
        piece_type = type(piece).__name__.lower()
        # Add material value
        value = self.piece_values[piece_type]

        # Add positional value
        value += self.evaluate_position(piece_type, position, color)

        # Special considerations for pawns
        if piece_type == 'pawn':
            value += self.evaluate_pawn_structure(position, color, board)

        # Add penalties for king safety
        if piece_type == 'king':
            value += self.evaluate_king_safety(position, color)

        return value

    def evaluate_position(self, piece_type, position, color):
        """Evaluate the positional value with bonuses/penalties based on piece-tables."""
        x, y = position
        if color == 'black':
            # Flip the board for black pieces
            x, y = 7 - x, 7 - y

        # Get the positional value from the piece's table
        position_value = self.position_values[piece_type][y][x]

        return position_value

    def evaluate_pawn_structure(self, position, color, board):
        """Evaluate the pawn structure for penalties like doubled, isolated."""
        x, y = position
        penalty = 0
        isolated = True

        # Check for doubled pawns
        for i in range(1, 4):
            if (x, y + i) in board.pieces[color] and isinstance(board.pieces[color][(x, y + i)], Pawn):
                penalty -= 1  # Doubled pawns are a weakness

        # Check for isolated pawns
        for pos, piece_type in board.pieces[color].items():
            if isinstance(piece_type, Pawn):
                if (pos[1] - 1, pos[0]) in board.pieces[color] or (pos[1] + 1, pos[0]) in board.pieces[color]:
                    isolated = False
        if isolated:
            penalty -= 0.5  # Isolated pawns have no support

        return penalty

    def evaluate_king_safety(self, position, color):
        """Evaluate the king's safety by making sure that he cover."""
        x, y = position
        penalty = 0

        return penalty

    def minimax(self, board, depth, alpha, beta, maximizing_player, original_board):
        """Perform the Minimax algorithm with alpha-beta pruning and return the 
        evaluation score of the best move for the current player."""
        if depth == 0 or board.has_legal_moves(board.turn, True) is False:
            # Restore the board state
            board.board = original_board.board
            board.pieces = original_board.pieces
            board.white_king_position = original_board.white_king_position
            board.black_king_position = original_board.black_king_position
            board.turn = original_board.turn
            board.castling_rights = original_board.castling_rights
            board.en_passant_square = original_board.en_passant_square
            board.halfmove_clock = original_board.halfmove_clock
            board.fullmove_number = original_board.fullmove_number
            board.board_history = original_board.board_history
            board.fen_stack = original_board.fen_stack

            return self.evaluate_board(board)

        if maximizing_player == 'white':
            max_eval = -inf
            for move in board.generate_legal_moves('white'):
                # Save the board state before making the move
                original_board = board.clone()

                # Make the move on the board
                piece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
                target_piece = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
                board.move_piece(move['start'], move['end'], 'white')

                # Update the turn, en passant square, FEN stack and evaluate the state
                board.updateTurn()
                last_move = (move['start'], move['end'], piece)
                board.updateEnPassantSquare(board.turn, last_move)
                board.updateFENstack()
                evaluation = self.minimax(board, depth - 1, alpha, beta, 'black', original_board)

                # Restore the board state
                board.board = original_board.board
                board.pieces = original_board.pieces
                board.white_king_position = original_board.white_king_position
                board.black_king_position = original_board.black_king_position
                board.turn = original_board.turn
                board.castling_rights = original_board.castling_rights
                board.en_passant_square = original_board.en_passant_square
                board.halfmove_clock = original_board.halfmove_clock
                board.fullmove_number = original_board.fullmove_number
                board.board_history = original_board.board_history
                board.fen_stack = original_board.fen_stack

                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = inf
            for move in board.generate_legal_moves('black'):
                # Save the board state before making the move
                original_board = board.clone()

                # Make the move on the board
                piece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
                target_piece = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
                board.move_piece(move['start'], move['end'], 'black')

                # Update the turn, en passant square, FEN stack and evaluate the state
                board.updateTurn()
                last_move = (move['start'], move['end'], piece)
                board.updateEnPassantSquare(board.turn, last_move)
                board.updateFENstack()
                evaluation = self.minimax(board, depth - 1, alpha, beta, 'white', original_board)

                # Restore the board state
                board.board = original_board.board
                board.pieces = original_board.pieces
                board.white_king_position = original_board.white_king_position
                board.black_king_position = original_board.black_king_position
                board.turn = original_board.turn
                board.castling_rights = original_board.castling_rights
                board.en_passant_square = original_board.en_passant_square
                board.halfmove_clock = original_board.halfmove_clock
                board.fullmove_number = original_board.fullmove_number
                board.board_history = original_board.board_history
                board.fen_stack = original_board.fen_stack

                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def find_best_move(self, board, depth):
        """Find the best move for the current player using Minimax with Alpha-Beta Pruning 
        and return the best move for the current player in the format "e2 e4"."""
        best_move = None
        best_value = -inf if board.turn == 'white' else inf

        for move in board.generate_legal_moves(board.turn):
            # Save the board state before making the move
            original_board = board.clone()

            # Make the move on the board
            piece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
            target_piece = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
            board.move_piece(move['start'], move['end'], board.turn)

            # Update the turn, en passant square, FEN stack and evaluate the state
            board.updateTurn()
            last_move = (move['start'], move['end'], piece)
            board.updateEnPassantSquare(board.turn, last_move)
            board.updateFENstack()
            evaluation = self.minimax(board, depth - 1, -inf, inf, board.turn, original_board)

            # Restore the board state
            board.board = original_board.board
            board.pieces = original_board.pieces
            board.white_king_position = original_board.white_king_position
            board.black_king_position = original_board.black_king_position
            board.turn = original_board.turn
            board.castling_rights = original_board.castling_rights
            board.en_passant_square = original_board.en_passant_square
            board.halfmove_clock = original_board.halfmove_clock
            board.fullmove_number = original_board.fullmove_number
            board.board_history = original_board.board_history
            board.fen_stack = original_board.fen_stack

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
            start_square = to_square_notation(best_move['start'])
            end_square = to_square_notation(best_move['end'])
            return f"{start_square} {end_square}"

        # No valid moves available
        return None
