"""Graphical user interface for the Othello game."""

import pygame
from typing import Optional, Tuple
from .constants import (
    WINDOW_SIZE, BOARD_SIZE, CELL_SIZE,
    BLACK, WHITE, GREEN, DARK_GREEN
)
from .board import OthelloBoard

class OthelloGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE+40))
        pygame.display.set_caption('Othello')
        # Initialize font
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)

    def draw_board(self, board: OthelloBoard):
        """Draw the game board with pieces and valid moves."""
        self.screen.fill(GREEN)
        
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(self.screen, BLACK, (i * CELL_SIZE, 0),
                           (i * CELL_SIZE, WINDOW_SIZE), 2)
            pygame.draw.line(self.screen, BLACK, (0, i * CELL_SIZE),
                           (WINDOW_SIZE, i * CELL_SIZE), 2)

        # Draw pieces and valid moves
        valid_moves = board.get_valid_moves()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                center = (col * CELL_SIZE + CELL_SIZE // 2,
                         row * CELL_SIZE + CELL_SIZE // 2)
                
                # Draw pieces
                if board.board[row][col] is not None:
                    pygame.draw.circle(self.screen, board.board[row][col],
                                     center, CELL_SIZE // 2 - 4)
                
                # Draw valid move indicators
                elif (row, col) in valid_moves:
                    pygame.draw.circle(self.screen, DARK_GREEN,
                                     center, CELL_SIZE // 8)

        # Draw current player's turn
        black_score, white_score = board.get_score()
        self.draw_status(board.current_player, black_score, white_score)

        # Update the display
        pygame.display.flip()

    def draw_status(self, current_player: Tuple[int, int, int], black_score: int, white_score: int):
        """Draw the current player's turn and scores."""
        # Create background rectangle for text
        pygame.draw.rect(self.screen, (0, 100, 0), (0, WINDOW_SIZE, WINDOW_SIZE, 40))
        
        # Draw scores
        score_text = f"Black: {black_score} - White: {white_score}"
        score_surface = self.font.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (10, WINDOW_SIZE + 5))

        # Draw current player
        turn_text = "Black's turn" if current_player == BLACK else "White's turn"
        turn_surface = self.font.render(turn_text, True, WHITE)
        self.screen.blit(turn_surface, (WINDOW_SIZE - 150, WINDOW_SIZE + 5))

    def get_clicked_cell(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to board coordinates."""
        x, y = pos
        row = y // CELL_SIZE
        col = x // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None 