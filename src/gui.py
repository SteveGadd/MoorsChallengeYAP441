"""Graphical user interface for the Othello game."""

import pygame
from typing import Optional, Tuple, List
from .constants import (
    WINDOW_SIZE, BOARD_SIZE, CELL_SIZE,
    BLACK, WHITE, GREEN, DARK_GREEN
)
from .board import OthelloBoard

class OthelloGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Othello')
        # Initialize font
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.ai_names = [
            "Minimax with Alpha-Beta Pruning",
            "Expectimax",
            "Monte Carlo Tree Search"
        ]
        self.selected_ai = None

    def show_algorithm_selection_menu(self) -> int:
        """Show the AI selection menu and return the selected algorithm index."""
        menu_active = True
        while menu_active:
            self.screen.fill(GREEN)
            
            # Draw title
            title = self.font.render("Select AI Opponent", True, WHITE)
            title_rect = title.get_rect(center=(WINDOW_SIZE//2, 100))
            self.screen.blit(title, title_rect)
            
            # Draw options
            for i, name in enumerate(self.ai_names):
                y = 200 + i * 60
                color = WHITE if self.selected_ai == i else (200, 200, 200)
                text = self.font.render(f"{i+1}. {name}", True, color)
                text_rect = text.get_rect(center=(WINDOW_SIZE//2, y))
                self.screen.blit(text, text_rect)
            
            # Draw instructions
            instructions = self.small_font.render("Click on an option or press 1-3 to select", True, WHITE)
            instructions_rect = instructions.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE - 100))
            self.screen.blit(instructions, instructions_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return -1
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for i in range(3):
                        option_y = 200 + i * 60
                        if abs(y - option_y) < 30 and abs(x - WINDOW_SIZE//2) < 200:
                            self.selected_ai = i
                            menu_active = False
                            break
                
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        self.selected_ai = int(event.unicode) - 1
                        menu_active = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return -1
        
        return self.selected_ai

    def draw_board(self, board: OthelloBoard, ai_name: str):
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
                elif (row, col) in valid_moves and board.current_player == BLACK:
                    pygame.draw.circle(self.screen, DARK_GREEN,
                                     center, CELL_SIZE // 8)

        # Draw current player's turn and AI info
        black_score, white_score = board.get_score()
        self.draw_status(board.current_player, black_score, white_score, ai_name)

        # Update the display
        pygame.display.flip()

    def draw_status(self, current_player: Tuple[int, int, int], black_score: int, white_score: int, ai_name: str):
        """Draw the current player's turn, scores, and AI info."""
        # Create background rectangle for text
        pygame.draw.rect(self.screen, (0, 100, 0), (0, WINDOW_SIZE - 40, WINDOW_SIZE, 40))
        
        # Draw scores
        score_text = f"Black: {black_score} - White: {white_score}"
        score_surface = self.font.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (10, WINDOW_SIZE - 35))

        # Draw current player
        turn_text = "Black's turn" if current_player == BLACK else "White's turn"
        turn_surface = self.font.render(turn_text, True, WHITE)
        self.screen.blit(turn_surface, (WINDOW_SIZE//2 - 50, WINDOW_SIZE - 35))

        # Draw AI name
        ai_surface = self.small_font.render(f"AI: {ai_name}", True, WHITE)
        self.screen.blit(ai_surface, (WINDOW_SIZE - 200, WINDOW_SIZE - 35))

    def get_clicked_cell(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to board coordinates."""
        x, y = pos
        row = y // CELL_SIZE
        col = x // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None

    def show_game_over_screen(self, black_score: int, white_score: int):
        """Show the game over screen with final scores."""
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        
        # Draw game over text
        game_over = self.font.render("Game Over!", True, WHITE)
        game_over_rect = game_over.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50))
        
        # Draw final scores
        score_text = f"Black: {black_score} - White: {white_score}"
        score_surface = self.font.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
        
        # Draw winner
        if black_score > white_score:
            winner = "Black wins!"
        elif white_score > black_score:
            winner = "White wins!"
        else:
            winner = "It's a tie!"
        winner_surface = self.font.render(winner, True, WHITE)
        winner_rect = winner_surface.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 50))
        
        # Draw instructions
        instructions = self.small_font.render("Press ESC to exit", True, WHITE)
        instructions_rect = instructions.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 100))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(game_over, game_over_rect)
        self.screen.blit(score_surface, score_rect)
        self.screen.blit(winner_surface, winner_rect)
        self.screen.blit(instructions, instructions_rect)
        
        pygame.display.flip()
        
        # Wait for ESC key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    waiting = False
                    exit(1)