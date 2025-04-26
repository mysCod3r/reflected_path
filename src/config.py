# src/config.py
"""
Game Configuration and Constants for Reflected Path
"""
import pygame

# Initialize font module early and handle potential errors
try:
    pygame.font.init()
    _font_module_available = True
except Exception as e:
    print(f"CRITICAL ERROR: Could not initialize pygame.font: {e}")
    print("UI text rendering will not work.")
    _font_module_available = False

# --- Screen and Display ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Yansıyan Yol"
FPS = 60

# --- Colors (RGB Tuples) ---
COLOR_BACKGROUND = (20, 30, 40)        # Dark bluish-grey
COLOR_GRID_LINES = (50, 60, 70)        # Lighter grey for grid lines
COLOR_SYMMETRY_LINE = (255, 255, 255)  # White for the central line

COLOR_TILE_EMPTY = (25, 35, 45)        # Slightly different from background
COLOR_TILE_ORIGINAL_PATH = (100, 180, 255) # Light Blue for the path to memorize
# COLOR_TILE_PLAYER_DRAWN = (255, 255, 0)   # Yellow - Decided not to use directly, use Correct/Incorrect instead
COLOR_TILE_CORRECT = (0, 200, 100)         # Green for correctly reflected tiles
COLOR_TILE_INCORRECT = (220, 50, 50)       # Red for incorrectly placed tiles

COLOR_UI_TEXT = (230, 230, 230)         # Light grey/white for UI text
COLOR_MESSAGE_TEXT = (255, 220, 180)    # A distinct color for messages (Game Over, etc.)
COLOR_MESSAGE_BG = (0, 0, 0, 180)       # Semi-transparent black background for messages

# --- Grid Layout ---
TILE_SIZE = 40          # Pixel dimension of each square tile
GRID_WIDTH_TILES = 16   # Number of tiles horizontally
GRID_HEIGHT_TILES = 12  # Number of tiles vertically

# Calculate derived grid dimensions in pixels
GRID_WIDTH_PX = GRID_WIDTH_TILES * TILE_SIZE
GRID_HEIGHT_PX = GRID_HEIGHT_TILES * TILE_SIZE

# Calculate top-left corner for centering the grid
GRID_ORIGIN_X = (SCREEN_WIDTH - GRID_WIDTH_PX) // 2
GRID_ORIGIN_Y = 70  # Increased top margin for better UI spacing

# --- Symmetry Line ---
# Calculate based on tile index to ensure alignment between tiles
SYMMETRY_LINE_TILE_INDEX = GRID_WIDTH_TILES // 2
SYMMETRY_LINE_X = GRID_ORIGIN_X + SYMMETRY_LINE_TILE_INDEX * TILE_SIZE
SYMMETRY_LINE_WIDTH = 3 # Make it slightly thicker

# --- Tile States ---
# Using integers can be slightly more performant for lookups/comparisons
TILE_STATE_EMPTY = 0
TILE_STATE_ORIGINAL_PATH = 1
TILE_STATE_CORRECT = 3
TILE_STATE_INCORRECT = 4

# Map tile states to their corresponding colors for drawing
TILE_COLORS = {
    TILE_STATE_EMPTY: COLOR_TILE_EMPTY,
    TILE_STATE_ORIGINAL_PATH: COLOR_TILE_ORIGINAL_PATH,
    TILE_STATE_CORRECT: COLOR_TILE_CORRECT,
    TILE_STATE_INCORRECT: COLOR_TILE_INCORRECT,
}

# --- Game States ---
STATE_SHOWING_PATH = "SHOWING_PATH" # When the path is shown to the player
STATE_PLAYER_DRAWING = "PLAYER_DRAWING" # When the player is drawing
STATE_LEVEL_TRANSITION = "LEVEL_TRANSITION" # Between levels
STATE_GAME_OVER_TIME = "GAME_OVER_TIME" # When time runs out
STATE_GAME_OVER_INK = "GAME_OVER_INK" # When ink runs out
STATE_GAME_COMPLETE = "GAME_COMPLETE" # When all levels are done
STATE_GAME_OVER_MISTAKES = "GAME_OVER_MISTAKES" # When too many mistakes are made

# --- Gameplay Tuning ---
PATH_SHOW_DURATION = 1800       # ms (Slightly less than 2s)
DEFAULT_LEVEL_TIME_LIMIT = 25000 # ms (25 seconds)
DEFAULT_LEVEL_INK_LIMIT = 25     # Max number of tiles player can draw
LEVEL_TRANSITION_DELAY = 1500   # ms pause between levels or after messages
TIMER_WARNING_THRESHOLD_MS = 10000 # 10 seconds before time runs out
TIMER_WARNING_REPEAT_DELAY_MS = 1000 # ms between warnings
DEFAULT_MISTAKE_LIMIT = 5 

# --- UI Settings ---
UI_FONT_SIZE = 26
UI_MARGIN_TOP = 20               # Top margin for UI elements
UI_MARGIN_LEFT = GRID_ORIGIN_X   # Align UI with grid start
UI_INFO_SPACING = 220            # Increased horizontal space between Time and Ink display

# --- Sound Effect Keys ---
SOUND_CLICK = 'click'
SOUND_CORRECT = 'correct'
SOUND_INCORRECT = 'incorrect'
SOUND_LEVEL_COMPLETE = 'level_complete'
SOUND_GAME_OVER = 'game_over'
SOUND_PATH_SHOW = 'path_show'
SOUND_TIMER_LOW = 'timer_warning'

# --- Animation Settings ---
TILE_COLOR_TRANSITION_DURATION = 250 # ms
PATH_REVEAL_DELAY_PER_TILE = 75 # ms

# --- Font Loading ---
# Attempt to load the default font, provide fallbacks
UI_FONT = None
if _font_module_available:
    try:
        UI_FONT = pygame.font.Font(None, UI_FONT_SIZE)
    except pygame.error as e: # Catch Pygame specific errors
        print(f"Warning: Pygame error loading default font: {e}. Using fallback SysFont.")
        try:
            UI_FONT = pygame.font.SysFont('consolas', UI_FONT_SIZE, bold=True)
        except pygame.error:
             print(f"Warning: Consolas not found. Using Arial.")
             try:
                 UI_FONT = pygame.font.SysFont('arial', UI_FONT_SIZE) # Basic fallback
             except pygame.error as e_sys:
                  print(f"CRITICAL ERROR: Could not load any system font: {e_sys}")
    except FileNotFoundError:
        print(f"Warning: Custom font file not found (if specified). Using default/fallback.")
        UI_FONT = pygame.font.Font(None, UI_FONT_SIZE) # Fallback to default None
    except Exception as e:
         print(f"CRITICAL ERROR: Unexpected error loading font: {e}")

if UI_FONT is None and _font_module_available:
    print("Warning: UI_FONT is None, attempting final fallback to basic SysFont.")
    try:
        UI_FONT = pygame.font.SysFont(pygame.font.get_default_font(), UI_FONT_SIZE)
    except Exception as e:
        print(f"CRITICAL ERROR: Final font fallback failed: {e}")

FONT_AVAILABLE = UI_FONT is not None