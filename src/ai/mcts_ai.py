"""Monte Carlo Tree Search AI implementation."""

from typing import Optional, Tuple, Dict, List
import random
import math
from ..constants import BLACK, BOARD_SIZE
from ..board import OthelloBoard
from .base_ai import BaseAI

class MCTSNode:
    def __init__(self, board: OthelloBoard, parent: Optional['MCTSNode'] = None, move: Optional[Tuple[int, int]] = None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children: List[MCTSNode] = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = board.get_valid_moves()

class MCTSAI(BaseAI):
    def __init__(self, color: Tuple[int, int, int], iterations: int = 1000, exploration_weight: float = 1.4):
        super().__init__(color)
        self.iterations = iterations
        self.exploration_weight = exploration_weight
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
        """Get the best move using Monte Carlo Tree Search."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        root = MCTSNode(board)
        
        for _ in range(self.iterations):
            node = self._select(root)
            if not node.untried_moves and node.children:
                node = self._select(node)
            
            if node.untried_moves:
                node = self._expand(node)
            
            result = self._simulate(node)
            self._backpropagate(node, result)

        # Select the move with the highest win rate
        best_move = None
        best_win_rate = -1
        
        for child in root.children:
            win_rate = child.wins / child.visits
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                best_move = child.move

        return best_move

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select a node to expand using UCT (Upper Confidence Bound for Trees)."""
        while not node.untried_moves and node.children:
            node = self._select_uct(node)
        return node

    def _select_uct(self, node: MCTSNode) -> MCTSNode:
        """Select a child node using UCT formula."""
        log_parent_visits = math.log(node.visits)
        
        def uct(child: MCTSNode) -> float:
            if child.visits == 0:
                return float('inf')
            exploitation = child.wins / child.visits
            exploration = math.sqrt(log_parent_visits / child.visits)
            # Add position-based bonus for corner and edge moves
            position_bonus = 0
            if child.move:
                row, col = child.move
                position_bonus = self.position_weights[row][col] * 0.1
            return exploitation + self.exploration_weight * exploration + position_bonus

        return max(node.children, key=uct)

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand the tree by adding a new child node."""
        # Prioritize corner and edge moves during expansion
        corner_moves = []
        edge_moves = []
        other_moves = []
        
        for move in node.untried_moves:
            row, col = move
            if (row, col) in [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]:
                corner_moves.append(move)
            elif row == 0 or row == BOARD_SIZE-1 or col == 0 or col == BOARD_SIZE-1:
                edge_moves.append(move)
            else:
                other_moves.append(move)
        
        # Choose move based on priority
        if corner_moves:
            move = random.choice(corner_moves)
        elif edge_moves:
            move = random.choice(edge_moves)
        else:
            move = random.choice(other_moves)
            
        node.untried_moves.remove(move)
        
        new_board = node.board.clone()
        new_board.make_move(*move)
        
        child = MCTSNode(new_board, node, move)
        node.children.append(child)
        return child

    def _simulate(self, node: MCTSNode) -> float:
        """Simulate a game from the current state with improved move selection."""
        board = node.board.clone()
        
        while True:
            valid_moves = board.get_valid_moves()
            if not valid_moves:
                board.current_player = board._opposite_color()
                if not board.get_valid_moves():
                    # Game is over
                    black_score, white_score = board.get_score()
                    if self.color == BLACK:
                        return 1.0 if black_score > white_score else 0.0
                    else:
                        return 1.0 if white_score > black_score else 0.0
                continue
            
            # Use weighted random selection based on position importance
            move_weights = [self.position_weights[row][col] for row, col in valid_moves]
            total_weight = sum(move_weights)
            if total_weight > 0:
                probabilities = [w/total_weight for w in move_weights]
                move = random.choices(valid_moves, weights=probabilities, k=1)[0]
            else:
                move = random.choice(valid_moves)
                
            board.make_move(*move)

    def _backpropagate(self, node: MCTSNode, result: float):
        """Backpropagate the simulation result up the tree."""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def _evaluate_board(self, board: OthelloBoard) -> float:
        """Enhanced evaluation function for MCTS."""
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