# Proposed content for: /Users/kaiqiangzhang/3_game/Group_AIGame/main.py
# Instruction: Update main.py to simply instantiate and run the Game class.

import pygame
from src.core.game import Game # Correct import assuming game.py is in src
import sys # Import sys for clean exit

def main():
    """Initialize and run the game."""
    # Pygame initialization is now handled within Game.__init__
    game = Game()
    game.run()
    # Pygame quit is handled within game loop on QUIT event or sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()
 