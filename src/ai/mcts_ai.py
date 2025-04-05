"""Monte Carlo Tree Search AI implementation."""

from typing import Optional, Tuple, Dict, List
import random
import math
from ..constants import BLACK
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
            return exploitation + self.exploration_weight * exploration

        return max(node.children, key=uct)

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand the tree by adding a new child node."""
        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)
        
        new_board = node.board.clone()
        new_board.make_move(*move)
        
        child = MCTSNode(new_board, node, move)
        node.children.append(child)
        return child

    def _simulate(self, node: MCTSNode) -> float:
        """Simulate a random game from the current state."""
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
            
            # Make a random move
            move = random.choice(valid_moves)
            board.make_move(*move)

    def _backpropagate(self, node: MCTSNode, result: float):
        """Backpropagate the simulation result up the tree."""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def _evaluate_board(self, board: OthelloBoard) -> float:
        """Evaluation function used during simulation."""
        # This is a simplified evaluation since MCTS relies more on simulations
        black_score, white_score = board.get_score()
        if self.color == BLACK:
            return black_score - white_score
        else:
            return white_score - black_score 