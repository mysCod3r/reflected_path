# src/game.py
import pygame
import sys
import os
from src.config import *
from src.tile import Tile
from src.level_data import *

class Game:
    def __init__(self):
        """Initialize Pygame, display, subsystems, and game variables."""
        # --- 1. Initialize ALL of Pygame FIRST ---
        try:
            pygame.init()
            print("Pygame initialized successfully.")
        except pygame.error as e:
            print(f"CRITICAL ERROR: Pygame initialization failed: {e}")
            sys.exit("Failed to initialize Pygame.")

        # --- 2. Set Display Mode SECOND ---
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(WINDOW_TITLE)
            print("Display mode set successfully.")
        except pygame.error as e:
            print(f"CRITICAL ERROR: Could not set display mode: {e}")
            pygame.quit() # Clean up pygame if display fails
            sys.exit("Failed to initialize display.")

        # --- 3. Initialize Other Subsystems (Mixer, Font) ---
        self._initialize_mixer()
        self._initialize_font() # Use helper for font init

        # --- 4. Load Assets (Sounds, Images - AFTER display is set) ---
        self._load_sounds() # Load sounds now that mixer is ready
        self.background_image = self._load_background() # Load background now that display is ready

        # --- 5. Initialize Game Components & State ---
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = STATE_SHOWING_PATH
        self.current_level_index = 0
        self.grid = self._create_grid()

        # --- Level Specific Data Containers ---
        self.correct_reflection_coords = set()
        self.player_drawn_tiles = set()
        self.current_path_coords_to_reveal = [] # Path for reveal animation

        # --- Timers, Limits & Counters ---
        self.remaining_ink = DEFAULT_LEVEL_INK_LIMIT
        self.remaining_time_ms = DEFAULT_LEVEL_TIME_LIMIT
        self.mistake_limit = DEFAULT_MISTAKE_LIMIT
        self.mistakes_made = 0

        self.path_show_start_time = 0
        self.level_timer_start = 0
        self.transition_timer_start = 0
        self.last_timer_warning_play_time = 0
        self.reveal_index = 0
        self.last_reveal_time = 0

        # --- 6. Initial Level Setup ---
        if not self._setup_level():
            print("ERROR: Failed to setup initial level. Exiting.")
            self.running = False # Stop the game loop if setup fails

    # --- Initialization Helpers ---

    def _initialize_mixer(self):
        """Initializes the Pygame mixer."""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            # print("Pygame mixer initialized.")
            self.sound_enabled = True
        except pygame.error as e:
            print(f"Warning: Mixer init failed: {e}. Sounds disabled.")
            self.sound_enabled = False
            self.sounds = {}

    def _initialize_font(self):
        """Initializes the font object using config settings."""
        # Font module should be initialized by pygame.init()
        # We just need to load the font object here
        self.font = UI_FONT # Get font object loaded in config.py
        if not FONT_AVAILABLE:
            print("CRITICAL: Font not available. UI text cannot be rendered.")
            # Game might still run, but without text

    def _load_sounds(self):
        """Loads sound effects into self.sounds dictionary."""
        self.sounds = {} # Initialize fresh
        if not self.sound_enabled: return # Don't load if mixer failed

        sound_files = {
            SOUND_CLICK: 'assets/sounds/click.wav',
            SOUND_CORRECT: 'assets/sounds/correct.wav',
            SOUND_INCORRECT: 'assets/sounds/incorrect.wav',
            SOUND_LEVEL_COMPLETE: 'assets/sounds/level_complete.wav',
            SOUND_GAME_OVER: 'assets/sounds/game_over.wav',
            SOUND_PATH_SHOW: 'assets/sounds/path_show.wav',
            SOUND_TIMER_LOW: 'assets/sounds/timer_warning.wav',
        }
        loaded_count = 0
        for name_key, path in sound_files.items():
            # (Loading logic remains the same)
            try:
                if os.path.exists(path):
                    self.sounds[name_key] = pygame.mixer.Sound(path)
                    loaded_count += 1
                else:
                    self.sounds[name_key] = None
            except pygame.error as e:
                print(f"  Error loading sound '{name_key}': {e}")
                self.sounds[name_key] = None
        # print(f"Sounds loaded: {loaded_count}/{len(sound_files)}")

    def _load_background(self):
        """Loads and converts the background image surface."""
        background_path = "assets/images/background.png"
        try:
            if os.path.exists(background_path):
                loaded_image = pygame.image.load(background_path)
                background_surface = loaded_image.convert_alpha() if background_path.lower().endswith(".png") else loaded_image.convert()

                if background_surface.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
                    background_surface = pygame.transform.scale(background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
                return background_surface
            else:
                return None
        except pygame.error as e:
            print(f"Error loading background {background_path}: {e}")
            return None
        except Exception as e_gen: # Catch other potential errors
             print(f"Unexpected error loading background: {e_gen}")
             return None

    # --- Grid and Level Setup
    def _create_grid(self):
        grid = []
        for r in range(GRID_HEIGHT_TILES):
            row_tiles = [Tile(r, c) for c in range(GRID_WIDTH_TILES)]
            grid.append(row_tiles)
        return grid

    def _get_reflected_coords(self, row, col):
        if not (0 <= row < GRID_HEIGHT_TILES and 0 <= col < SYMMETRY_LINE_TILE_INDEX): return None
        distance_from_line = SYMMETRY_LINE_TILE_INDEX - col - 1
        reflected_col = SYMMETRY_LINE_TILE_INDEX + distance_from_line
        if 0 <= reflected_col < GRID_WIDTH_TILES: return row, reflected_col
        else: return None

    def _setup_level(self):
        if not (0 <= self.current_level_index < len(LEVELS)):
            self.game_state = STATE_GAME_COMPLETE
            return False

        level_time = DEFAULT_LEVEL_TIME_LIMIT
        level_ink = DEFAULT_LEVEL_INK_LIMIT
        level_mistakes = DEFAULT_MISTAKE_LIMIT
        if self.current_level_index < len(LEVEL_SETTINGS):
            settings = LEVEL_SETTINGS[self.current_level_index]
            level_time = settings.get('time', level_time)
            level_ink = settings.get('ink', level_ink)
            level_mistakes = settings.get('mistakes', level_mistakes)

        self.correct_reflection_coords.clear()
        self.player_drawn_tiles.clear()
        self.remaining_ink = level_ink
        self.remaining_time_ms = level_time
        self.mistake_limit = level_mistakes
        self.mistakes_made = 0
        self.last_timer_warning_play_time = 0

        for r in range(GRID_HEIGHT_TILES):
            for c in range(GRID_WIDTH_TILES):
                self.grid[r][c].set_state(TILE_STATE_EMPTY, force_immediate=True)

        current_path_coords = LEVELS[self.current_level_index]
        self.current_path_coords_to_reveal = []
        valid_path_exists = False
        for r, c in current_path_coords:
            if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < SYMMETRY_LINE_TILE_INDEX:
                self.current_path_coords_to_reveal.append((r, c))
                valid_path_exists = True
                reflected_coords = self._get_reflected_coords(r, c)
                if reflected_coords: self.correct_reflection_coords.add(reflected_coords)

        if not valid_path_exists: return False

        self.game_state = STATE_SHOWING_PATH
        self.reveal_index = 0
        self.last_reveal_time = pygame.time.get_ticks()
        if self.current_path_coords_to_reveal: self._play_sound(SOUND_PATH_SHOW)

        return True

    # --- Main Loop and Handlers ---
    def run(self):
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if self.game_state == STATE_PLAYER_DRAWING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self._handle_tile_click(event.pos)
            if self.game_state in [STATE_GAME_OVER_TIME, STATE_GAME_OVER_INK, STATE_GAME_OVER_MISTAKES, STATE_GAME_COMPLETE]:
                 if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                      self.current_level_index = 0
                      if not self._setup_level(): self.running = False

    def _handle_tile_click(self, mouse_pos):
        if self.remaining_ink <= 0: return
        for r in range(GRID_HEIGHT_TILES):
            for c in range(GRID_WIDTH_TILES):
                tile = self.grid[r][c]
                if tile.is_clicked(mouse_pos):
                    if tile.col >= SYMMETRY_LINE_TILE_INDEX and tile.state == TILE_STATE_EMPTY:
                        self._play_sound(SOUND_CLICK)
                        self.remaining_ink -= 1
                        clicked_coords = (r, c)
                        self.player_drawn_tiles.add(clicked_coords)
                        if clicked_coords in self.correct_reflection_coords:
                            tile.set_state(TILE_STATE_CORRECT)
                            self._play_sound(SOUND_CORRECT)
                        else:
                            tile.set_state(TILE_STATE_INCORRECT)
                            self._play_sound(SOUND_INCORRECT)
                            self.mistakes_made += 1
                        # Check mistake limit immediately after incrementing
                        if self.mistakes_made > self.mistake_limit:
                             self.game_state = STATE_GAME_OVER_MISTAKES
                             self.transition_timer_start = pygame.time.get_ticks()
                             self._play_sound(SOUND_GAME_OVER)
                             print("Game Over: Too Many Mistakes!")
                    return

    def _check_level_complete(self):
         correctly_drawn_player_tiles = self.player_drawn_tiles.intersection(self.correct_reflection_coords)
         return len(self.correct_reflection_coords) > 0 and correctly_drawn_player_tiles == self.correct_reflection_coords

    def _update(self, current_time):
        for row in self.grid: # Update animations first
            for tile in row: tile.update_animation(current_time)

        if self.game_state == STATE_SHOWING_PATH:
            if self.reveal_index < len(self.current_path_coords_to_reveal):
                if current_time - self.last_reveal_time >= PATH_REVEAL_DELAY_PER_TILE:
                    r, c = self.current_path_coords_to_reveal[self.reveal_index]
                    if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < GRID_WIDTH_TILES:
                        self.grid[r][c].set_state(TILE_STATE_ORIGINAL_PATH, force_immediate=True)
                    self._play_sound(SOUND_PATH_SHOW)
                    self.reveal_index += 1
                    self.last_reveal_time = current_time
            else:
                wait_after_reveal = PATH_SHOW_DURATION
                if self.reveal_index > 0:
                    if current_time - self.last_reveal_time >= wait_after_reveal:
                        for r, c in self.current_path_coords_to_reveal:
                             if 0 <= r < GRID_HEIGHT_TILES and 0 <= c < GRID_WIDTH_TILES:
                                if self.grid[r][c].state == TILE_STATE_ORIGINAL_PATH:
                                    self.grid[r][c].set_state(TILE_STATE_EMPTY)
                        self.game_state = STATE_PLAYER_DRAWING
                        self.level_timer_start = current_time

        elif self.game_state == STATE_PLAYER_DRAWING:
            current_level_time_limit = DEFAULT_LEVEL_TIME_LIMIT
            if self.current_level_index < len(LEVEL_SETTINGS):
                current_level_time_limit = LEVEL_SETTINGS[self.current_level_index].get('time', DEFAULT_LEVEL_TIME_LIMIT)
            elapsed_time = current_time - self.level_timer_start
            self.remaining_time_ms = max(0, current_level_time_limit - elapsed_time)

            if self.remaining_time_ms <= TIMER_WARNING_THRESHOLD_MS and self.remaining_time_ms > 0:
                if current_time - self.last_timer_warning_play_time >= TIMER_WARNING_REPEAT_DELAY_MS:
                    self._play_sound(SOUND_TIMER_LOW)
                    self.last_timer_warning_play_time = current_time

            if self._check_level_complete():
                if self.game_state != STATE_LEVEL_TRANSITION:
                    self.game_state = STATE_LEVEL_TRANSITION
                    self.transition_timer_start = current_time
                    self._play_sound(SOUND_LEVEL_COMPLETE)
            elif self.remaining_time_ms <= 0:
                if self.game_state != STATE_GAME_OVER_TIME:
                    self.game_state = STATE_GAME_OVER_TIME
                    self.transition_timer_start = current_time
                    self._play_sound(SOUND_GAME_OVER)
                    print("Game Over: Time Up!")
            # Check ink AFTER mistake check in handle_click
            elif self.remaining_ink <= 0 and not self._check_level_complete():
                if self.game_state not in [STATE_GAME_OVER_INK, STATE_GAME_OVER_MISTAKES]: # Don't override mistake game over
                    self.game_state = STATE_GAME_OVER_INK
                    self.transition_timer_start = current_time
                    self._play_sound(SOUND_GAME_OVER)
                    print("Game Over: Ink Depleted!")


        elif self.game_state == STATE_LEVEL_TRANSITION:
            if current_time - self.transition_timer_start >= LEVEL_TRANSITION_DELAY:
                self.current_level_index += 1
                if not self._setup_level():
                    self.transition_timer_start = current_time

    def _draw_grid_and_tiles(self):
        for row in self.grid:
            for tile in row: tile.draw(self.screen, draw_grid_overlay=True)

    def _draw_symmetry_line(self):
        pygame.draw.line(self.screen, COLOR_SYMMETRY_LINE, (SYMMETRY_LINE_X, GRID_ORIGIN_Y), (SYMMETRY_LINE_X, GRID_ORIGIN_Y + GRID_HEIGHT_PX), SYMMETRY_LINE_WIDTH)

    def _draw_ui(self):
        if not FONT_AVAILABLE: return
        try:
            time_sec = self.remaining_time_ms / 1000.0; time_text = f"Zaman: {time_sec:.1f}s"
            ink_text = f"Mürekkep: {self.remaining_ink}"
            mistakes_remaining = max(0, self.mistake_limit - self.mistakes_made); mistakes_text = f"Hata Hakkı: {mistakes_remaining}"
            time_surface = self.font.render(time_text, True, COLOR_UI_TEXT); ink_surface = self.font.render(ink_text, True, COLOR_UI_TEXT); mistakes_surface = self.font.render(mistakes_text, True, COLOR_UI_TEXT)
            time_pos = (UI_MARGIN_LEFT, UI_MARGIN_TOP); ink_pos = (UI_MARGIN_LEFT + UI_INFO_SPACING, UI_MARGIN_TOP); mistakes_pos = (UI_MARGIN_LEFT + UI_INFO_SPACING * 2, UI_MARGIN_TOP)
            self.screen.blit(time_surface, time_pos); self.screen.blit(ink_surface, ink_pos); self.screen.blit(mistakes_surface, mistakes_pos)
        except Exception as e: print(f"Error rendering UI text: {e}")

    def _draw_messages(self, current_time):
         if not FONT_AVAILABLE: return
         message = None; is_final_state = False
         if self.game_state == STATE_GAME_OVER_TIME: message = "SÜRE DOLDU!"; is_final_state = True
         elif self.game_state == STATE_GAME_OVER_INK: message = "MÜREKKEP BİTTİ!"; is_final_state = True
         elif self.game_state == STATE_GAME_OVER_MISTAKES: message = "ÇOK FAZLA HATA!"; is_final_state = True
         elif self.game_state == STATE_GAME_COMPLETE: message = "TEBRİKLER! OYUN BİTTİ!"; is_final_state = True
         elif self.game_state == STATE_LEVEL_TRANSITION:
              if current_time - self.transition_timer_start < LEVEL_TRANSITION_DELAY - 300: message = f"SEVİYE {self.current_level_index} TAMAMLANDI!"
         if message:
             try:
                message_surface = self.font.render(message, True, COLOR_MESSAGE_TEXT); message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                bg_rect = message_rect.inflate(40, 20); bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surface.fill(COLOR_MESSAGE_BG)
                self.screen.blit(bg_surface, bg_rect.topleft); self.screen.blit(message_surface, message_rect)
                if is_final_state:
                     prompt_text = "Yeniden Başlamak İçin Tıkla"; prompt_surface = self.font.render(prompt_text, True, COLOR_UI_TEXT); prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, message_rect.bottom + 30))
                     self.screen.blit(prompt_surface, prompt_rect)
             except Exception as e: print(f"Error rendering message '{message}': {e}")

    def _draw(self):
        if self.background_image: self.screen.blit(self.background_image, (0, 0))
        else: self.screen.fill(COLOR_BACKGROUND)
        self._draw_grid_and_tiles(); self._draw_symmetry_line(); self._draw_ui(); self._draw_messages(pygame.time.get_ticks())
        pygame.display.flip()

    def _play_sound(self, name_key):
        if self.sound_enabled and name_key in self.sounds and self.sounds[name_key]:
            try: self.sounds[name_key].play()
            except pygame.error as e: print(f"Error playing sound '{name_key}': {e}")