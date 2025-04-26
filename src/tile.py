"""
Tile class representing a single interactive cell in the game grid.
Handles tile state, drawing, and color transition animation.
"""
import pygame
from src.config import *

class Tile:
    """
    Represents a single tile within the game grid.

    Attributes:
        row (int): The row index of the tile (0-based).
        col (int): The column index of the tile (0-based).
        state (int): The logical state of the tile (e.g., EMPTY, CORRECT).
        rect (pygame.Rect): The screen rectangle for drawing and collision.
        current_color (pygame.Color): The color currently displayed, used for animation.
        target_color (pygame.Color): The final color the tile should animate towards.
        is_animating (bool): Flag indicating if a color transition is active.
        animation_start_time (int): Timestamp when the current animation started.
        animation_start_color (pygame.Color): The color the tile had when animation started.
    """
    def __init__(self, row, col):
        """Initializes a Tile object."""
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("Tile row and column must be integers.")

        self.row = row
        self.col = col
        self.state = TILE_STATE_EMPTY       # Logical state used by game logic
        self._target_state = TILE_STATE_EMPTY # Internal state for animation target

        # Initialize colors using pygame.Color for lerp compatibility
        initial_color = pygame.Color(TILE_COLORS.get(self.state, COLOR_TILE_EMPTY))
        self.current_color = initial_color
        self.target_color = initial_color
        self.animation_start_color = initial_color

        # Animation state flags
        self.is_animating = False
        self.animation_start_time = 0

        # Calculate screen rectangle
        try:
            self.rect = pygame.Rect(
                GRID_ORIGIN_X + col * TILE_SIZE,
                GRID_ORIGIN_Y + row * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
        except NameError as e:
            print(f"ERROR: Missing config constant for Tile Rect calculation: {e}")
            self.rect = None # Indicate rect couldn't be created

    def set_state(self, new_state, force_immediate=False):
        """
        Sets the logical state and initiates/updates the color transition animation.

        Args:
            new_state (int): The target state constant from config.py.
            force_immediate (bool): If True, skips animation and sets color instantly.
        """
        if new_state not in TILE_COLORS:
            print(f"Warning: Invalid state '{new_state}' for tile ({self.row},{self.col}). Using EMPTY.")
            new_state = TILE_STATE_EMPTY

        # Update the logical state immediately for game logic checks
        self.state = new_state
        self._target_state = new_state # Keep track of where we're animating to

        new_target_color = pygame.Color(TILE_COLORS[new_state])

        # --- Animation Handling ---
        if force_immediate or TILE_COLOR_TRANSITION_DURATION <= 0:
            # Set color immediately if forced, duration is zero/negative, or already at target
            self.current_color = new_target_color
            self.target_color = new_target_color
            self.is_animating = False
        elif self.current_color != new_target_color:
            # Only start a new animation if the target color is different
            self.target_color = new_target_color
            # Use the *current* visual color as the start point for the new animation
            self.animation_start_color = self.current_color
            self.animation_start_time = pygame.time.get_ticks()
            self.is_animating = True
        # If self.current_color == new_target_color, do nothing (already there or animating there)


    def update_animation(self, current_ticks):
        """
        Updates the tile's current_color based on the animation progress.
        Should be called once per frame.

        Args:
            current_ticks (int): The current time in milliseconds (from pygame.time.get_ticks()).
        """
        if not self.is_animating:
            return # Nothing to update if not animating

        elapsed_time = current_ticks - self.animation_start_time
        duration = TILE_COLOR_TRANSITION_DURATION

        if elapsed_time >= duration:
            # Animation finished
            self.current_color = self.target_color
            self.is_animating = False
        elif elapsed_time < 0:
             # Edge case: if timer wrapped around or time went backwards somehow
             self.current_color = self.animation_start_color # Reset to start or end? End is safer.
             # self.current_color = self.target_color
             # self.is_animating = False # Optionally stop animation
             print(f"Warning: Negative elapsed time ({elapsed_time}) in tile animation.")
        else:
            # Animation in progress - calculate interpolation factor (progress)
            # Clamp progress value strictly between 0.0 and 1.0 to avoid ValueError in lerp
            progress = max(0.0, min(1.0, elapsed_time / duration))

            try:
                # Perform linear interpolation between start and target colors
                self.current_color = self.animation_start_color.lerp(self.target_color, progress)
            except ValueError as e:
                 # This should theoretically not happen with clamping, but catch just in case
                 print(f"ERROR during color lerp for Tile({self.row},{self.col}): {e}")
                 print(f"  Start: {self.animation_start_color}, Target: {self.target_color}, Progress: {progress}")
                 self.current_color = self.target_color # Jump to target on error
                 self.is_animating = False


    def draw(self, screen, draw_grid_overlay=True):
        """
        Draws the tile onto the provided screen surface using its current animated color.

        Args:
            screen (pygame.Surface): The surface to draw the tile onto.
            draw_grid_overlay (bool): If True, draws a thin border around the tile.
        """
        if self.rect is None:
            print(f"Warning: Cannot draw Tile ({self.row},{self.col}), rect is None.")
            return

        # Draw the tile background using the current animated color
        pygame.draw.rect(screen, self.current_color, self.rect)

        # Draw the grid line overlay if requested
        if draw_grid_overlay:
            pygame.draw.rect(screen, COLOR_GRID_LINES, self.rect, 1)

    def is_clicked(self, mouse_pos):
        """Checks if the mouse coordinates are within this tile's rectangle."""
        if self.rect is None: return False
        try:
            return self.rect.collidepoint(mouse_pos)
        except TypeError:
            # Handle cases where mouse_pos might not be a valid coordinate pair
            print(f"Warning: Invalid mouse_pos format ({mouse_pos}) for is_clicked.")
            return False

    def get_coords(self):
        """Returns the grid coordinates (row, column) of this tile."""
        return self.row, self.col

    def __repr__(self):
        """Returns a developer-friendly string representation of the Tile."""
        state_repr = self.state # Or map integer state to string if needed
        return f"Tile(row={self.row}, col={self.col}, state={state_repr}, animating={self.is_animating})"