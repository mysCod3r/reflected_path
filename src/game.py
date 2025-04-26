# src/game.py
import pygame
import sys
import os
from src.config import *
from src.tile import Tile
# Import both LEVELS and LEVEL_SETTINGS
from src.level_data import LEVELS, LEVEL_SETTINGS

class Game:
    def __init__(self):
        # --- Core Pygame Initialization ---
        try:
            pygame.init()
            # print("Pygame initialized successfully.") # Optional debug
        except pygame.error as e:
            print(f"FATAL: Pygame initialization failed: {e}")
            sys.exit(1)

        # --- Display Setup ---
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(WINDOW_TITLE) # Use title from config
            # print(f"Display set to {SCREEN_WIDTH}x{SCREEN_HEIGHT}") # Optional debug
        except pygame.error as e:
            print(f"FATAL: Failed to set display mode: {e}")
            pygame.quit()
            sys.exit(1)

        # --- Font Setup ---
        # Font loading and availability check is handled in config.py
        # We just assign the imported font object and availability flag.
        self.font = UI_FONT # Use the font object loaded by config.py
        self.FONT_AVAILABLE = FONT_AVAILABLE # Use the flag set by config.py

        # --- Clock ---
        self.clock = pygame.time.Clock()

        # --- Game State ---
        self.running = True
        self.game_state = STATE_SHOWING_PATH
        self.current_level_index = 0

        # --- Level Specific Data ---
        self.grid = self._create_grid()
        self.correct_reflection_coords = set()
        self.player_drawn_tiles = set()

        # --- Timers, Limits & Counters ---
        self.remaining_ink = DEFAULT_LEVEL_INK_LIMIT
        self.remaining_time_ms = DEFAULT_LEVEL_TIME_LIMIT
        self.mistake_limit = DEFAULT_MISTAKE_LIMIT # Max allowed mistakes for the level
        self.mistakes_made = 0 # Counter for incorrect clicks this level

        self.path_show_start_time = 0
        self.level_timer_start = 0
        self.transition_timer_start = 0
        self.last_timer_warning_play_time = 0

        # --- Load Sounds & Background ---
        self.sound_enabled = False # Will be set by mixer init
        self.sounds = {}
        self._initialize_mixer_and_load_sounds() # Combined helper for cleaner init

        self.background_image = self._load_background() # Helper to load background

        # --- Initial Level Setup ---
        if not self._setup_level():
            print("ERROR: Failed to setup initial level. Exiting.")
            self.running = False

    # --- Initialization Helpers ---

    def _initialize_mixer_and_load_sounds(self):
        """Initializes the mixer and loads sounds."""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            # print("Pygame mixer initialized.") # Less verbose logging
            self.sound_enabled = True
            self._load_sounds()
        except pygame.error as e:
            print(f"Warning: Mixer init failed: {e}. Sounds disabled.")
            self.sound_enabled = False
            self.sounds = {}

    def _load_sounds(self):
        """Loads sound effects into self.sounds dictionary."""
        # (This method remains the same as before, using sound constants)
        self.sounds = {}
        sound_files = {
            SOUND_CLICK: 'assets/sounds/click.wav',
            SOUND_CORRECT: 'assets/sounds/correct.wav',
            SOUND_INCORRECT: 'assets/sounds/incorrect.wav',
            SOUND_LEVEL_COMPLETE: 'assets/sounds/level_complete.wav',
            SOUND_GAME_OVER: 'assets/sounds/game_over.wav',
            SOUND_PATH_SHOW: 'assets/sounds/path_show.wav',
            SOUND_TIMER_LOW: 'assets/sounds/timer_warning.wav',
        }
        # print("Loading sounds...") # Less verbose
        loaded_count = 0
        for name_key, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name_key] = pygame.mixer.Sound(path)
                    loaded_count += 1
                else:
                    # print(f"  Warning: Sound file not found for '{name_key}': {path}") # Less verbose
                    self.sounds[name_key] = None
            except pygame.error as e:
                print(f"  Error loading sound for '{name_key}' ({path}): {e}")
                self.sounds[name_key] = None
        # print(f"Sounds loaded: {loaded_count}/{len(sound_files)}") # Less verbose


    def _load_background(self):
        """Loads and returns the background image surface."""
        background_path = "assets/images/background.png"
        try:
            if os.path.exists(background_path):
                loaded_image = pygame.image.load(background_path)
                background_surface = loaded_image.convert_alpha() if background_path.lower().endswith(".png") else loaded_image.convert()
                if background_surface.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                    # print(f"Warning: Scaling background {background_path}...") # Less verbose
                    background_surface = pygame.transform.scale(background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
                # print(f"Loaded background: {background_path}") # Less verbose
                return background_surface
            else:
                # print(f"Warning: Background not found: {background_path}") # Less verbose
                return None
        except pygame.error as e:
            print(f"Error loading background {background_path}: {e}")
            return None

    # --- Grid and Level Setup ---

    def _create_grid(self):
        """Creates and returns the grid as a 2D list of Tile objects."""
        # (This method remains the same)
        grid = []
        for r in range(GRID_HEIGHT_TILES):
            row_tiles = [Tile(r, c) for c in range(GRID_WIDTH_TILES)]
            grid.append(row_tiles)
        return grid

    def _get_reflected_coords(self, row, col):
        """Calculates the reflected coordinates across the vertical symmetry line."""
        # (This method remains the same)
        if not (0 <= row < GRID_HEIGHT_TILES and 0 <= col < SYMMETRY_LINE_TILE_INDEX):
            return None
        distance_from_line = SYMMETRY_LINE_TILE_INDEX - col - 1
        reflected_col = SYMMETRY_LINE_TILE_INDEX + distance_from_line
        if 0 <= reflected_col < GRID_WIDTH_TILES:
            return row, reflected_col
        else:
            return None

    def _setup_level(self):
        """Sets up the game state for the current level index."""
        if not (0 <= self.current_level_index < len(LEVELS)):
            self.game_state = STATE_GAME_COMPLETE
            # print("All levels completed!") # Less verbose
            return False

        # --- Get Level Settings ---
        # Start with defaults
        level_time = DEFAULT_LEVEL_TIME_LIMIT
        level_ink = DEFAULT_LEVEL_INK_LIMIT
        level_mistakes = DEFAULT_MISTAKE_LIMIT

        # Override with level-specific settings if they exist
        if self.current_level_index < len(LEVEL_SETTINGS):
            settings = LEVEL_SETTINGS[self.current_level_index]
            level_time = settings.get('time', level_time) # Use default if key missing
            level_ink = settings.get('ink', level_ink)
            level_mistakes = settings.get('mistakes', level_mistakes)

        # --- Reset Level State ---
        self.correct_reflection_coords.clear()
        self.player_drawn_tiles.clear()
        self.remaining_ink = level_ink # Use level-specific or default ink
        self.remaining_time_ms = level_time # Use level-specific or default time
        self.mistake_limit = level_mistakes # Use level-specific or default limit
        self.mistakes_made = 0 # Reset mistake counter
        self.last_timer_warning_play_time = 0 # Reset warning timer

        # Clear Grid Tile States
        for r in range(GRID_HEIGHT_TILES):
            for c in range(GRID_WIDTH_TILES):
                self.grid[r][c].set_state(TILE_STATE_EMPTY, force_immediate=True)

        # Load Path and Prepare for Reveal
        current_path_coords = LEVELS[self.current_level_index]
        self.current_path_coords_to_reveal = []
        valid_path_exists = False
        # print(f"--- Setting up Level {self.current_level_index + 1} ---") # Less verbose
        for r, c in current_path_coords:
            if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < SYMMETRY_LINE_TILE_INDEX:
                self.current_path_coords_to_reveal.append((r, c))
                valid_path_exists = True
                reflected_coords = self._get_reflected_coords(r, c)
                if reflected_coords:
                    self.correct_reflection_coords.add(reflected_coords)
            # else: # Less verbose
                # print(f"  Warning: Invalid original path coordinate: ({r},{c})")

        if not valid_path_exists:
            print(f"  ERROR: Level {self.current_level_index + 1} invalid path.")
            return False

        # Set Initial Game State
        self.game_state = STATE_SHOWING_PATH
        self.reveal_index = 0
        self.last_reveal_time = pygame.time.get_ticks()
        # Play path show sound immediately if there's a path
        if self.current_path_coords_to_reveal:
             self._play_sound(SOUND_PATH_SHOW)

        return True

    # --- Main Loop and Handlers ---

    def run(self):
        """Starts and manages the main game loop."""
        # (This method remains the same)
        while self.running:
            current_time = pygame.time.get_ticks()
            self._handle_input(current_time)
            self._update(current_time)
            self._draw()
            self.clock.tick(FPS)
        print("Exiting game.")
        pygame.quit()
        sys.exit()

    def _handle_input(self, current_time):
        """Processes Pygame events (quit, mouse clicks, restart)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == STATE_PLAYER_DRAWING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_tile_click(event.pos)

            # Restart on Game Over/Complete with click or key press
            if self.game_state in [STATE_GAME_OVER_TIME, STATE_GAME_OVER_INK, STATE_GAME_OVER_MISTAKES, STATE_GAME_COMPLETE]:
                 if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                      # print("Restarting game...") # Less verbose
                      self.current_level_index = 0
                      if not self._setup_level():
                          self.running = False

    def _handle_tile_click(self, mouse_pos):
        """Handles logic when a tile is clicked during PLAYER_DRAWING state."""
        if self.remaining_ink <= 0: return

        for r in range(GRID_HEIGHT_TILES):
            for c in range(GRID_WIDTH_TILES):
                tile = self.grid[r][c]
                if tile.is_clicked(mouse_pos):
                    if tile.col >= SYMMETRY_LINE_TILE_INDEX and tile.state == TILE_STATE_EMPTY:
                        # --- Click Action ---
                        self._play_sound(SOUND_CLICK)
                        self.remaining_ink -= 1
                        clicked_coords = (r, c)
                        self.player_drawn_tiles.add(clicked_coords)

                        # --- Check Correctness ---
                        if clicked_coords in self.correct_reflection_coords:
                            tile.set_state(TILE_STATE_CORRECT)
                            self._play_sound(SOUND_CORRECT)
                        else:
                            tile.set_state(TILE_STATE_INCORRECT)
                            self._play_sound(SOUND_INCORRECT)
                            self.mistakes_made += 1 # Increment mistake counter

                        # --- Check for immediate mistake game over ---
                        if self.mistakes_made > self.mistake_limit:
                             self.game_state = STATE_GAME_OVER_MISTAKES
                             self.transition_timer_start = pygame.time.get_ticks()
                             self._play_sound(SOUND_GAME_OVER) # Play game over sound
                             print("Game Over: Too Many Mistakes!")

                    return # Found clicked tile

    def _check_level_complete(self):
         """Checks if all required reflection tiles have been correctly drawn."""
         # (This method remains the same)
         correctly_drawn_player_tiles = self.player_drawn_tiles.intersection(self.correct_reflection_coords)
         return correctly_drawn_player_tiles == self.correct_reflection_coords and len(self.correct_reflection_coords) > 0


    def _update(self, current_time):
        """Updates the game state AND tile animations."""
        # Update Tile Animations first
        for row in self.grid:
            for tile in row:
                tile.update_animation(current_time)

        # State-Specific Logic
        if self.game_state == STATE_SHOWING_PATH:
            # Sequential reveal logic (remains the same)
            if self.reveal_index < len(self.current_path_coords_to_reveal):
                if current_time - self.last_reveal_time >= PATH_REVEAL_DELAY_PER_TILE:
                    r, c = self.current_path_coords_to_reveal[self.reveal_index]
                    if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < GRID_WIDTH_TILES: # Bounds check
                        self.grid[r][c].set_state(TILE_STATE_ORIGINAL_PATH, force_immediate=True)
                    self._play_sound(SOUND_PATH_SHOW)
                    self.reveal_index += 1
                    self.last_reveal_time = current_time
            else:
                # Wait after last reveal before hiding
                wait_after_reveal = PATH_SHOW_DURATION
                if self.reveal_index > 0: # Ensure at least one tile was revealed
                    if current_time - self.last_reveal_time >= wait_after_reveal:
                        for r, c in self.current_path_coords_to_reveal:
                             if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < GRID_WIDTH_TILES:
                                if self.grid[r][c].state == TILE_STATE_ORIGINAL_PATH:
                                    self.grid[r][c].set_state(TILE_STATE_EMPTY) # Fade out
                        self.game_state = STATE_PLAYER_DRAWING
                        self.level_timer_start = current_time

        elif self.game_state == STATE_PLAYER_DRAWING:
            # Update time
            elapsed_time = current_time - self.level_timer_start
            # Use level-specific time limit or default
            current_level_time_limit = DEFAULT_LEVEL_TIME_LIMIT
            if self.current_level_index < len(LEVEL_SETTINGS):
                current_level_time_limit = LEVEL_SETTINGS[self.current_level_index].get('time', DEFAULT_LEVEL_TIME_LIMIT)
            self.remaining_time_ms = max(0, current_level_time_limit - elapsed_time)

            # Play Timer Warning Sound
            if self.remaining_time_ms <= TIMER_WARNING_THRESHOLD_MS and self.remaining_time_ms > 0:
                if current_time - self.last_timer_warning_play_time >= TIMER_WARNING_REPEAT_DELAY_MS:
                    self._play_sound(SOUND_TIMER_LOW)
                    self.last_timer_warning_play_time = current_time

            # Check Win/Loss (Mistake check moved to _handle_tile_click for immediacy)
            if self._check_level_complete():
                if self.game_state != STATE_LEVEL_TRANSITION:
                    self.game_state = STATE_LEVEL_TRANSITION
                    self.transition_timer_start = current_time
                    # print(f"Level {self.current_level_index + 1} Complete!") # Less verbose
                    self._play_sound(SOUND_LEVEL_COMPLETE)
            elif self.remaining_time_ms <= 0:
                if self.game_state != STATE_GAME_OVER_TIME:
                    self.game_state = STATE_GAME_OVER_TIME
                    self.transition_timer_start = current_time
                    self._play_sound(SOUND_GAME_OVER)
                    print("Game Over: Time Up!")
            elif self.remaining_ink <= 0 and not self._check_level_complete():
                # Check if already Game Over by mistakes first
                if self.game_state != STATE_GAME_OVER_INK and self.game_state != STATE_GAME_OVER_MISTAKES:
                    self.game_state = STATE_GAME_OVER_INK
                    self.transition_timer_start = current_time
                    self._play_sound(SOUND_GAME_OVER)
                    print("Game Over: Ink Depleted!")

        elif self.game_state == STATE_LEVEL_TRANSITION:
            if current_time - self.transition_timer_start >= LEVEL_TRANSITION_DELAY:
                self.current_level_index += 1
                if not self._setup_level():
                    self.transition_timer_start = current_time # Keep timer for final message

        # Other states (GAME_OVER_*, GAME_COMPLETE) wait for input in _handle_input

    # --- Drawing Methods ---

    def _draw_grid_and_tiles(self):
        """Draws the background tiles and the grid lines."""
        # (This method remains the same)
        for row in self.grid:
            for tile in row:
                tile.draw(self.screen, draw_grid_overlay=True)

    def _draw_symmetry_line(self):
        """Draws the central symmetry line."""
        # (This method remains the same)
        pygame.draw.line(
            self.screen, COLOR_SYMMETRY_LINE,
            (SYMMETRY_LINE_X, GRID_ORIGIN_Y),
            (SYMMETRY_LINE_X, GRID_ORIGIN_Y + GRID_HEIGHT_PX),
            SYMMETRY_LINE_WIDTH
        )

    def _draw_ui(self):
        """Draws the User Interface elements (timer, ink, mistakes)."""
        if not FONT_AVAILABLE: return

        try:
            time_sec = self.remaining_time_ms / 1000.0
            time_text = f"Zaman: {time_sec:.1f}s"
            ink_text = f"Mürekkep: {self.remaining_ink}"
            # Display mistakes remaining: limit - made
            mistakes_remaining = max(0, self.mistake_limit - self.mistakes_made)
            mistakes_text = f"Hata Hakkı: {mistakes_remaining}" # Changed text

            time_surface = self.font.render(time_text, True, COLOR_UI_TEXT)
            ink_surface = self.font.render(ink_text, True, COLOR_UI_TEXT)
            mistakes_surface = self.font.render(mistakes_text, True, COLOR_UI_TEXT)

            # Position UI elements
            time_pos = (UI_MARGIN_LEFT, UI_MARGIN_TOP)
            ink_pos = (UI_MARGIN_LEFT + UI_INFO_SPACING, UI_MARGIN_TOP)
            # Position mistakes further right or below
            mistakes_pos = (UI_MARGIN_LEFT + UI_INFO_SPACING * 2, UI_MARGIN_TOP)

            self.screen.blit(time_surface, time_pos)
            self.screen.blit(ink_surface, ink_pos)
            self.screen.blit(mistakes_surface, mistakes_pos)

        except Exception as e:
            print(f"Error rendering UI text: {e}")

    def _draw_messages(self, current_time):
         """Draws game state messages."""
         # (Add STATE_GAME_OVER_MISTAKES to message logic)
         if not FONT_AVAILABLE: return

         message = None
         is_final_state = False # Flag for adding restart prompt

         if self.game_state == STATE_GAME_OVER_TIME:
             message = "SÜRE DOLDU!"
             is_final_state = True
         elif self.game_state == STATE_GAME_OVER_INK:
             message = "MÜREKKEP BİTTİ!"
             is_final_state = True
         elif self.game_state == STATE_GAME_OVER_MISTAKES: # New message
             message = "ÇOK FAZLA HATA!"
             is_final_state = True
         elif self.game_state == STATE_GAME_COMPLETE:
              message = "TEBRİKLER! OYUN BİTTİ!"
              is_final_state = True
         elif self.game_state == STATE_LEVEL_TRANSITION:
              if current_time - self.transition_timer_start < LEVEL_TRANSITION_DELAY - 300:
                    message = f"SEVİYE {self.current_level_index} TAMAMLANDI!" # Show COMPLETED level number

         if message:
             try:
                message_surface = self.font.render(message, True, COLOR_MESSAGE_TEXT)
                message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                bg_rect = message_rect.inflate(40, 20)
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                bg_surface.fill(COLOR_MESSAGE_BG)
                self.screen.blit(bg_surface, bg_rect.topleft)
                self.screen.blit(message_surface, message_rect)

                if is_final_state: # Show restart only on final states
                     prompt_text = "Yeniden Başlamak İçin Tıkla"
                     prompt_surface = self.font.render(prompt_text, True, COLOR_UI_TEXT)
                     prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, message_rect.bottom + 30))
                     self.screen.blit(prompt_surface, prompt_rect)
             except Exception as e:
                 print(f"Error rendering message '{message}': {e}")

    def _draw(self):
        """Draws all game elements onto the screen."""
        # (This method remains the same, calls other draw methods)
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(COLOR_BACKGROUND)
        self._draw_grid_and_tiles()
        self._draw_symmetry_line()
        self._draw_ui()
        self._draw_messages(pygame.time.get_ticks())
        pygame.display.flip()

    def _play_sound(self, name_key):
        """Plays a loaded sound effect if available."""
        # (This method remains the same)
        if self.sound_enabled and name_key in self.sounds and self.sounds[name_key]:
            try:
                self.sounds[name_key].play()
            except pygame.error as e:
                print(f"Error playing sound '{name_key}': {e}")