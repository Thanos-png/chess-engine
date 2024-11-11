#!/usr/bin/env python3

from board import ChessBoard
from utils import parse_position

def main():
    board = ChessBoard()
    turn = board.turn
    # Those variables are only used if we want to implement FEN notation and load a game halfway in 
    # castling_rights = board.castling_rights
    # en_passant_square = board.en_passant_square
    # halfmove_clock = board.halfmove_clock
    fullmove_number = board.fullmove_number
    last_move = None  # To track last move for en passant

    while True:
        board.display()
        print(f"{turn.capitalize()}'s move")

        # Update turn
        board.setTurn(turn)

        # Check for checkmate or stalemate
        if not board.has_legal_moves(turn):
            break

        move = input("Enter your move: ").strip().lower()

        try:
            start_str, end_str = move.split()
            start = parse_position(start_str)
            end = parse_position(end_str)
            piece = board.board[start[0]][start[1]]

            if piece and piece.color == turn:
                prev_en_passant_square = board.en_passant_square
                board.updateEnPassantSquare(start, end, turn, last_move)
                if board.move_piece(start, end, turn, last_move):
                    if turn == 'white':
                        fullmove_number += 1
                        board.setFullMoveNumber(fullmove_number)
                    turn = 'black' if turn == 'white' else 'white'
                    last_move = (start, end, piece)
                else:
                    board.setEnPassantSquare(prev_en_passant_square)
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
