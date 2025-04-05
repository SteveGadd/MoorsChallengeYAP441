"""Base class for all AI implementations."""

from abc import ABC, abstractmethod
from ..constants import BLACK, BOARD_SIZE
from typing import Optional, Tuple
from ..board import OthelloBoard

class BaseAI(ABC):
    def __init__(self, color: Tuple[int, int, int]):
        self.color = color

    @abstractmethod
    def get_move(self, board: OthelloBoard) -> Optional[Tuple[int, int]]:
        """Get the best move for the current board state."""
        pass

    def _evaluate_board(self, board: OthelloBoard) -> float:
        """Basic evaluation function that can be overridden by specific implementations."""
        # Piece count heuristic
        black_count, white_count = board.get_score()
        piece_count = black_count - white_count if self.color == BLACK else white_count - black_count

        # Position heuristic - corners and edges are more valuable
        position_score = 0
        corner_value = 4.0
        edge_value = 2.0

        # Corner positions
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        for row, col in corners:
            if board.board[row][col] == self.color:
                position_score += corner_value
            elif board.board[row][col] == board._opposite_color():
                position_score -= corner_value

        # Edge positions
        for i in range(BOARD_SIZE):
            # Top and bottom edges
            for row in [0, BOARD_SIZE-1]:
                if board.board[row][i] == self.color:
                    position_score += edge_value
                elif board.board[row][i] == board._opposite_color():
                    position_score -= edge_value
            
            # Left and right edges
            for col in [0, BOARD_SIZE-1]:
                if board.board[i][col] == self.color:
                    position_score += edge_value
                elif board.board[i][col] == board._opposite_color():
                    position_score -= edge_value

        # Combine heuristics
        return piece_count + position_score 