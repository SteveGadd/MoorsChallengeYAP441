"""Othello board implementation with game logic."""

from typing import List, Tuple, Optional
from .constants import BOARD_SIZE, BLACK, WHITE

class OthelloBoard:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = BLACK  # Black goes first
        self.initialize_board()

    def initialize_board(self):
        """Place the initial four pieces."""
        center = BOARD_SIZE // 2
        self.board[center-1][center-1] = WHITE
        self.board[center-1][center] = BLACK
        self.board[center][center-1] = BLACK
        self.board[center][center] = WHITE

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid at the given position."""
        if self.board[row][col] is not None:
            return False

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for dr, dc in directions:
            if self._would_flip(row, col, dr, dc):
                return True
        return False

    def _would_flip(self, row: int, col: int, dr: int, dc: int) -> bool:
        """Check if any pieces would be flipped in a given direction."""
        r, c = row + dr, col + dc
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return False
        if self.board[r][c] != self._opposite_color():
            return False

        r, c = r + dr, c + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if self.board[r][c] is None:
                return False
            if self.board[r][c] == self.current_player:
                return True
            r, c = r + dr, c + dc
        return False

    def make_move(self, row: int, col: int) -> bool:
        """Make a move at the given position."""
        if not self.is_valid_move(row, col):
            return False

        self.board[row][col] = self.current_player
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for dr, dc in directions:
            self._flip_pieces(row, col, dr, dc)

        self.current_player = self._opposite_color()
        return True

    def _flip_pieces(self, row: int, col: int, dr: int, dc: int):
        """Flip pieces in a given direction."""
        if not self._would_flip(row, col, dr, dc):
            return

        r, c = row + dr, col + dc
        while self.board[r][c] == self._opposite_color():
            self.board[r][c] = self.current_player
            r, c = r + dr, c + dc

    def _opposite_color(self) -> Tuple[int, int, int]:
        """Get the opposite color of the current player."""
        return WHITE if self.current_player == BLACK else BLACK

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves for the current player."""
        valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col):
                    valid_moves.append((row, col))
        return valid_moves

    def get_score(self) -> Tuple[int, int]:
        """Get the current score (black_count, white_count)."""
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)
        return black_count, white_count
    
    def clone(self) -> 'OthelloBoard':
        """Create a deep copy of the board for AI simulation."""
        new_board = OthelloBoard()
        new_board.board = [row[:] for row in self.board]
        new_board.current_player = self.current_player
        return new_board

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        # Check if the current player has valid moves
        if self.get_valid_moves():
            return False
        
        # Temporarily switch to the opponent and check their valid moves
        original_player = self.current_player
        self.current_player = self._opposite_color()
        opponent_has_moves = bool(self.get_valid_moves())
        self.current_player = original_player  # Restore the original player

        # If neither player has valid moves, the game is over
        return not opponent_has_moves