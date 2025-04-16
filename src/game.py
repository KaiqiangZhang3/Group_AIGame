# Proposed changes for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/game.py
# Instruction: Manage multiple level files, load levels by index, and handle transitions via next_level callback.

import pygame
import sys
import os # Added for path joining
import json # Import json for saving/loading scores
from .settings import * # Import all settings
from .level import Level # Import Level class
# Assuming Menu class exists and is imported if needed
from .menu import Menu # Make sure menu.py exists and Menu class is defined

# Remove redundant path definitions - these should come from settings.py
# BASE_DIR = os.path.dirname(__file__) 
# LEVELS_DIR = os.path.join(BASE_DIR, '..', 'assets', 'levels') 
# HIDDEN_LEVEL_PATH = os.path.join(BASE_DIR, '..', 'assets', 'hidden_level.txt')


class Game:
    """Main game class managing states, levels, and menus."""
    def __init__(self):
        """Initialize Pygame, display, clock, and game state."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("I Wanna Study Computer Science") # Set a window title
        self.clock = pygame.time.Clock()
        print("Starting game...")

        # Game State Management
        # Define states
        self.MENU = 'menu'
        self.PLAYING = 'playing'
        self.SETTINGS = 'settings' # If you have a settings screen
        self.DEATH_SCREEN = 'death_screen' # New state
        self.GAME_OVER = 'game_over' # Optional: If all levels completed
        self.WIN = 'win' # New state
        self.RANKING = 'ranking' # New state for showing scores

        self.current_state = self.MENU # Start in the menu

        # Level Management
        self.current_level_index = 0
        self.return_level_index = None # Track which level to return to after hidden level
        self.level = None # No level loaded initially

        # Timer Management
        self.start_time = None
        self.end_time = None

        # Menu Management
        # Assuming Menu class is less relevant now and options are managed here
        self.menu_options = ['Start Game', 'Ranking', 'Settings', 'Exit'] # Add Ranking
        self.selected_option = 0
        self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE) # Use settings font size
        self.menu_rects = {} # Store rects for mouse interaction

        # Font for death screen (or use a dedicated font loader) - Reverted
        try:
            # Original font loading
            self.font = pygame.font.Font(None, 74) # Default font, size 74
            self.small_font = pygame.font.Font(None, 36) # Smaller font for options
        except Exception as e:
            print(f"Error loading font: {e}. Using default pygame font.")
            self.font = pygame.font.SysFont(None, 74) # Fallback
            self.small_font = pygame.font.SysFont(None, 36)


    def load_level(self, level_index):
        """Load a specific level by index."""
        if 0 <= level_index < len(LEVEL_MAPS):
            relative_path = LEVEL_MAPS[level_index]
            # Construct path relative to *this* file (game.py)
            # Go up one level from src (..) then combine with relative_path
            full_path = os.path.join(LEVELS_DIR, relative_path)

            print(f"Loading level {level_index + 1} from '{full_path}'...")
            try:
                # Read the level layout from the full path
                with open(full_path, 'r') as file:
                    level_data = [line.strip('\n') for line in file.readlines()]

                # Pass self (game instance) to Level constructor
                level_path = os.path.join(LEVELS_DIR, LEVEL_MAPS[level_index])
                self.level = Level(level_path, self.screen, self.next_level, self.show_death_screen, self.load_hidden_level, level_index)
                self.current_level_index = level_index
                self.current_state = self.PLAYING # Change state to playing
                print(f"Level {level_index + 1} loaded successfully.")

            except FileNotFoundError:
                print(f"Error: Level file not found: {full_path}")
                # Handle error - maybe return to menu or show error message
                self.return_to_menu()
            except Exception as e:
                print(f"Error loading level {level_index + 1}: {e}")
                self.return_to_menu()
        else:
            print("Attempted to load invalid level index or no more levels.")
            # Handle case where level index is out of bounds (e.g., finished last level)
            self.return_to_menu() # Or go to a "You Win" screen


    def load_hidden_level(self):
        """Loads the hidden level and stores the return level index."""
        if self.return_level_index is not None:
            print("Already in hidden level, cannot re-enter.")
            return # Prevent entering hidden level from hidden level
        
        print("Loading hidden level...")
        self.return_level_index = self.current_level_index + 1 # Store index of the next normal level
        self.level = Level(HIDDEN_LEVEL_PATH, self.screen, self.next_level, self.show_death_screen, self.load_hidden_level, -1) # Use -1 or similar to indicate hidden level
        self.current_state = self.PLAYING


    def next_level(self):
        """Advance to the next level or return to menu if last level completed."""
        print("Proceeding to next level...")
        if self.level:
            self.level.reset_checkpoints() # Reset checkpoints of the completed level
        if self.return_level_index is not None:
            next_index = self.return_level_index
            print(f"Returning from hidden level to level {next_index}...")
            self.return_level_index = None # Clear the return index
        else:
            next_index = self.current_level_index + 1
            print(f"Proceeding to level {next_index + 1}...")

        if next_index < len(LEVEL_MAPS):
            self.load_level(next_index)
        else:
            print("You beat all the levels!")
            # Potentially add a 'WIN' state or screen here
            if self.start_time is not None:
                self.end_time = pygame.time.get_ticks()
                elapsed_time_ms = self.end_time - self.start_time
                print(f"Game completed in {elapsed_time_ms / 1000.0:.2f} seconds.")
                self.save_score(elapsed_time_ms) # Call function to save score
            else:
                print("Timer was not started, cannot save score.")

            self.current_state = self.WIN # Change state to 'win' after last level
            self.level = None # Clear the level object


    def return_to_menu(self):
        """Return to the main menu."""
        print("Returning to menu...")
        if self.level:
             self.level.reset_checkpoints() # Reset checkpoints before leaving
             self.level = None # Unload the level
        self.current_level_index = 0 # Reset level index? Optional.
        self.current_state = self.MENU


    def show_death_screen(self):
        """Transition to the death screen state."""
        print("Showing death screen.")
        self.current_state = self.DEATH_SCREEN


    def draw_death_screen(self):
        """Draw the 'You Died' message and options.""" # Original docstring
        # Original black background
        self.screen.fill(BLACK)

        # Death message - Reverted font and layout
        death_text = self.font.render('ERROR: FAIL TO LOAD', True, RED)
        death_rect = death_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
        self.screen.blit(death_text, death_rect)

        # Respawn option - Reverted font and layout
        respawn_text = self.small_font.render('Press [R] to Respawn', True, WHITE)
        respawn_rect = respawn_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(respawn_text, respawn_rect)

        # Menu option - Reverted font and layout
        menu_text = self.small_font.render('Press [M] for Main Menu', True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        self.screen.blit(menu_text, menu_rect)

        # No flip here, it's handled in run()


    def draw_win_screen(self):
        """Draw the 'You Win!' message and options."""
        # Original black background
        self.screen.fill(BLACK)

        # Win message - Reverted font and layout
        win_text = self.font.render('You Graduate', True, GREEN)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
        self.screen.blit(win_text, win_rect)

        # Menu option - Reverted font and layout
        menu_text = self.small_font.render('Press [M] for Main Menu', True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        self.screen.blit(menu_text, menu_rect)

        # No flip here, it's handled in run()


    def load_scores(self):
        """Loads scores from the JSON file."""
        try:
            with open(SCORE_FILE_PATH, 'r') as f:
                scores = json.load(f)
            if isinstance(scores, list):
                 # Ensure scores are numbers (could add more validation)
                return [s for s in scores if isinstance(s, (int, float))]
            else:
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            return [] # Return empty list if file not found or invalid
        except Exception as e:
            print(f"Error loading scores for display: {e}")
            return []


    def draw_ranking_screen(self):
        """Draws the top 5 fastest times."""
        self.screen.fill(BLACK) # Or another background color

        # Title
        title_text = self.font.render('Fastest Times', True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        self.screen.blit(title_text, title_rect)

        # Load scores
        scores = self.load_scores()

        if not scores:
            no_scores_text = self.small_font.render('No scores recorded yet!', True, WHITE)
            no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            self.screen.blit(no_scores_text, no_scores_rect)
        else:
            # Display top 5 scores
            y_offset = SCREEN_HEIGHT / 2 - (len(scores) * 40) / 2 # Center the block
            for i, score_ms in enumerate(scores):
                 # Format time to seconds with 2 decimal places
                score_sec = score_ms / 1000.0
                score_str = f"{i + 1}. {score_sec:.2f} seconds"
                score_text = self.small_font.render(score_str, True, WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, y_offset + i * 40))
                self.screen.blit(score_text, score_rect)

        # Instructions to return
        menu_text = self.small_font.render('Press [M] or [ESC] for Main Menu', True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.85))
        self.screen.blit(menu_text, menu_rect)


    def run(self):
        """Main game loop handling different states."""
        while True:
            # --- Event Handling ---
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # --- State-Specific Event Handling ---
                if self.current_state == self.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if self.level and self.level.player:
                            player = self.level.player
                            if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                                player.jump()
                            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                                player.dash()
                            # Add other playing state keydowns if needed

                elif self.current_state == self.MENU:
                    # Pass events to the menu handler
                    self.handle_menu_input(event) # Call method directly on self

                elif self.current_state == self.DEATH_SCREEN:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: # Respawn
                            print("Respawn selected.")
                            if self.level:
                                self.level.reset_player_to_respawn()
                                self.current_state = self.PLAYING # Go back to playing
                            else: # Should not happen, but safety check
                                self.return_to_menu()
                        elif event.key == pygame.K_m: # Return to Menu
                            print("Return to Menu selected.")
                            self.return_to_menu() # Handles level cleanup and state change

                elif self.current_state == self.WIN:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m: # Return to Menu
                            print("Return to Menu selected.")
                            self.return_to_menu() # Handles level cleanup and state change

                elif self.current_state == self.RANKING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                            print("Return to Menu selected from Ranking.")
                            self.return_to_menu()

                # Add event handling for other states (SETTINGS, GAME_OVER) if they exist

            # --- Game Logic Update ---
            # Only update logic, not drawing here
            # if self.current_state == self.PLAYING:
            #     if self.level:
            #         self.level.run() # Update and draw level content -> MOVED TO DRAWING
            #     else:
            #         # Safety check: If in PLAYING state but no level, return to menu
            #         print("Warning: PLAYING state with no level loaded. Returning to menu.")
            #         self.return_to_menu()

            # --- Drawing ---
            # self.screen.fill(SKY_BLUE) # REMOVED - Let states draw their own background

            if self.current_state == self.MENU:
                self.draw_menu() # Call method directly on self
            elif self.current_state == self.PLAYING:
                if self.level:
                    # Pass dt to level's run method for updates
                    dt = self.clock.tick(FPS) / 1000.0 # Calculate dt here for PLAYING state
                    self.level.run(dt) 
                else:
                     # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.return_to_menu()
            elif self.current_state == self.DEATH_SCREEN:
                self.draw_death_screen()
            elif self.current_state == self.WIN:
                self.draw_win_screen()
            elif self.current_state == self.RANKING:
                self.draw_ranking_screen()
            # Add drawing for other states if they exist

            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame

            # Ensure clock ticks even if not in PLAYING state to maintain frame rate
            if self.current_state != self.PLAYING:
                 self.clock.tick(FPS) 


    def start_game(self):
        """Initialize the first level, reset timer, and switch state to PLAYING."""
        print("Starting game...") # Debug message
        self.current_level_index = 0 # Ensure we start at level 0
        self.start_time = pygame.time.get_ticks() # Record start time
        self.end_time = None # Reset end time
        self.load_level(0) # Load the first level (index 0)
        # State is set to PLAYING inside load_level


    def draw_menu(self):
        """Draw the main menu screen."""
        self.screen.fill(BLACK)
        title_font = pygame.font.SysFont(None, 80)
        title_surf = title_font.render("I Wanna Study Computer Science", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)

        # Draw menu options
        for i, option in enumerate(self.menu_options):
            color = MENU_FONT_HIGHLIGHT_COLOR if i == self.selected_option else MENU_FONT_COLOR
            text_surf = self.menu_font.render(option, True, color)
            # Position options vertically centered
            y_pos = SCREEN_HEIGHT // 2 + i * (MENU_FONT_SIZE + 20)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.menu_rects[option] = text_rect # Store rect for clicking
            self.screen.blit(text_surf, text_rect)


    def handle_menu_input(self, event):
         """Handle input events in the menu state."""
         if event.type == pygame.KEYDOWN:
             if event.key == pygame.K_UP or event.key == pygame.K_w:
                 self.selected_option = (self.selected_option - 1) % len(self.menu_options)
             elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                 self.selected_option = (self.selected_option + 1) % len(self.menu_options)
             elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                 self.select_menu_option()
         elif event.type == pygame.MOUSEBUTTONDOWN:
             # Check if mouse click is on any menu option
             mouse_pos = event.pos
             for option, rect in self.menu_rects.items():
                 if rect.collidepoint(mouse_pos):
                     self.selected_option = self.menu_options.index(option)
                     self.select_menu_option()
                     break # Exit loop once an option is clicked
         elif event.type == pygame.MOUSEMOTION:
             # Highlight option under mouse cursor
             mouse_pos = event.pos
             highlighted = False
             for i, option in enumerate(self.menu_options):
                 if option in self.menu_rects and self.menu_rects[option].collidepoint(mouse_pos):
                     self.selected_option = i
                     highlighted = True
                     break
             # Optional: De-select if mouse moves off all options (could also keep last highlighted)
             # if not highlighted:
             #     pass # Keep current selection or reset


    def select_menu_option(self):
        """Execute action based on selected menu option."""
        selected = self.menu_options[self.selected_option]
        if selected == "Start Game":
            self.start_game()
        elif selected == "Ranking":
            print("Ranking selected.")
            self.current_state = self.RANKING # Change state to show rankings
        elif selected == "Settings":
            print("Settings selected (Not implemented yet)") # Placeholder
            # Could switch to a SETTINGS state here later
        elif selected == "Exit":
            pygame.quit()
            sys.exit()


    def save_score(self, time_ms):
        """Loads existing scores, adds the new score, sorts, keeps top 5, and saves back to the file."""
        scores = []
        try:
            # Try to load existing scores
            with open(SCORE_FILE_PATH, 'r') as f:
                scores = json.load(f)
            if not isinstance(scores, list): # Basic validation
                print(f"Warning: Score file {SCORE_FILE_PATH} contained invalid data. Resetting scores.")
                scores = []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # If file not found or invalid JSON, start with an empty list
            print(f"Info: Score file {SCORE_FILE_PATH} not found or invalid ({e}). Creating new one.")
            scores = []
        except Exception as e:
             print(f"Error loading scores: {e}")
             # Decide how to handle unexpected errors, maybe return without saving
             return

        # Add the new score (time in milliseconds)
        scores.append(time_ms)

        # Sort scores - fastest times first (ascending)
        scores.sort()

        # Keep only the top 5 scores
        top_scores = scores[:5]

        try:
            # Save the top scores back to the file
            with open(SCORE_FILE_PATH, 'w') as f:
                json.dump(top_scores, f, indent=4) # Use indent for readability
            print(f"Score {time_ms}ms saved successfully. Top scores: {top_scores}")
        except IOError as e:
            print(f"Error saving scores to {SCORE_FILE_PATH}: {e}")
        except Exception as e:
             print(f"Unexpected error saving scores: {e}")


    def show_death_screen(self):
        """Transition to the death screen state."""
        print("Showing death screen.")
        self.current_state = self.DEATH_SCREEN


    def run(self):
        """Main game loop handling different states."""
        while True:
            # --- Event Handling ---
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # --- State-Specific Event Handling ---
                if self.current_state == self.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if self.level and self.level.player:
                            player = self.level.player
                            if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                                player.jump()
                            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                                player.dash()
                            # Add other playing state keydowns if needed

                elif self.current_state == self.MENU:
                    # Pass events to the menu handler
                    self.handle_menu_input(event) # Call method directly on self

                elif self.current_state == self.DEATH_SCREEN:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: # Respawn
                            print("Respawn selected.")
                            if self.level:
                                self.level.reset_player_to_respawn()
                                self.current_state = self.PLAYING # Go back to playing
                            else: # Should not happen, but safety check
                                self.return_to_menu()
                        elif event.key == pygame.K_m: # Return to Menu
                            print("Return to Menu selected.")
                            self.return_to_menu() # Handles level cleanup and state change

                elif self.current_state == self.WIN:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m: # Return to Menu
                            print("Return to Menu selected.")
                            self.return_to_menu() # Handles level cleanup and state change

                elif self.current_state == self.RANKING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                            print("Return to Menu selected from Ranking.")
                            self.return_to_menu()

                # Add event handling for other states (SETTINGS, GAME_OVER) if they exist

            # --- Game Logic Update ---
            # Only update logic, not drawing here
            # if self.current_state == self.PLAYING:
            #     if self.level:
            #         self.level.run() # Update and draw level content -> MOVED TO DRAWING
            #     else:
            #         # Safety check: If in PLAYING state but no level, return to menu
            #         print("Warning: PLAYING state with no level loaded. Returning to menu.")
            #         self.return_to_menu()

            # --- Drawing ---
            # self.screen.fill(SKY_BLUE) # REMOVED - Let states draw their own background

            if self.current_state == self.MENU:
                self.draw_menu() # Call method directly on self
            elif self.current_state == self.PLAYING:
                if self.level:
                    # Pass dt to level's run method for updates
                    dt = self.clock.tick(FPS) / 1000.0 # Calculate dt here for PLAYING state
                    self.level.run(dt) 
                else:
                     # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.return_to_menu()
            elif self.current_state == self.DEATH_SCREEN:
                self.draw_death_screen()
            elif self.current_state == self.WIN:
                self.draw_win_screen()
            elif self.current_state == self.RANKING:
                self.draw_ranking_screen()
            # Add drawing for other states if they exist

            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame

            # Ensure clock ticks even if not in PLAYING state to maintain frame rate
            if self.current_state != self.PLAYING:
                 self.clock.tick(FPS) 
