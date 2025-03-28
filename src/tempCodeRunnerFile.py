"""AI player implementation using minimax algorithm with alpha-beta pruning."""

from typing import Tuple, Optional
from .constants import BOARD_SIZE, BLACK, WHITE, MAX_DEPTH
from .board import OthelloBoard

class OthelloAI:
    def __init__(self, color: Tuple[int, int, int]):
        self.color = color

    def get_move(self, board: OthelloBoard) -> Optional[Tuple[int, int]]:
        """Get the best move for the AI player using minimax with alpha-beta pruning."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_move = None

        for move in valid_moves:
            # Try the move on a cloned board
            new_board = board.clone()
            new_board.make_move(*move)
            
            # Get the score for this move
            score = self._minimax(new_board, MAX_DEPTH - 1, float('-inf'), float('inf'), False)
            
            if score > best_score:
                best_score = score
                best_move = move

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

    def _evaluate_board(self, board: OthelloBoard) -> float:
        """Evaluate the board position for the AI player."""
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