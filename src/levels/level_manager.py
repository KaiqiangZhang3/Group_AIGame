import os
from src.levels.level import Level
from src.levels.level_data import ROOT_LEVEL
from src.settings import *

class LevelManager:
    """Manages the loading and switching of levels."""
    def __init__(self, game_instance):
        self.screen = game_instance.screen
        self.game = game_instance
        self.current_level_data = ROOT_LEVEL
        self.level = None
        self.next = None
        self.hidden = None

    def load_level(self, level_data):
        """Load a specific level by index."""
        level_layout = level_data.layout
        self.next = level_data.next_level
        self.hidden = level_data.hidden_level

        # Create a Level instance
        self.level = Level(level_layout, self.screen, self.game)
        self.current_level_data = level_data
        self.game.current_state = GameState.PLAYING  # Set game state to playing
        print(f"Level {level_data.name} loaded successfully.")
        return self.level


    def next_level(self):
        """Advance to the next level."""
        if not self.next:
            self.game.current_state = GameState.GAME_OVER
            return None
        return self.load_level(self.next)
    
    def hidden_level(self):
        """Load the hidden level."""
        return self.load_level(self.hidden)

    def reload_current_level(self):
        """Reload the current level."""
        return self.load_level(self.current_level_data)

    def game_entry(self):
        """Entry point for the game."""
        self.load_level(ROOT_LEVEL)