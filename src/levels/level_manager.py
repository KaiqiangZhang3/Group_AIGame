import os
from src.levels.level import Level
from src.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Group_AIGame directory
ASSETS_DIR = os.path.join(BASE_DIR, '..', 'assets')
LEVELS_DIR = os.path.join(ASSETS_DIR, 'levels')

LEVEL_MAPS = [
    os.path.join(LEVELS_DIR, 'level_1.txt'),
    os.path.join(LEVELS_DIR, 'level_2.txt'),
]

class LevelManager:
    """Manages the loading and switching of levels."""
    def __init__(self, game_instance):
        self.screen = game_instance.screen
        self.game = game_instance
        self.current_level_index = 0
        self.level = None

    def load_level(self, level_index):
        """Load a specific level by index."""
        if 0 <= level_index < len(LEVEL_MAPS):
            try:
                # Read the level layout from the file
                level_path = LEVEL_MAPS[level_index]
                with open(level_path, 'r') as file:
                    level_data = [line.strip('\n') for line in file.readlines()]

                # Create a Level instance
                self.level = Level(level_data, self.screen, self.game)
                self.current_level_index = level_index
                self.game.current_state = GameState.PLAYING  # Set game state to playing
                print(f"Level {level_index + 1} loaded successfully.")
                return self.level

            except FileNotFoundError:
                print(f"Error: Level file not found: {LEVEL_MAPS[level_index]}")
                raise
            except Exception as e:
                print(f"Error loading level {level_index + 1}: {e}")
                raise
        else:
            print("Invalid level index.")
            raise ValueError("Level index out of bounds.")

    def next_level(self):
        """Advance to the next level."""
        if self.current_level_index + 1 < len(LEVEL_MAPS):
            return self.load_level(self.current_level_index + 1)
        else:
            print("No more levels. Game completed!")
            self.game.current_state = GameState.GAME_OVER
            return None

    def reload_current_level(self):
        """Reload the current level."""
        return self.load_level(self.current_level_index)