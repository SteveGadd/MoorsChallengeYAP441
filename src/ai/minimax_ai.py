"""Minimax AI implementation with alpha-beta pruning."""

from typing import Optional, Tuple, List
from ..constants import MAX_DEPTH, BOARD_SIZE, BLACK
from ..board import OthelloBoard
from .base_ai import BaseAI

class MinimaxAI(BaseAI):
    def __init__(self, color: Tuple[int, int, int]):
        super().__init__(color)
        # Position weights for evaluation
        self.position_weights = self._initialize_position_weights()
        # Corner adjacency positions
        self.corner_adjacent = [
            (0, 1), (1, 0), (1, 1),  # Top-left corner
            (0, BOARD_SIZE-2), (1, BOARD_SIZE-1), (1, BOARD_SIZE-2),  # Top-right corner
            (BOARD_SIZE-2, 0), (BOARD_SIZE-1, 1), (BOARD_SIZE-2, 1),  # Bottom-left corner
            (BOARD_SIZE-2, BOARD_SIZE-1), (BOARD_SIZE-1, BOARD_SIZE-2), (BOARD_SIZE-2, BOARD_SIZE-2)  # Bottom-right corner
        ]

    def _initialize_position_weights(self) -> List[List[float]]:
        """Initialize position weights for the board."""
        # These weights are based on Othello strategy research
        weights = [
            [1000.0, -100.0,  20.0,  10.0,  10.0,  20.0, -100.0, 1000.0],
            [-100.0, -200.0,  -5.0,  -5.0,  -5.0,  -5.0, -200.0, -100.0],
            [20.0,   -5.0,    5.0,   3.0,   3.0,   5.0,   -5.0,   20.0],
            [10.0,   -5.0,    3.0,   2.0,   2.0,   3.0,   -5.0,   10.0],
            [10.0,   -5.0,    3.0,   2.0,   2.0,   3.0,   -5.0,   10.0],
            [20.0,   -5.0,    5.0,   3.0,   3.0,   5.0,   -5.0,   20.0],
            [-100.0, -200.0,  -5.0,  -5.0,  -5.0,  -5.0, -200.0, -100.0],
            [1000.0, -100.0,  20.0,  10.0,  10.0,  20.0, -100.0, 1000.0],
        ]
        return weights

    def get_move(self, board: OthelloBoard) -> Optional[Tuple[int, int]]:
        """Get the best move using minimax with alpha-beta pruning."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        # Prioritize corner moves
        corner_moves = []
        edge_moves = []
        other_moves = []
        
        for move in valid_moves:
            row, col = move
            if (row, col) in [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]:
                corner_moves.append(move)
            elif row == 0 or row == BOARD_SIZE-1 or col == 0 or col == BOARD_SIZE-1:
                edge_moves.append(move)
            else:
                other_moves.append(move)
        
        # Try corner moves first
        if corner_moves:
            valid_moves = corner_moves
        # Then edge moves
        elif edge_moves:
            valid_moves = edge_moves

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

    def _evaluate_board(self, board: OthelloBoard) -> float:
        """Enhanced evaluation function for minimax."""
        black_score, white_score = board.get_score()
        total_pieces = black_score + white_score
        score_diff = black_score - white_score if self.color == BLACK else white_score - black_score
        
        # Position evaluation
        position_score = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board.board[row][col] == self.color:
                    position_score += self.position_weights[row][col]
                elif board.board[row][col] == board._opposite_color():
                    position_score -= self.position_weights[row][col]
        
        # Mobility evaluation (relative)
        my_moves = len(board.get_valid_moves())
        board.current_player = board._opposite_color()
        opp_moves = len(board.get_valid_moves())
        board.current_player = self.color  # reset
        mobility_score = (my_moves - opp_moves) * 2.0
        
        # Corner control
        corner_score = self._evaluate_corners(board)
        
        # Edge stability
        edge_score = self._evaluate_edges(board)
        
        # Corner adjacency danger
        danger_score = self._evaluate_corner_danger(board)
        
        # Game phase adjustment
        if total_pieces < 20:  # Early game
            return position_score * 0.6 + mobility_score * 0.4 + corner_score * 0.2 + score_diff * 0.1
        elif total_pieces < 50:  # Middle game
            return position_score * 0.4 + mobility_score * 0.3 + corner_score * 0.3 + edge_score * 0.2 + score_diff * 0.2
        else:  # End game
            return score_diff * 0.8 + corner_score * 0.2 + position_score * 0.1

    def _evaluate_corners(self, board: OthelloBoard) -> float:
        """Evaluate corner control."""
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        corner_score = 0
        for row, col in corners:
            if board.board[row][col] == self.color:
                corner_score += 100.0
            elif board.board[row][col] == board._opposite_color():
                corner_score -= 100.0
        return corner_score

    def _evaluate_edges(self, board: OthelloBoard) -> float:
        """Evaluate edge stability."""
        edge_score = 0
        # Check horizontal edges
        for col in range(1, BOARD_SIZE-1):
            if board.board[0][col] == self.color:
                edge_score += 10.0
            elif board.board[0][col] == board._opposite_color():
                edge_score -= 10.0
            if board.board[BOARD_SIZE-1][col] == self.color:
                edge_score += 10.0
            elif board.board[BOARD_SIZE-1][col] == board._opposite_color():
                edge_score -= 10.0
        # Check vertical edges
        for row in range(1, BOARD_SIZE-1):
            if board.board[row][0] == self.color:
                edge_score += 10.0
            elif board.board[row][0] == board._opposite_color():
                edge_score -= 10.0
            if board.board[row][BOARD_SIZE-1] == self.color:
                edge_score += 10.0
            elif board.board[row][BOARD_SIZE-1] == board._opposite_color():
                edge_score -= 10.0
        return edge_score

    def _evaluate_corner_danger(self, board: OthelloBoard) -> float:
        """Evaluate danger of corner captures."""
        danger_score = 0
        for row, col in self.corner_adjacent:
            if board.board[row][col] == self.color:
                danger_score -= 50.0  # Penalty for playing in corner-adjacent positions
            elif board.board[row][col] == board._opposite_color():
                danger_score += 50.0  # Bonus if opponent plays in corner-adjacent positions
        return danger_score 