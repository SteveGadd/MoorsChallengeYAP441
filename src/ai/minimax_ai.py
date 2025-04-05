"""Minimax AI implementation with alpha-beta pruning."""

from typing import Optional, Tuple
from ..constants import MAX_DEPTH
from ..board import OthelloBoard
from .base_ai import BaseAI

class MinimaxAI(BaseAI):
    def get_move(self, board: OthelloBoard) -> Optional[Tuple[int, int]]:
        """Get the best move using minimax with alpha-beta pruning."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        for move in valid_moves:
            # Try the move on a cloned board
            new_board = board.clone()
            new_board.make_move(*move)
            
            # Get the score for this move
            score = self._minimax(new_board, MAX_DEPTH - 1, alpha, beta, False)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return best_move

    def _minimax(self, board: OthelloBoard, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self._evaluate_board(board)

        valid_moves = board.get_valid_moves()
        if not valid_moves:
            # If no moves available, pass turn to opponent
            board.current_player = board._opposite_color()
            if not board.get_valid_moves():
                # Game is over, evaluate final position
                return self._evaluate_board(board)
            return self._minimax(board, depth - 1, alpha, beta, not maximizing)

        if maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                new_board = board.clone()
                new_board.make_move(*move)
                eval = self._minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = board.clone()
                new_board.make_move(*move)
                eval = self._minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval 