import pygame
from src.settings import *
from src.ui.menu import Menu
from src.levels.level_manager import LevelManager
from src.core.util import event_handler, draw_frame

class Game:
    """Main game class managing states, levels, and menus."""
    def __init__(self):
        """Initialize Pygame, display, clock, and game state."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("I Wanna Study Computer Science") # Set a window title
        self.clock = pygame.time.Clock()
        print("Starting game...")

        self.current_state = GameState.MENU # Start in the menu

        self.font = pygame.font.SysFont(None, 74) # Fallback
        self.small_font = pygame.font.SysFont(None, 36)

        self.menu = Menu(self)
        self.level_manager = LevelManager(self) # Pass self to LevelManager

    def run(self):
        """Main game loop handling different states."""
        while True:
            # --- Event Handling ---
            events = pygame.event.get()
            for event in events:
                event_handler(event, self) # Handle events for the current state

            draw_frame(self) # Draw the current frame based on state
            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame
            self.clock.tick(FPS)