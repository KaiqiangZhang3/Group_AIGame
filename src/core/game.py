import pygame
import sys
import os
from src.settings import *
from src.levels.level import Level
from src.ui.menu import Menu
from src.levels.level_manager import LevelManager

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

        self.level_manager = LevelManager(self) # Pass self to LevelManager

    def respawn(self):
        """Respawns the player at the last checkpoint."""
        print("Respawn selected.")
        if self.level_manager.level:
            self.level_manager.level.reset_player_to_respawn()
            self.current_state = GameState.PLAYING # Use Enum member
        else: # Should not happen, but safety check
            print("Error: Cannot respawn, no level loaded.")
            self.menu.return_to_menu()

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
                self.level_manager.level.player.one_time_input(event) # Assuming player has one_time_input method
            case _:
                self.menu.handle_input(event) # Assuming Menu has handle_input

    def draw_frame(self):
        """Draw a single frame of the game."""
        match self.current_state:
            case GameState.MENU: # Use Enum member
                self.menu.draw_menu() # Placeholder call
            case GameState.PLAYING: # Use Enum member
                if self.level_manager.level:
                    self.level_manager.level.run() # Update logic AND draw level content here
                else:
                    # Safety check: If in PLAYING state but no level, return to menu
                    print("Warning: PLAYING state with no level loaded. Returning to menu.")
                    self.menu.return_to_menu()
            case GameState.DEATH_SCREEN: # Use Enum member
                self.menu.draw_death_screen() # Placeholder call
            case GameState.GAME_OVER: # Use Enum member
                self.menu.draw_game_over_screen() # Placeholder call
            case _:
                print("Unknown game state. Returning to menu.")
                self.menu.return_to_menu()