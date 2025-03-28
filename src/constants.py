"""Game constants and configuration."""

# Window and board settings
WINDOW_SIZE = 800
BOARD_SIZE = 8
CELL_SIZE = WINDOW_SIZE // BOARD_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)

# AI Settings
MAX_DEPTH = 5  # Maximum depth for minimax search
AI_MOVE_DELAY = 1000  # Delay between AI moves in milliseconds 