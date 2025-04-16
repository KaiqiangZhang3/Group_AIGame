# Proposed changes for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/settings.py
# Instruction: Add menu colors and basic font settings.

import pygame
import os

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)      # Exit tiles
RED = (255, 0, 0)        # Keep for menu highlight/errors
BLUE = (0, 0, 255)      # No longer used for platforms
PURPLE = (128, 0, 128) # For hidden door
# LIGHT_GREY = (100, 100, 100) # Removed - Was for fancier menu background
SILVER = (192, 192, 192) # Traps
EARTH_BROWN = (139, 69, 19) # Platforms
LIGHT_PINK = (255, 182, 193) # Player
CHECKPOINT_YELLOW = (255, 255, 0) # Yellow for inactive checkpoints
CHECKPOINT_ACTIVE_BLUE = (0, 0, 255) # Blue for active checkpoints
SKY_BLUE = (135, 206, 235) # Added missing color

# Define the base directory of the project (Group_AIGame)
# This assumes settings.py is in the src directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # Goes up one level from src

# Player settings
PLAYER_GRAVITY = 0.8
PLAYER_JUMP_STRENGTH = -16 # Increased initial jump height
PLAYER_DOUBLE_JUMP_STRENGTH = -13 # Increased strength of the second jump
PLAYER_SPEED = 5
PLAYER_DASH_SPEED = 15   # Speed during dash
PLAYER_DASH_DURATION = 8 # Duration of dash in frames
PLAYER_DASH_COOLDOWN = 60 # Frames (1 second at 60 FPS)

# -- Bullet Settings --
BULLET_SPEED = 10
BULLET_COLOR = (192, 192, 192) # Silver
PLAYER_SHOOT_COOLDOWN = 15 # Frames (e.g., 4 shots/sec at 60 FPS)

# Moving Spike Settings
MOVING_SPIKE_SPEED = 2
MOVING_SPIKE_HORIZONTAL_RANGE = 3 # Number of tiles the spike moves left/right from its start

# Framerate
FPS = 60

# Fonts (Consider using a specific font file later)
MENU_FONT_SIZE = 50
MENU_FONT_COLOR = WHITE
MENU_FONT_HIGHLIGHT_COLOR = RED

# Levels directory
LEVELS_DIR = os.path.join(BASE_DIR, 'assets', 'levels') # Corrected from 'assets'
HIDDEN_LEVEL_PATH = os.path.join(LEVELS_DIR, 'level_hidden.txt')

# Score file
SCORE_FILE_PATH = os.path.join(BASE_DIR, 'scores.json')

# Level maps (using absolute paths based on BASE_DIR)
LEVEL_MAPS = [
    os.path.join(LEVELS_DIR, 'level_1.txt'),
    os.path.join(LEVELS_DIR, 'level_2.txt'),
    os.path.join(LEVELS_DIR, 'level_3.txt'), 
    os.path.join(LEVELS_DIR, 'level_4.txt'), 
    os.path.join(LEVELS_DIR, 'level_5.txt'), 
    os.path.join(LEVELS_DIR, 'level_6.txt'), 
    os.path.join(LEVELS_DIR, 'level_7.txt')  
]
