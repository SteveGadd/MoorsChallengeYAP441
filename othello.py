import pygame
import sys
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 8
CELL_SIZE = WINDOW_SIZE // BOARD_SIZE
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)

# Initialize the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Othello')

class OthelloBoard:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = BLACK  # Black goes first
        self.initialize_board()

    def initialize_board(self):
        # Place the initial four pieces
        center = BOARD_SIZE // 2
        self.board[center-1][center-1] = WHITE
        self.board[center-1][center] = BLACK
        self.board[center][center-1] = BLACK
        self.board[center][center] = WHITE

    def is_valid_move(self, row: int, col: int) -> bool:
        if self.board[row][col] is not None:
            return False

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for dr, dc in directions:
            if self._would_flip(row, col, dr, dc):
                return True
        return False

    def _would_flip(self, row: int, col: int, dr: int, dc: int) -> bool:
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
        if not self._would_flip(row, col, dr, dc):
            return

        r, c = row + dr, col + dc
        while self.board[r][c] == self._opposite_color():
            self.board[r][c] = self.current_player
            r, c = r + dr, c + dc

    def _opposite_color(self) -> Tuple[int, int, int]:
        return WHITE if self.current_player == BLACK else BLACK

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col):
                    valid_moves.append((row, col))
        return valid_moves

    def get_score(self) -> Tuple[int, int]:
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)
        return black_count, white_count

def draw_board(screen: pygame.Surface, board: OthelloBoard):
    screen.fill(GREEN)
    
    # Draw grid lines
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0),
                        (i * CELL_SIZE, WINDOW_SIZE), 2)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE),
                        (WINDOW_SIZE, i * CELL_SIZE), 2)

    # Draw pieces and valid moves
    valid_moves = board.get_valid_moves()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            center = (col * CELL_SIZE + CELL_SIZE // 2,
                     row * CELL_SIZE + CELL_SIZE // 2)
            
            # Draw pieces
            if board.board[row][col] is not None:
                pygame.draw.circle(screen, board.board[row][col],
                                 center, CELL_SIZE // 2 - 4)
            
            # Draw valid move indicators
            elif (row, col) in valid_moves:
                pygame.draw.circle(screen, DARK_GREEN,
                                 center, CELL_SIZE // 8)

def main():
    board = OthelloBoard()
    clock = pygame.time.Clock()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    board.make_move(row, col)

        # Check if game is over
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            board.current_player = board._opposite_color()
            if not board.get_valid_moves():
                game_over = True

        # Draw everything
        draw_board(screen, board)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 