# chess-engine
A robust chess engine implementation built using Minimax and Alpha-Beta Pruning algorithms. This engine evaluates positions heuristically and supports standard chess gameplay features.

## Features
* Implements Minimax with Alpha-Beta Pruning for optimal decision-making.
* Supports essential chess rules:
    * Castling (Kingside and Queenside).
    * En Passant.
    * Pawn promotion.
* Implements a FEN string input option so that you can input your games.
* Utilizes a Polyglot opening book for quick and accurate early-game decisions.
* Includes a command-line interface(CLI) for playing against the engine.

## Requirements
* Python 3.8 or higher.

## Installation
Clone this repository:

```
git clone https://github.com/Thanos-png/chess-engine.git
cd chess-engine
```

## Run
To start a game run the following command on your CLI:

```python3 main.py```

## How to Play
Once the game starts, follow the prompts and choose a color to play as.  
You can type ```w``` as well as ```white``` and ```b``` as well as ```black```  
If you want the engine to play with itself you can press ```Enter```  
After you chose your color you can input your moves.  
(e.g., ```e2 e4``` for moving a pawn from ```e2``` to ```e4```).

### Example Gameplay
```
Choose your color (white/black): w

  a b c d e f g h
8 ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ 8
7 ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ 7
6 . . . . . . . . 6
5 . . . . . . . . 5
4 . . . . . . . . 4
3 . . . . . . . . 3
2 ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙ 2
1 ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ 1
  a b c d e f g h

White's move
Enter your move: e2 e4
```

## Contributing
Contributions are welcome! Please feel free to fork the repository and submit a pull request.

### Todo
1. Add a Transposition Table
2. Add an Endgame Table
3. Bitmap Implementation

## Contact
For questions or feedback, feel free to reach me out:
* **Email:** thanos.panagiotidis@protonmail.com
