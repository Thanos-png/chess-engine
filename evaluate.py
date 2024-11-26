
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
            'king': inf  # King is invaluable for evaluation
        }

    def evaluate_board(self, board):
        """Evaluate the board state based on material advantage and return the evaluation 
        score where positive values favor white and negative values favor black."""
        white_score = 0
        black_score = 0

        # Use the piece dictionaries for efficiency
        for pos, piece_type in board.pieces['white'].items():
            if not isinstance(piece_type, King):
                white_score += len(pos) * self.piece_values[type(piece_type).__name__.lower()]

        for pos, piece_type in board.pieces['black'].items():
            if not isinstance(piece_type, King):
                black_score += len(pos) * self.piece_values[type(piece_type).__name__.lower()]

        # Positive score favors white, negative score favors black
        return white_score - black_score

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

            # Undo the move
            # board.undo_move(move['start'], move['end'], board.turn, target_piece)

            # Update the best move based on evaluation
            if board.turn == 'white':
                print("White Evaluation: ", evaluation)
                if evaluation > best_value:
                    best_value = evaluation
                    best_move = move
            else:
                print("Black Evaluation: ", evaluation)
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
