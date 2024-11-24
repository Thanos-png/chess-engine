
from math import inf

class HeuristicEvaluator:
    """Evaluate a chess board using a heuristic and perform Minimax with Alpha-Beta Pruning."""

    def __init__(self):
        # Assign static values to pieces for the heuristic
        self.piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3.5,
            'rook': 5,
            'queen': 9,
            'king': inf  # King is invaluable for evaluation, but we don't count it in heuristic
        }

    def evaluate_board(self, board):
        """
        Evaluate the board state based on material advantage.
        
        Args:
            board (ChessBoard): The chess board instance.
        
        Returns:
            int: The evaluation score where positive values favor white and negative values favor black.
        """
        white_score = 0
        black_score = 0

        # Use the piece dictionaries for efficiency
        for piece_type, positions in board.white_pieces.items():
            white_score += len(positions) * self.piece_values[piece_type]

        for piece_type, positions in board.black_pieces.items():
            black_score += len(positions) * self.piece_values[piece_type]

        # Positive score favors white, negative score favors black
        return white_score - black_score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Perform the Minimax algorithm with alpha-beta pruning.

        Args:
            board (ChessBoard): The chess board instance.
            depth (int): The depth of the search.
            alpha (int): The alpha value for pruning.
            beta (int): The beta value for pruning.
            maximizing_player (string): "white" if maximizing player (white), "black" if minimizing player (black).

        Returns:
            int: The evaluation score of the best move for the current player.
        """
        if depth == 0 or board.has_legal_moves(board.turn, True) is False:
            return self.evaluate_board(board)

        if maximizing_player == 'white':
            max_eval = -inf
            for move in board.generate_legal_moves('white'):
                board.move_piece(move['start'], move['end'], 'white')
                evaluation = self.minimax(board, depth - 1, alpha, beta, 'black')
                board.undo_move(move)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = inf
            for move in board.generate_legal_moves('black'):
                board.move_piece(move['start'], move['end'], 'black')
                evaluation = self.minimax(board, depth - 1, alpha, beta, 'white')
                board.undo_move(move)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def find_best_move(self, board, depth):
        """
        Find the best move for the current player using Minimax with Alpha-Beta Pruning.

        Args:
            board (ChessBoard): The chess board instance.
            depth (int): The depth of the search.

        Returns:
            dict: The best move for the current player in the format {'start': (x1, y1), 'end': (x2, y2)}.
        """
        best_move = None
        best_value = -inf if board.turn == 'white' else inf

        for move in board.generate_legal_moves(board.turn):
            board.move_piece(move['start'], move['end'], board.turn)
            evaluation = self.minimax(board, depth - 1, -inf, inf, board.turn == 'black')
            board.undo_move(move)

            if board.turn == 'white':
                if evaluation > best_value:
                    best_value = evaluation
                    best_move = move
            else:
                if evaluation < best_value:
                    best_value = evaluation
                    best_move = move

        return best_move
