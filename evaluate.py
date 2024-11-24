
from math import inf

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
            white_score += len(pos) * self.piece_values[type(piece_type).__name__.lower()]

        for pos, piece_type in board.pieces['black'].items():
            black_score += len(pos) * self.piece_values[type(piece_type).__name__.lower()]

        # Positive score favors white, negative score favors black
        return white_score - black_score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """Perform the Minimax algorithm with alpha-beta pruning and return the 
        evaluation score of the best move for the current player."""
        if depth == 0 or board.has_legal_moves(board.turn, True) is False:
            return self.evaluate_board(board)

        if maximizing_player == 'white':
            max_eval = -inf
            for move in board.generate_legal_moves('white'):
                # Save the board state before making the move
                boardprev = board.board
                piecesprev = board.pieces
                white_king_positionprev = board.white_king_position
                black_king_positionprev = board.black_king_position
                turnprev = board.turn
                castling_rightsprev = board.castling_rights
                en_passant_squareprev = board.en_passant_square
                halfmove_clockprev = board.halfmove_clock
                fullmove_numberprev = board.fullmove_number
                board_historyprev = board.board_history
                fen_stackprev = board.fen_stack

                # Make the move on the board
                piece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
                target_piece = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
                print("Piece: ", piece, " Start: ", move['start'], " End: ", move['end'], " Color: White", " Target: ", target_piece)
                board.move_piece(move['start'], move['end'], 'white')

                # Update the turn, en passant square, FEN stack and evaluate the state
                board.updateTurn()
                last_move = (move['start'], move['end'], piece)
                board.updateEnPassantSquare(board.turn, last_move)
                board.updateFENstack()
                evaluation = self.minimax(board, depth - 1, alpha, beta, 'black')

                # Restore the board state
                board.board = boardprev
                board.pieces = piecesprev
                board.white_king_position = white_king_positionprev
                board.black_king_position = black_king_positionprev
                board.turn = turnprev
                board.castling_rights = castling_rightsprev
                board.en_passant_square = en_passant_squareprev
                board.halfmove_clock = halfmove_clockprev
                board.fullmove_number = fullmove_numberprev
                board.board_history = board_historyprev
                board.fen_stack = fen_stackprev

                # Undo the move
                board.undo_move(move['start'], move['end'], 'white', target_piece)

                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = inf
            for move in board.generate_legal_moves('black'):
                # Save the board state before making the move
                boardprev = board.board
                piecesprev = board.pieces
                white_king_positionprev = board.white_king_position
                black_king_positionprev = board.black_king_position
                turnprev = board.turn
                castling_rightsprev = board.castling_rights
                en_passant_squareprev = board.en_passant_square
                halfmove_clockprev = board.halfmove_clock
                fullmove_numberprev = board.fullmove_number
                board_historyprev = board.board_history
                fen_stackprev = board.fen_stack

                # Make the move on the board
                piece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
                target_piece = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
                print("Piece: ", piece, " Start: ", move['start'], " End: ", move['end'], " Color: Black", " Target: ", target_piece)
                board.move_piece(move['start'], move['end'], 'black')

                # Update the turn, en passant square, FEN stack and evaluate the state
                board.updateTurn()
                last_move = (move['start'], move['end'], piece)
                board.updateEnPassantSquare(board.turn, last_move)
                board.updateFENstack()
                evaluation = self.minimax(board, depth - 1, alpha, beta, 'white')

                # Restore the board state
                board.board = boardprev
                board.pieces = piecesprev
                board.white_king_position = white_king_positionprev
                board.black_king_position = black_king_positionprev
                board.turn = turnprev
                board.castling_rights = castling_rightsprev
                board.en_passant_square = en_passant_squareprev
                board.halfmove_clock = halfmove_clockprev
                board.fullmove_number = fullmove_numberprev
                board.board_history = board_historyprev
                board.fen_stack = fen_stackprev

                # Undo the move
                board.undo_move(move['start'], move['end'], 'black', target_piece)

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
            boardprev = board.board
            piecesprev = board.pieces
            white_king_positionprev = board.white_king_position
            black_king_positionprev = board.black_king_position
            turnprev = board.turn
            castling_rightsprev = board.castling_rights
            en_passant_squareprev = board.en_passant_square
            halfmove_clockprev = board.halfmove_clock
            fullmove_numberprev = board.fullmove_number
            board_historyprev = board.board_history
            fen_stackprev = board.fen_stack

            # Make the move on the board
            piece = board.board[move['start'][0]][move['start'][1]]  # Save the moving piece
            target_piece = board.board[move['end'][0]][move['end'][1]]  # Save the target piece (if any)
            board.move_piece(move['start'], move['end'], board.turn)

            # Update the turn, en passant square, FEN stack and evaluate the state
            board.updateTurn()
            last_move = (move['start'], move['end'], piece)
            board.updateEnPassantSquare(board.turn, last_move)
            board.updateFENstack()
            evaluation = self.minimax(board, depth - 1, -inf, inf, board.turn == 'black')

            # Restore the board state
            board.board = boardprev
            board.pieces = piecesprev
            board.white_king_position = white_king_positionprev
            board.black_king_position = black_king_positionprev
            board.turn = turnprev
            board.castling_rights = castling_rightsprev
            board.en_passant_square = en_passant_squareprev
            board.halfmove_clock = halfmove_clockprev
            board.fullmove_number = fullmove_numberprev
            board.board_history = board_historyprev
            board.fen_stack = fen_stackprev

            # Undo the move
            board.undo_move(move['start'], move['end'], board.turn, target_piece)

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
            start_square = self.to_square_notation(best_move['start'])
            end_square = self.to_square_notation(best_move['end'])
            return f"{start_square} {end_square}"

        # No valid moves available
        return None
