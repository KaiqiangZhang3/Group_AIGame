import pygame
import sys
import os
from src.settings import *
from src.levels.level import Level
from src.ui.menu import Menu

# Define path to levels directory relative to this file's directory
BASE_DIR = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(BASE_DIR, '..', '..', 'assets', 'levels')
LEVEL_MAPS = [
    os.path.join(LEVELS_DIR, 'level_1.txt'),
    os.path.join(LEVELS_DIR, 'level_2.txt'),
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

        # Font for death screen (or use a dedicated font loader) - Reverted
        try:
            # Original font loading
            self.font = pygame.font.Font(None, 74) # Default font, size 74
            self.small_font = pygame.font.Font(None, 36) # Smaller font for options
        except Exception as e:
            print(f"Error loading font: {e}. Using default pygame font.")
            self.font = pygame.font.SysFont(None, 74) # Fallback
            self.small_font = pygame.font.SysFont(None, 36)
                # Menu Management (Assuming a Menu class exists)
        # Pass self to Menu if it needs to change game state
        self.menu = Menu(self)

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

    def respawn(self):
        """Respawns the player at the last checkpoint."""
        print("Respawn selected.")
        if self.level:
            self.level.reset_player_to_respawn()
            self.current_state = GameState.PLAYING # Use Enum member
        else: # Should not happen, but safety check
            print("Error: Cannot respawn, no level loaded.")
            self.return_to_menu()

    def run(self):
        """Main game loop handling different states."""
        while True:
            # --- Event Handling ---
            events = pygame.event.get()
            for event in events:
                self.event_handler(event) # Handle events for the current state

            self.draw_frame() # Draw the current frame based on state
            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame
            self.clock.tick(FPS)

    def event_handler(self, event):
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                sys.exit()
            case pygame.KEYDOWN:
                self.keyboard_handler(event) # Handle keyboard events
            case _:
                pass

    def keyboard_handler(self, event):
        match self.current_state:
            case GameState.PLAYING: # Use Enum member
                self.level.player.one_time_input(event) # Assuming player has one_time_input method
            case _:
                self.menu.handle_input(event) # Assuming Menu has handle_input

    def draw_frame(self):
        """Draw a single frame of the game."""
        match self.current_state:
            case GameState.MENU: # Use Enum member
                self.menu.draw_menu() # Placeholder call
            case GameState.PLAYING: # Use Enum member
                if self.level:
                    self.level.run() # Update logic AND draw level content here
                else:
                    # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.return_to_menu()
            case GameState.DEATH_SCREEN: # Use Enum member
                self.menu.draw_death_screen() # Placeholder call
            case GameState.GAME_OVER: # Use Enum member
                self.menu.draw_game_over_screen() # Placeholder call
            case _:
                print("Unknown game state. Returning to menu.")
                self.return_to_menu()