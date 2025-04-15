# Proposed changes for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/game.py
# Instruction: Manage multiple level files, load levels by index, and handle transitions via next_level callback.

import pygame
import sys
import os # Added for path joining
from .settings import * # Import all settings
from .level import Level # Import Level class
# Assuming Menu class exists and is imported if needed
from .menu import Menu # Make sure menu.py exists and Menu class is defined

# Define path to levels directory relative to this file's directory
BASE_DIR = os.path.dirname(__file__) # Gets the directory of game.py (src)
LEVELS_DIR = os.path.join(BASE_DIR, '..', 'asserts', 'levels')
LEVEL_MAPS = [
    os.path.join(LEVELS_DIR, 'level_1.txt'),
    os.path.join(LEVELS_DIR, 'level_2.txt'),
    # Add more level file paths here later
]


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

        self.current_state = self.MENU # Start in the menu

        # Level Management
        self.current_level_index = 0
        self.level = None # No level loaded initially

        # Menu Management (Assuming a Menu class exists)
        # Pass self to Menu if it needs to change game state
        self.menu = Menu(self.screen, self)

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
            print(f"Loading level {level_index + 1}...")
            try:
                # Read the level layout from the file
                with open(LEVEL_MAPS[level_index], 'r') as file:
                    level_data = [line.strip('\n') for line in file.readlines()]

                # Pass self (game instance) to Level constructor
                self.level = Level(level_data, self.screen, self)
                self.current_level_index = level_index
                self.current_state = self.PLAYING # Change state to playing
                print(f"Level {level_index + 1} loaded successfully.")

            except FileNotFoundError:
                print(f"Error: Level file not found: {LEVEL_MAPS[level_index]}")
                # Handle error - maybe return to menu or show error message
                self.return_to_menu()
            except Exception as e:
                print(f"Error loading level {level_index + 1}: {e}")
                self.return_to_menu()
        else:
            print("Attempted to load invalid level index or no more levels.")
            # Handle case where level index is out of bounds (e.g., finished last level)
            self.return_to_menu() # Or go to a "You Win" screen


    def next_level(self):
        """Advance to the next level or return to menu if last level completed."""
        print("Proceeding to next level...")
        if self.level:
            self.level.reset_checkpoints() # Reset checkpoints of the completed level
        next_index = self.current_level_index + 1
        if next_index < len(LEVEL_MAPS):
            self.load_level(next_index)
        else:
            print("All levels completed!")
            # Optional: Transition to a GAME_OVER state or win screen
            self.return_to_menu() # For now, return to menu


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
        death_text = self.font.render('You Died!', True, RED)
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
                    self.menu.handle_input(event) # Assuming Menu has handle_input

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
                self.menu.draw() # Assuming Menu has draw method
            elif self.current_state == self.PLAYING:
                if self.level:
                    self.level.run() # Update logic AND draw level content here
                else:
                     # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.return_to_menu()
            elif self.current_state == self.DEATH_SCREEN:
                self.draw_death_screen()
            # Add drawing for other states if they exist

            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame

            self.clock.tick(FPS)


    def start_game(self):
        """Initialize the first level and switch state to PLAYING."""
        print("Starting game...") # Debug message
        self.load_level(0) # Load the first level (index 0)
        self.game_state = 'PLAYING'


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
        elif selected == "Settings":
            print("Settings selected (Not implemented yet)") # Placeholder
            # Could switch to a SETTINGS state here later
        elif selected == "Exit":
            pygame.quit()
            sys.exit()


    def next_level(self):
        """Callback function to advance to the next level."""
        print("Level Complete!")
        next_index = self.current_level_index + 1
        if next_index < len(LEVEL_MAPS):
            self.load_level(next_index)
        else:
            print("You beat all the levels!")
            # Potentially add a 'WIN' state or screen here
            self.return_to_menu() # Return to menu for now
            self.level = None # Clear the level object


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
                    self.menu.handle_input(event) # Assuming Menu has handle_input

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
                self.menu.draw() # Assuming Menu has draw method
            elif self.current_state == self.PLAYING:
                if self.level:
                    self.level.run() # Update logic AND draw level content here
                else:
                     # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.return_to_menu()
            elif self.current_state == self.DEATH_SCREEN:
                self.draw_death_screen()
            # Add drawing for other states if they exist

            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame

            self.clock.tick(FPS)
