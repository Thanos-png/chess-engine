#!/usr/bin/env python3

from board import ChessBoard
from utils import parse_position
from evaluate import ChessEngine
from pieces.rook import Rook
from pieces.king import King
import time


def main():
    board = ChessBoard()
    engine = ChessEngine()
    last_move = None  # To track last move for en passant
    update_threefold_repetition = True
    intErrorFlag = False
    depth = None
    color = None

    # Player chooses depth
    while depth not in ["1", "2", "3", "4", ""]:
        if intErrorFlag:
            print(f"{depth} is not a valid number.")
        depth = input("Choose the depth of the engine: ").strip()
        intErrorFlag = True
    if (depth == ""):
        depth = "3"

    # Player chooses color
    while color not in ['white', 'black', 'w', 'b', '']:
        color = input("Choose your color (white/black): ").strip().lower()
    if color == 'w':
        color = 'white'
    elif color == 'b':
        color = 'black'

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
        engineflag = False
        if turn != color:
            engineflag = True

            # Start the timer
            start_time = time.time()

            print("Engine is thinking...\n")
            move = engine.find_best_move(board, depth=int(depth))

            # End the timer
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Print the time taken
            print(f"Engine took {elapsed_time:.2f} seconds to decide on the move.")
        else:
            move = input("Enter your move: ").strip().lower()

        if move == 'resign' or move == 'r':
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
                if board.move_piece(start, end, turn, False, engineflag):
                    turn = board.updateTurn()
                    last_move = (start, end, piece)
                    board.updateEnPassantSquare(turn, last_move)
                    board.updateFENstack()
                    update_threefold_repetition = True

                    # Update the has_move atributes for the engine's color in case the engine played a move
                    # Player's has_move atributes are been updated inside the move_piece_helper() function
                    if (engineflag):
                        x, y = end
                        if isinstance(board.board[x][y], King):
                            board.board[x][y].has_moved = True
                            # Castling move
                            if abs(start[0] - end[0]) == 2:
                                if end[0] == 6:  # Kingside
                                    if not (turn == 'white'):  # It's "not" because the turn has been updated already
                                        rook: Rook = board.pieces[color][(5, 0)]  # It's (5, 0) because the castling move has already been played
                                    else:
                                        rook: Rook = board.pieces[color][(5, 7)]
                                elif end[0] == 2:  # Queenside
                                    if not (turn == 'white'):
                                        rook: Rook = board.pieces[color][(3, 0)]
                                    else:
                                        rook: Rook = board.pieces[color][(3, 7)]
                                rook.has_moved = True
                        elif isinstance(board.board[x][y], Rook):
                            board.board[x][y].has_moved = True
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
