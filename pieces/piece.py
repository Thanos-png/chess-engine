
class ChessPiece:
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, start, end, board):
        raise NotImplementedError("This method should be implemented by subclasses.")