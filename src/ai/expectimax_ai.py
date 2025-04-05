"""Expectimax AI implementation."""

from typing import Optional, Tuple, List
import random
from ..constants import MAX_DEPTH, BOARD_SIZE
from ..board import OthelloBoard
from .base_ai import BaseAI

class ExpectimaxAI(BaseAI):
    def __init__(self, color: Tuple[int, int, int], opponent_randomness: float = 0.3):
        super().__init__(color)
        self.opponent_randomness = opponent_randomness  # Probability of opponent making a random move

    def get_move(self, board: OthelloBoard) -> Optional[Tuple[int, int]]:
        """Get the best move using expectimax."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_move = None

        for move in valid_moves:
            # Try the move on a cloned board
            new_board = board.clone()
            new_board.make_move(*move)
            
            # Get the expected score for this move
            score = self._expectimax(new_board, MAX_DEPTH - 1, False)
            
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _expectimax(self, board: OthelloBoard, depth: int, maximizing: bool) -> float:
        """Expectimax algorithm implementation."""
        if depth == 0:
            return self._evaluate_board(board)

        valid_moves = board.get_valid_moves()
        if not valid_moves:
            # If no moves available, pass turn to opponent
            board.current_player = board._opposite_color()
            if not board.get_valid_moves():
                # Game is over, evaluate final position
                return self._evaluate_board(board)
            return self._expectimax(board, depth - 1, not maximizing)

        if maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                new_board = board.clone()
                new_board.make_move(*move)
                eval = self._expectimax(new_board, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            # Chance node - opponent might make a random move
            if random.random() < self.opponent_randomness:
                # Opponent makes a random move
                move = random.choice(valid_moves)
                new_board = board.clone()
                new_board.make_move(*move)
                return self._expectimax(new_board, depth - 1, True)
            else:
                # Opponent makes an optimal move (minimizing)
                min_eval = float('inf')
                for move in valid_moves:
                    new_board = board.clone()
                    new_board.make_move(*move)
                    eval = self._expectimax(new_board, depth - 1, True)
                    min_eval = min(min_eval, eval)
                return min_eval

    def _evaluate_board(self, board: OthelloBoard) -> float:
        """Enhanced evaluation function for expectimax."""
        # Basic position evaluation
        base_score = super()._evaluate_board(board)

        # Add mobility heuristic
        mobility = len(board.get_valid_moves())
        if board.current_player == self.color:
            mobility_score = mobility * 0.5
        else:
            mobility_score = -mobility * 0.5

        # Add stability heuristic
        stability_score = self._calculate_stability(board)

        return base_score + mobility_score + stability_score

    def _calculate_stability(self, board: OthelloBoard) -> float:
        """Calculate stability score for pieces."""
        stability_score = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board.board[row][col] == self.color:
                    stability_score += self._is_stable(board, row, col)
                elif board.board[row][col] == board._opposite_color():
                    stability_score -= self._is_stable(board, row, col)
        return stability_score

    def _is_stable(self, board: OthelloBoard, row: int, col: int) -> float:
        """Check if a piece is stable (cannot be flipped)."""
        if board.board[row][col] is None:
            return 0

        # Check if piece is in a corner
        if (row, col) in [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]:
            return 2.0

        # Check if piece is on an edge
        if row == 0 or row == BOARD_SIZE-1 or col == 0 or col == BOARD_SIZE-1:
            return 1.0

        # Check if piece is in a stable position (surrounded by same color)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]
        stability = 0
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if board.board[r][c] == board.board[row][col]:
                    stability += 0.1
        return stability 