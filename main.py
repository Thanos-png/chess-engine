#!/usr/bin/env python3

from board import ChessBoard
from utils import parse_position
from evaluate import ChessEngine
import time

def main():
    board = ChessBoard()
    engine = ChessEngine()
    last_move = None  # To track last move for en passant
    update_threefold_repetition = True
    color = None

    # Player chooses color
    while color not in ['white', 'black', 'w', 'b']:
        color = input("Choose your color (white/black): ").strip().lower()

    while True:
        turn = board.turn
        board.display()

        # Check for threefold repetition
        if update_threefold_repetition and board.checkThreefoldRepetition():
            break
        update_threefold_repetition = False

        # Check for fifty-move rule
        if board.checkFiftyMoveRule():
            break

        # Check for checkmate or stalemate
        if not board.has_legal_moves(turn):
            break

        if board.checkInsufficientMaterial():
            print("Draw by Insufficient Material.")
            break

        # Update turn
        print(f"{turn.capitalize()}'s move")

        # Get move
        if turn != color:
            # Start the timer
            start_time = time.time()

            print("Engine is thinking...")
            move = engine.find_best_move(board, depth=4)

            # End the timer
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Print the time taken
            print(f"Engine took {elapsed_time:.2f} seconds to decide on the move.")
        else:
            move = input("Enter your move: ").strip().lower()

        if move == 'resign':
            print(f"{turn.capitalize()} resigns. {('Black' if turn == 'white' else 'White')} wins!")
            break

        if move == 'fen':
            board.from_fen(input("Enter FEN: "))
            continue

        try:
            start_str, end_str = move.split()
            start = parse_position(start_str)
            end = parse_position(end_str)
            piece = board.board[start[0]][start[1]]

            if piece and piece.color == turn:
                if board.move_piece(start, end, turn):
                    turn = board.updateTurn()
                    last_move = (start, end, piece)
                    board.updateEnPassantSquare(turn, last_move)
                    board.updateFENstack()
                    update_threefold_repetition = True
                else:
                    print("""
Invalid move, try again.""")
            else:
                print("""
No valid piece to move at that position.""")
        except (ValueError, IndexError):
            print("""
Invalid input, format should be 'e2 e4'.""")

if __name__ == "__main__":
    main()
