
from typing import Optional, Dict, Tuple

class ChessPiece:
    def __init__(self, color: str) -> None:
        self.color = color

    def __name__(self) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def __str__(self) -> str:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int], board: list[list[Optional['ChessPiece']]]) -> bool:
        raise NotImplementedError("This method should be implemented by subclasses.")
