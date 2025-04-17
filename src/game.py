# Proposed changes for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/game.py
# Instruction: Manage multiple level files, load levels by index, and handle transitions via next_level callback.

import pygame
import sys
import os # Added for path joining
from .settings import * # Import all settings, including GameState Enum
from .level import Level # Import Level class
# Assuming Menu class exists and is imported if needed
from .menu import Menu # Make sure menu.py exists and Menu class is defined

# Define path to levels directory relative to this file's directory
BASE_DIR = os.path.dirname(__file__) # Gets the directory of game.py (src)
LEVELS_DIR = os.path.join(BASE_DIR, '..', 'assets', 'levels')
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
        self.current_state = GameState.MENU # Start in the menu

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
                self.current_state = GameState.PLAYING # Use Enum member
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
            self.current_state = GameState.GAME_OVER # Use Enum member
            self.level = None # Clear the level object


    def return_to_menu(self):
        """Return to the main menu."""
        print("Returning to menu...")
        if self.level:
             self.level.reset_checkpoints() # Reset checkpoints before leaving
             self.level = None # Unload the level
        self.current_level_index = 0 # Reset level index? Optional.
        self.current_state = GameState.MENU # Use Enum member


    def show_death_screen(self):
        """Transition to the death screen state."""
        print("Showing death screen.")
        self.current_state = GameState.DEATH_SCREEN # Use Enum member


    def respawn(self):
        """Respawns the player at the last checkpoint."""
        print("Respawn selected.")
        if self.level:
            self.level.reset_player_to_respawn()
            self.current_state = GameState.PLAYING # Use Enum member
        else: # Should not happen, but safety check
            print("Error: Cannot respawn, no level loaded.")
            self.return_to_menu()


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
                if self.current_state == GameState.PLAYING: # Use Enum member
                    if event.type == pygame.KEYDOWN:
                        if self.level and self.level.player:
                            player = self.level.player
                            if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                                player.jump()
                            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                                player.dash()
                            # Add other playing state keydowns if needed

                elif self.current_state == GameState.MENU: # Use Enum member
                    # Pass events to the menu handler
                    self.menu.handle_input(event) # Assuming Menu has handle_input

                elif self.current_state == GameState.DEATH_SCREEN: # Use Enum member
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: # Respawn
                            self.respawn()
                        elif event.key == pygame.K_m: # Return to Menu
                            self.return_to_menu() # Handles level cleanup and state change

                elif self.current_state == GameState.GAME_OVER: # Use Enum member
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m or event.key == pygame.K_ESCAPE: # Return to Menu
                            self.return_to_menu()

                # Add event handling for other states (SETTINGS) if they exist

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

            if self.current_state == GameState.MENU: # Use Enum member
                self.draw_menu() # Placeholder call
            elif self.current_state == GameState.PLAYING: # Use Enum member
                if self.level:
                    self.level.run() # Update logic AND draw level content here
                else:
                     # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.return_to_menu()
            elif self.current_state == GameState.DEATH_SCREEN: # Use Enum member
                self.draw_death_screen() # Placeholder call
            elif self.current_state == GameState.GAME_OVER: # Use Enum member
                self.draw_game_over_screen() # Placeholder call
            # Add drawing for other states if they exist

            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame

            self.clock.tick(FPS)


    # --- Placeholder Draw Methods (Replace with actual Menu class calls later) --- 
    def draw_menu(self):
        self.screen.fill(BLACK)
        title_text = self.font.render('Main Menu', True, WHITE)
        start_text = self.small_font.render('Press ENTER to Start', True, WHITE)
        quit_text = self.small_font.render('Press ESC to Quit', True, WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))
        self.screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
        self.screen.blit(quit_text, quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))

    def draw_death_screen(self):
        self.screen.fill(BLACK)
        death_text = self.font.render('You Died!', True, RED)
        respawn_text = self.small_font.render('Press [R] to Respawn', True, WHITE)
        menu_text = self.small_font.render('Press [M] for Main Menu', True, WHITE)
        self.screen.blit(death_text, death_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))
        self.screen.blit(respawn_text, respawn_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
        self.screen.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))

    def draw_game_over_screen(self):
        self.screen.fill(BLACK)
        over_text = self.font.render('All Levels Complete!', True, GREEN)
        menu_text = self.small_font.render('Press [M] for Main Menu', True, WHITE)
        self.screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))
        self.screen.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

    def start_game(self):
        """Initialize the first level and switch state to PLAYING."""
        print("Starting game...") # Debug message
        self.load_level(0) # Load the first level (index 0)
        # State is set to PLAYING inside load_level
