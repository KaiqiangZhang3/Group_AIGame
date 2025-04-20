import pygame
from src.settings import *
from src.ui.menu import Menu
from src.levels.level_manager import LevelManager
from src.core.util import events_handler, draw_frame

class Game:
    """Main game class managing states, levels, and menus."""
    def __init__(self):
        """Initialize Pygame, display, clock, and game state."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME) # Set a window title
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 74) # Fallback
        self.small_font = pygame.font.SysFont(None, 36)
        print("Starting game...")

        self.current_state = GameState.MENU # Start in the menu
        self.menu = Menu(self)
        self.level_manager = LevelManager(self) # Pass self to LevelManager

    def run(self):
        while True:
            # --- Event Handling ---
            events_handler(pygame.event.get(), self)
            draw_frame(self) # Draw the current frame based on state
            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame
            self.clock.tick(FPS)