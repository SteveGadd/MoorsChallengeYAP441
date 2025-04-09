"""Main entry point for the Othello game."""

import pygame
import sys
import time
from src.constants import BLACK, WHITE, AI_MOVE_DELAY
from src.board import OthelloBoard
from src.gui import OthelloGUI
from src.ai.minimax_ai import MinimaxAI
from src.ai.expectimax_ai import ExpectimaxAI
from src.ai.mcts_ai import MCTSAI

def create_ai(choice: int) -> object:
    """Create the selected AI opponent."""
    if choice == 0:
        return MinimaxAI(WHITE), "Minimax"
    elif choice == 1:
        return ExpectimaxAI(WHITE), "Expectimax"
    else:
        return MCTSAI(WHITE), "MCTS"

def main():
    # Initialize Pygame
    pygame.init()
    
    # Create game objects
    board = OthelloBoard()
    gui = OthelloGUI()
    
    # Show AI selection menu
    ai_choice = gui.show_algorithm_selection_menu()
    if ai_choice == -1:  # User closed the window
        pygame.quit()
        sys.exit()
    
    # Create AI opponent
    ai, ai_name = create_ai(ai_choice)
    
    clock = pygame.time.Clock()
    game_over = False
    last_move_time = 0  # Track when the last move was made

    while True:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Human's turn (Black)
                if board.current_player == BLACK:
                    clicked_cell = gui.get_clicked_cell(event.pos)
                    if clicked_cell and board.make_move(*clicked_cell):
                        last_move_time = current_time
                        # After human moves, check if game is over
                        if not board.get_valid_moves():
                            board.current_player = board._opposite_color()
                            if not board.get_valid_moves():
                                game_over = True

        # AI's turn (White)
        if (board.current_player == WHITE and not game_over and 
            current_time - last_move_time >= AI_MOVE_DELAY):
            ai_move = ai.get_move(board)
            if ai_move:
                board.make_move(*ai_move)
                last_move_time = current_time
                # After AI moves, check if game is over
                if not board.get_valid_moves():
                    board.current_player = board._opposite_color()
                    if not board.get_valid_moves():
                        game_over = True
            else:
                # AI has no valid moves
                board.current_player = board._opposite_color()
                last_move_time = current_time
                if not board.get_valid_moves():
                    game_over = True

        # Draw the current state
        gui.draw_board(board, ai_name)
        
        # Display game over
        if game_over:
            black_score, white_score = board.get_score()
            gui.show_game_over_screen(black_score, white_score)

        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()