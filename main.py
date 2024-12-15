#!/usr/bin/env python3

from board import ChessBoard
from utils import parse_position, to_square_notation
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
    dynamicDepth = False
    depth = None
    color = None

    # Player chooses depth
    while depth not in ["1", "2", "3", "4", "5", ""]:
        if intErrorFlag:
            print(f"{depth} is not a valid number.")
        depth = input("Choose the depth of the engine: ").strip()
        intErrorFlag = True
    if (depth == ""):
        dynamicDepth = True
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
        if update_threefold_repetition and last_move:
            print(f"Last move: {to_square_notation(last_move[0])} {to_square_notation(last_move[1])}")

        # Check for threefold repetition
        if (update_threefold_repetition and board.checkThreefoldRepetition()):
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
        print(f"It's {turn.capitalize()}'s move\n")

        # Get move
        engineFlag = False
        if (turn != color):
            engineFlag = True

            # Start the timer
            start_time = time.time()

            print("Engine is thinking...\n")
            move = engine.find_best_move(board, depth=int(depth))

            # End the timer
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Print the time taken
            print(f"Engine took {elapsed_time:.2f} seconds to decide on the move.")

            # If the dynamic depth is enabled check if the depth of the search can be increased
            if (dynamicDepth and board.fullmove_number >= 16 and elapsed_time < 0.25):
                depth = int(depth) + 1
        else:
            move = input("Enter your move: ").strip().lower()

        if (move == 'resign' or move == 'r'):
            print(f"{turn.capitalize()} resigns. {('Black' if turn == 'white' else 'White')} wins!")
            break

        if (move == 'fen'):
            board.from_fen(input("Enter FEN: "))
            continue

        try:
            start_str, end_str = move.split()
            start = parse_position(start_str)
            end = parse_position(end_str)
            piece = board.board[start[0]][start[1]]

            if (piece and piece.color == turn):
                if board.move_piece(start, end, turn, False, engineFlag):
                    turn = board.updateTurn()
                    last_move = (start, end, piece)
                    board.updateEnPassantSquare(turn, last_move)
                    board.updateFENstack()
                    update_threefold_repetition = True

                    # Update the has_move atributes for the engine's color in case the engine played a move
                    # Player's has_move atributes are been updated inside the move_piece_helper() function
                    if (engineFlag):
                        x, y = end
                        if isinstance(board.board[x][y], King):
                            board.board[x][y].has_moved = True
                            # Castling move
                            if (abs(start[0] - end[0]) == 2):
                                if (end[0] == 6):  # Kingside
                                    if (turn == 'white'):
                                        rook: Rook = board.pieces[color][(5, 0)]  # It's (5, 0) because the castling move has already been played
                                    else:
                                        print(board.pieces[color])
                                        rook: Rook = board.pieces[color][(5, 7)]
                                elif (end[0] == 2):  # Queenside
                                    if (turn == 'white'):
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
