"""
Main Game class containing the game logic, state management, and main loop.
"""
import pygame
import sys
# Import everything from config for easy access to constants
from src.config import *
# Import the Tile class and level data
from src.tile import Tile
from src.level_data import LEVELS
import os

class Game:
    """
    Manages the overall game state, updates, input handling, and rendering.
    """
    def __init__(self):
        """Initialize Pygame, screen, clock, font, and game variables."""
        pygame.init() # Initialize all Pygame modules

        # --- Mixer Initialization (Sound) ---
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("Pygame mixer initialized successfully.")
            self.sound_enabled = True
            # Sounds will be loaded *after* display setup if needed, or here is fine
            # self._load_sounds()
        except pygame.error as e:
            print(f"Warning: Pygame mixer could not be initialized: {e}")
            print("Sounds will be disabled.")
            self.sound_enabled = False
            self.sounds = {} # Still create dict but it will be empty

        # --- Display Setup (MUST be done BEFORE loading images) ---
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(WINDOW_TITLE)
            print("Display mode set successfully.")
        except pygame.error as e:
            print(f"CRITICAL ERROR: Could not set display mode: {e}")
            # Exit if we cannot create a screen
            pygame.quit()
            sys.exit("Failed to initialize display.")
        # ------------------------------------------------------------

        # --- Font (Can be loaded after display is set) ---
        self.font = UI_FONT
        if not FONT_AVAILABLE:
            print("CRITICAL: Font not available, UI text cannot be rendered.")

        # --- Clock ---
        self.clock = pygame.time.Clock()

        # --- Load Sounds (Now that display is set, safer place) ---
        if self.sound_enabled:
            self._load_sounds() # Load sounds here
        else:
            self.sounds = {} # Ensure it exists even if disabled


        # --- Load Background Image (Load AFTER display is set) ---
        self.background_image = None
        background_path = "assets/images/background.png" # Adjust filename
        try:
            if os.path.exists(background_path):
                # Load the image
                loaded_image = pygame.image.load(background_path)
                # Use convert_alpha() if PNG has transparency, otherwise convert()
                if background_path.lower().endswith(".png"):
                     self.background_image = loaded_image.convert_alpha()
                else:
                     self.background_image = loaded_image.convert()

                # Scale if necessary
                if self.background_image.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                    print(f"Warning: Background size mismatch. Scaling {background_path}...")
                    self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"Loaded background image: {background_path}")
            else:
                print(f"Warning: Background image not found at {background_path}. Using solid color.")
        except pygame.error as e:
            print(f"Error loading background image {background_path}: {e}")
        # ------------------------------------------------------------

        # --- Game State & Level Data ---
        self.running = True
        self.game_state = STATE_SHOWING_PATH # Initial state
        self.current_level_index = 0
        self.grid = self._create_grid()
        self.correct_reflection_coords = set()
        self.player_drawn_tiles = set()
        self.remaining_ink = DEFAULT_LEVEL_INK_LIMIT
        self.remaining_time_ms = DEFAULT_LEVEL_TIME_LIMIT
        self.path_show_start_time = 0
        self.level_timer_start = 0
        self.transition_timer_start = 0
        self.current_path_coords_to_reveal = []
        self.last_reveal_time = 0
        self.reveal_index = 0

        # --- Initial Level Setup ---
        if not self._setup_level():
            print("ERROR: Failed to setup initial level. Exiting.")
            self.running = False
    
    def _load_sounds(self):
        """Loads sound effects into a dictionary."""
        # ... (the _load_sounds code from the previous step) ...
        self.sounds = {}
        sound_files = {
            SOUND_CLICK: 'assets/sounds/click.wav',
            SOUND_CORRECT: 'assets/sounds/correct.wav',
            SOUND_INCORRECT: 'assets/sounds/incorrect.wav',
            SOUND_LEVEL_COMPLETE: 'assets/sounds/level_complete.wav',
            SOUND_GAME_OVER: 'assets/sounds/game_over.wav',
            SOUND_PATH_SHOW: 'assets/sounds/path_show.wav',
        }
        print("Loading sounds...")
        loaded_count = 0
        for name_key, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name_key] = pygame.mixer.Sound(path)
                    loaded_count += 1
                else:
                    print(f"  Warning: Sound file not found for '{name_key}': {path}")
                    self.sounds[name_key] = None
            except pygame.error as e:
                print(f"  Error loading sound for '{name_key}' ({path}): {e}")
                self.sounds[name_key] = None
        print(f"Finished loading sounds. {loaded_count}/{len(sound_files)} loaded.")


    def _play_sound(self, name):
            """Plays a loaded sound effect if sound is enabled and file exists."""
            if self.sound_enabled and name in self.sounds and self.sounds[name] is not None:
                try:
                    self.sounds[name].play()
                except pygame.error as e:
                    print(f"Error playing sound '{name}': {e}")

    def _create_grid(self):
        """Creates and returns the grid as a 2D list of Tile objects."""
        grid = []
        for r in range(GRID_HEIGHT_TILES):
            row_tiles = [Tile(r, c) for c in range(GRID_WIDTH_TILES)]
            grid.append(row_tiles)
        return grid

    def _get_reflected_coords(self, row, col):
        """Calculates the reflected coordinates across the vertical symmetry line."""
        # Ensure the original coordinate is valid and on the left side
        if not (0 <= row < GRID_HEIGHT_TILES and 0 <= col < SYMMETRY_LINE_TILE_INDEX):
            return None # Invalid input for reflection

        distance_from_line = SYMMETRY_LINE_TILE_INDEX - col - 1 # 0-based index adjustment
        reflected_col = SYMMETRY_LINE_TILE_INDEX + distance_from_line

        # Check if the reflected column is within the grid bounds
        if 0 <= reflected_col < GRID_WIDTH_TILES:
            return row, reflected_col
        else:
            return None # Reflection falls outside the grid

    def _setup_level(self):
        """
        Sets up the game state for the current level index.
        Clears the grid, loads path data, calculates reflection, resets timers/ink.

        Returns:
            bool: True if the level was set up successfully, False otherwise
                  (e.g., no more levels).
        """
        # --- Check if levels exist ---
        if not (0 <= self.current_level_index < len(LEVELS)):
            self.game_state = STATE_GAME_COMPLETE
            print("All levels completed!")
            return False # Signal no more levels to setup

        # --- Reset level state ---
        self.correct_reflection_coords.clear()
        self.player_drawn_tiles.clear()
        self.remaining_ink = DEFAULT_LEVEL_INK_LIMIT # Reset ink
        self.remaining_time_ms = DEFAULT_LEVEL_TIME_LIMIT # Reset timer

        # Clear Grid Tile States - Force immediate color change
        for r in range(GRID_HEIGHT_TILES):
            for c in range(GRID_WIDTH_TILES):
                self.grid[r][c].set_state(TILE_STATE_EMPTY, force_immediate=True)

        # --- Load Path and Prepare for Reveal ---
        current_path_coords = LEVELS[self.current_level_index]
        self.correct_reflection_coords.clear() # Clear reflection from previous level
        self.current_path_coords_to_reveal = [] # Clear path reveal list
        valid_path_exists = False
        print(f"--- Setting up Level {self.current_level_index + 1} ---")
        for r, c in current_path_coords:
            if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < SYMMETRY_LINE_TILE_INDEX:
                # DON'T set state here, just store coords for reveal
                self.current_path_coords_to_reveal.append((r, c))
                valid_path_exists = True
                # Calculate and store reflection (this part remains the same)
                reflected_coords = self._get_reflected_coords(r, c)
                if reflected_coords:
                    self.correct_reflection_coords.add(reflected_coords)
            else:
                print(f"  Warning: Invalid original path coordinate: ({r},{c})")

        if not valid_path_exists:
            print(f"  ERROR: Level {self.current_level_index + 1} has no valid path tiles.")
            return False

        # --- Set Initial Game State for Level Reveal ---
        self.game_state = STATE_SHOWING_PATH
        self.reveal_index = 0 # Start revealing from the first tile
        self.last_reveal_time = pygame.time.get_ticks() # Start timer for reveal delay

        return True

    def run(self):
        """Starts and manages the main game loop."""
        while self.running:
            # Get current time for state updates
            current_time = pygame.time.get_ticks()

            # Process events/inputs
            self._handle_input(current_time)

            # Update game state based on timers and logic
            self._update(current_time)

            # Draw everything to the screen
            self._draw()

            # Control the frame rate
            self.clock.tick(FPS)

        # --- Game Loop Ended ---
        print("Exiting game.")
        pygame.quit()
        sys.exit()

    def _handle_input(self, current_time):
        """Processes Pygame events (quit, mouse clicks)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False # Signal to exit the main loop

            # Handle clicks only when the player is supposed to be drawing
            if self.game_state == STATE_PLAYER_DRAWING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left mouse button
                        self._handle_tile_click(event.pos)

            # Allow restarting on Game Over/Complete with a click (for simplicity)
            if self.game_state in [STATE_GAME_OVER_TIME, STATE_GAME_OVER_INK, STATE_GAME_COMPLETE]:
                 if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                      # Reset to level 1 (or implement a proper menu later)
                      self.current_level_index = 0
                      if not self._setup_level():
                          self.running = False # Exit if reset fails

    def _handle_tile_click(self, mouse_pos):
        """Handles logic when a tile is clicked during PLAYER_DRAWING state."""
        if self.remaining_ink <= 0:
            # print("Out of ink!") # Optional feedback
            return # Can't draw without ink

        for r in range(GRID_HEIGHT_TILES):
            for c in range(GRID_WIDTH_TILES):
                tile = self.grid[r][c]
                if tile.is_clicked(mouse_pos):
                    # --- Allow drawing only on the player's side (right) ---
                    if tile.col >= SYMMETRY_LINE_TILE_INDEX:
                        clicked_coords = (r, c)
                        # --- Only allow drawing on empty tiles ---
                        if tile.state == TILE_STATE_EMPTY:
                            self.remaining_ink -= 1 # Use ink
                            self._play_sound(SOUND_CLICK) # Play click sound
                            self.player_drawn_tiles.add(clicked_coords) # Track player attempt

                            # --- Immediately check if correct and set state ---
                            if clicked_coords in self.correct_reflection_coords:
                                tile.set_state(TILE_STATE_CORRECT)
                                self._play_sound(SOUND_CORRECT) # Play correct sound
                            else:
                                tile.set_state(TILE_STATE_INCORRECT)
                                self._play_sound(SOUND_INCORRECT) # Play incorrect sound
                    # Found the clicked tile, no need to check others
                    return

    def _check_level_complete(self):
         """Checks if all required reflection tiles have been correctly drawn."""
         # A tile is correctly drawn if it's in the player set AND in the correct set
         correctly_drawn_player_tiles = self.player_drawn_tiles.intersection(self.correct_reflection_coords)
         return correctly_drawn_player_tiles == self.correct_reflection_coords

    def _update(self, current_time):
        # Update Tile Animations (Should be done first)
        for row in self.grid:
            for tile in row:
                tile.update_animation(current_time)

        # --- State-Specific Logic ---
        if self.game_state == STATE_SHOWING_PATH:
            # Reveal tiles sequentially
            if self.reveal_index < len(self.current_path_coords_to_reveal):
                if current_time - self.last_reveal_time >= PATH_REVEAL_DELAY_PER_TILE:
                    # Time to reveal the next tile
                    r, c = self.current_path_coords_to_reveal[self.reveal_index]
                    # Use force_immediate=True for instant reveal color, or False for reveal animation
                    self.grid[r][c].set_state(TILE_STATE_ORIGINAL_PATH, force_immediate=True)
                    self._play_sound(SOUND_PATH_SHOW) # Play sound for each reveal
                    self.reveal_index += 1
                    self.last_reveal_time = current_time # Reset timer for next delay
            else:
                # All tiles revealed, now wait for PATH_SHOW_DURATION before hiding
                # Calculate total reveal time approx.
                total_reveal_time = len(self.current_path_coords_to_reveal) * PATH_REVEAL_DELAY_PER_TILE
                # Wait an additional duration after the last tile is revealed
                # Let's use PATH_SHOW_DURATION as the *total* time the path is visible after reveal starts
                reveal_start_time = self.last_reveal_time - total_reveal_time # Approx start
                # Or simpler: Wait fixed duration after *last* reveal
                wait_after_reveal = PATH_SHOW_DURATION # How long to wait after last tile shown
                if current_time - self.last_reveal_time >= wait_after_reveal:
                     # Time to hide the path (using existing fade out animation)
                     for r, c in self.current_path_coords_to_reveal:
                         # Check if tile still exists and is in the correct state before hiding
                         if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < GRID_WIDTH_TILES:
                              if self.grid[r][c].state == TILE_STATE_ORIGINAL_PATH:
                                  self.grid[r][c].set_state(TILE_STATE_EMPTY) # Trigger fade out

                     self.game_state = STATE_PLAYER_DRAWING
                     self.level_timer_start = current_time # Start player timer

        # --- State: PLAYER_DRAWING ---
        elif self.game_state == STATE_PLAYER_DRAWING:
            # Update remaining time
            elapsed_time = current_time - self.level_timer_start
            self.remaining_time_ms = max(0, DEFAULT_LEVEL_TIME_LIMIT - elapsed_time)

            # Check for win condition first
            if self._check_level_complete():
                self.game_state = STATE_LEVEL_TRANSITION
                self.transition_timer_start = current_time
                print(f"Level {self.current_level_index + 1} Complete!")
                self._play_sound(SOUND_LEVEL_COMPLETE) # Play level complete sound

            # Check for lose conditions
            elif self.remaining_time_ms <= 0:
                self.game_state = STATE_GAME_OVER_TIME
                self.transition_timer_start = current_time # Start timer for message display
                print("Game Over: Time Up!")
                self._play_sound(SOUND_GAME_OVER) # Play game over sound
            elif self.remaining_ink <= 0 and not self._check_level_complete():
                 # Only trigger if ink is 0 AND level isn't complete
                 self.game_state = STATE_GAME_OVER_INK
                 self.transition_timer_start = current_time # Start timer for message display
                 print("Game Over: Ink Depleted!")
                 self._play_sound(SOUND_GAME_OVER) # Play game over sound


        # --- State: LEVEL_TRANSITION ---
        elif self.game_state == STATE_LEVEL_TRANSITION:
            # Wait for a short delay, then move to the next level
            if current_time - self.transition_timer_start >= LEVEL_TRANSITION_DELAY:
                self.current_level_index += 1
                if not self._setup_level(): # setup_level handles GAME_COMPLETE state
                     # If setup fails (e.g., no more levels), state is already GAME_COMPLETE
                     self.transition_timer_start = current_time # Start timer for final message

        # --- States: GAME_OVER / GAME_COMPLETE ---
        # These states currently just wait for input handled in _handle_input to restart

    def _draw_grid_and_tiles(self):
        """Draws the background tiles and the grid lines."""
        for row in self.grid:
            for tile in row:
                # Pass False to avoid double-drawing grid lines if preferred
                tile.draw(self.screen, draw_grid_overlay=True)
        # If draw_grid_overlay=False in tile.draw, uncomment below:
        # self._draw_grid_lines()

    # Helper if needed separately
    # def _draw_grid_lines(self):
    #     # ... (Copy grid line drawing logic from previous version) ...

    def _draw_symmetry_line(self):
        """Draws the central symmetry line."""
        pygame.draw.line(
            self.screen,
            COLOR_SYMMETRY_LINE,
            (SYMMETRY_LINE_X, GRID_ORIGIN_Y),
            (SYMMETRY_LINE_X, GRID_ORIGIN_Y + GRID_HEIGHT_PX),
            SYMMETRY_LINE_WIDTH
        )

    def _draw_ui(self):
        """Draws the User Interface elements (timer, ink)."""
        if not FONT_AVAILABLE: return # Cannot draw text if font failed

        try:
            # Format time (seconds remaining with one decimal place)
            time_sec = self.remaining_time_ms / 1000.0
            time_text = f"Zaman: {time_sec:.1f}s"
            ink_text = f"Mürekkep: {self.remaining_ink}"

            time_surface = self.font.render(time_text, True, COLOR_UI_TEXT)
            ink_surface = self.font.render(ink_text, True, COLOR_UI_TEXT)

            # Draw Time top-left (aligned with grid)
            self.screen.blit(time_surface, (UI_MARGIN_LEFT, UI_MARGIN_TOP))
            # Draw Ink spaced to the right
            self.screen.blit(ink_surface, (UI_MARGIN_LEFT + UI_INFO_SPACING, UI_MARGIN_TOP))

        except Exception as e:
            print(f"Error rendering UI text: {e}") # Catch potential rendering errors

    def _draw_messages(self, current_time):
         """Draws game state messages (Game Over, Level Complete, etc.)."""
         if not FONT_AVAILABLE: return

         message = None
         if self.game_state == STATE_GAME_OVER_TIME:
             message = "SÜRE DOLDU!"
         elif self.game_state == STATE_GAME_OVER_INK:
             message = "MÜREKKEP BİTTİ!"
         elif self.game_state == STATE_GAME_COMPLETE:
              message = "TEBRİKLER! OYUN BİTTİ!"
         elif self.game_state == STATE_LEVEL_TRANSITION:
              # Optionally show "Level Complete" briefly during transition
              if current_time - self.transition_timer_start < LEVEL_TRANSITION_DELAY - 300: # Show for most of delay
                    message = f"SEVİYE {self.current_level_index + 1} TAMAMLANDI!" # Show previous level number


         if message:
             try:
                message_surface = self.font.render(message, True, COLOR_MESSAGE_TEXT)
                message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

                # Draw semi-transparent background for better readability
                bg_rect = message_rect.inflate(40, 20) # Add padding
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA) # Enable transparency
                bg_surface.fill(COLOR_MESSAGE_BG)
                self.screen.blit(bg_surface, bg_rect.topleft)

                # Draw the message text on top
                self.screen.blit(message_surface, message_rect)

                # Add restart prompt for Game Over / Game Complete states
                if self.game_state in [STATE_GAME_OVER_TIME, STATE_GAME_OVER_INK, STATE_GAME_COMPLETE]:
                     prompt_text = "Yeniden Başlamak İçin Tıkla"
                     prompt_surface = self.font.render(prompt_text, True, COLOR_UI_TEXT)
                     prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, message_rect.bottom + 30))
                     self.screen.blit(prompt_surface, prompt_rect)

             except Exception as e:
                 print(f"Error rendering message '{message}': {e}")


    def _draw(self):
        """Draws all game elements onto the screen."""
        # 1. Fill background (Image or Color)
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0)) # Draw image first
        else:
            self.screen.fill(COLOR_BACKGROUND) # Fallback if no image

        # --- Draw elements ON TOP of the background ---
        self._draw_grid_and_tiles()
        self._draw_symmetry_line()
        self._draw_ui()
        self._draw_messages(pygame.time.get_ticks())
        # ---------------------------------------------

        pygame.display.flip()