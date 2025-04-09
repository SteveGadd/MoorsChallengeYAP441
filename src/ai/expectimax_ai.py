"""Expectimax AI implementation."""

from typing import Optional, Tuple, List
import random
from ..constants import MAX_DEPTH, BOARD_SIZE, BLACK
from ..board import OthelloBoard
from .base_ai import BaseAI

class ExpectimaxAI(BaseAI):
    def __init__(self, color: Tuple[int, int, int], opponent_randomness: float = 0.3):
        super().__init__(color)
        self.opponent_randomness = opponent_randomness  # Probability of opponent making a random move
        # Position weights for evaluation
        self.position_weights = self._initialize_position_weights()

    def _initialize_position_weights(self) -> List[List[float]]:
        """Initialize position weights for the board."""
        weights = [[0.0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Corner positions (highest value)
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        for row, col in corners:
            weights[row][col] = 100.0
            
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
        """Get the best move using expectimax."""
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
                # Opponent makes a weighted random move based on position importance
                move_weights = [self.position_weights[row][col] for row, col in valid_moves]
                total_weight = sum(move_weights)
                if total_weight > 0:
                    probabilities = [w/total_weight for w in move_weights]
                    move = random.choices(valid_moves, weights=probabilities, k=1)[0]
                else:
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
            
        # Stability evaluation
        stability_score = self._calculate_stability(board)
            
        return base_score + position_score + mobility_score + stability_score

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