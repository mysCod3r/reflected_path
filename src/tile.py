"""
Tile class representing a single interactive cell in the game grid.
"""
import pygame
# Import necessary constants from the config module
from src.config import (COLOR_TILE_EMPTY, TILE_SIZE, GRID_ORIGIN_X, GRID_ORIGIN_Y, TILE_COLORS,
                        TILE_STATE_EMPTY, COLOR_GRID_LINES, TILE_STATE_CORRECT,
                        TILE_STATE_INCORRECT, TILE_STATE_ORIGINAL_PATH)

class Tile:
    """
    Represents a single tile within the game grid.

    Attributes:
        row (int): The row index of the tile in the grid (0-based).
        col (int): The column index of the tile in the grid (0-based).
        state (int): The current state of the tile (e.g., EMPTY, CORRECT).
                     Uses constants defined in config.py.
        rect (pygame.Rect): The rectangle defining the tile's position and size
                            on the screen, used for drawing and collision detection.
    """
    def __init__(self, row, col):
        """
        Initializes a Tile object.

        Args:
            row (int): The row index for this tile.
            col (int): The column index for this tile.
        """
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("Tile row and column must be integers.")

        self.row = row
        self.col = col
        self.state = TILE_STATE_EMPTY # Tiles start as empty

        # Calculate the screen coordinates and size for this tile's rectangle
        # Using constants from config ensures consistency
        try:
            self.rect = pygame.Rect(
                GRID_ORIGIN_X + col * TILE_SIZE,
                GRID_ORIGIN_Y + row * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
        except NameError as e:
             print(f"ERROR: Missing config constant needed for Tile Rect calculation: {e}")
             # Handle this critical error, perhaps by setting rect to None or raising
             self.rect = None # Or raise a custom exception


    def draw(self, screen, draw_grid_overlay=True):
        """
        Draws the tile onto the provided screen surface.

        Args:
            screen (pygame.Surface): The surface to draw the tile onto.
            draw_grid_overlay (bool): If True, draws a thin border around the tile.
                                      Defaults to True.
        """
        if self.rect is None:
             print(f"Warning: Cannot draw Tile ({self.row},{self.col}) because its rect is None.")
             return

        # Determine the fill color based on the tile's current state
        # Use .get() with a default to gracefully handle potential invalid states
        tile_color = TILE_COLORS.get(self.state, COLOR_TILE_EMPTY)

        # Draw the filled rectangle representing the tile
        pygame.draw.rect(screen, tile_color, self.rect)

        # Optionally draw the grid line border over the tile
        if draw_grid_overlay:
            pygame.draw.rect(screen, COLOR_GRID_LINES, self.rect, 1) # '1' draws border

    def set_state(self, new_state):
        """
        Updates the state of the tile.

        Args:
            new_state (int): The new state constant (e.g., TILE_STATE_CORRECT)
                             from config.py.
        """
        # Optional: Validate the new state to prevent errors
        if new_state in TILE_COLORS: # Check if the state has a defined color
            self.state = new_state
        else:
            # Log a warning if an attempt is made to set an unknown state
            print(f"Warning: Attempted to set invalid state '{new_state}' for tile ({self.row},{self.col}). Reverting to EMPTY.")
            self.state = TILE_STATE_EMPTY

    def is_clicked(self, mouse_pos):
        """
        Checks if the given mouse coordinates fall within this tile's rectangle.

        Args:
            mouse_pos (tuple): A tuple containing the (x, y) coordinates of the mouse click.

        Returns:
            bool: True if the mouse position is inside the tile's rect, False otherwise.
        """
        if self.rect is None:
             return False # Cannot be clicked if rect doesn't exist
        try:
            return self.rect.collidepoint(mouse_pos)
        except TypeError:
             print(f"Warning: Invalid mouse_pos ({mouse_pos}) passed to is_clicked for Tile ({self.row},{self.col}).")
             return False


    def get_coords(self):
        """
        Returns the grid coordinates (row, column) of this tile.

        Returns:
            tuple: A tuple containing the (row, col) integer indices.
        """
        return self.row, self.col

    def __repr__(self):
        """
        Provides a developer-friendly string representation of the Tile object.
        Useful for debugging.
        """
        return f"Tile(row={self.row}, col={self.col}, state={self.state})"