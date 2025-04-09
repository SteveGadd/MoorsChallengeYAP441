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

    def _initialize_position_weights(self) -> List[List[float]]:
        """Initialize position weights for the board."""
        weights = [[0.0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Corner positions (highest value)
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        for row, col in corners:
            weights[row][col] = 8.0
            
        # Edge positions (high value)
        for i in range(BOARD_SIZE):
            if i not in [0, BOARD_SIZE-1]:
                weights[0][i] = 1.0  # Top edge
                weights[BOARD_SIZE-1][i] = 1.0  # Bottom edge
                weights[i][0] = 1.0  # Left edge
                weights[i][BOARD_SIZE-1] = 1.0  # Right edge
                
        # Inner positions (lower value)
        for i in range(1, BOARD_SIZE-1):
            for j in range(1, BOARD_SIZE-1):
                weights[i][j] = 0.5
                
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
        # Basic score difference
        black_score, white_score = board.get_score()
        base_score = black_score - white_score if self.color == BLACK else white_score - black_score
        
        # Position-based evaluation
        position_score = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board.board[row][col] == self.color:
                    position_score += self.position_weights[row][col]
                elif board.board[row][col] == board._opposite_color():
                    position_score -= self.position_weights[row][col]
        
        # Mobility evaluation
        mobility = len(board.get_valid_moves())
        if board.current_player == self.color:
            mobility_score = mobility * 0.5
        else:
            mobility_score = -mobility * 0.5
            
        return base_score + position_score + mobility_score 