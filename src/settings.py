# Proposed changes for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/settings.py
# Instruction: Add menu colors and basic font settings.

import pygame

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)        # Keep for menu highlight/errors
BLUE = (0, 0, 255)      # No longer used for platforms
GREEN = (0, 255, 0)      # Exit tiles
# LIGHT_GREY = (100, 100, 100) # Removed - Was for fancier menu background
SILVER = (192, 192, 192) # Traps
EARTH_BROWN = (139, 69, 19) # Platforms
LIGHT_PINK = (255, 182, 193) # Player
CHECKPOINT_YELLOW = (255, 255, 0) # Yellow for inactive checkpoints
CHECKPOINT_ACTIVE_BLUE = (0, 0, 255) # Blue for active checkpoints
SKY_BLUE = (135, 206, 235) # Added missing color

# Player settings
PLAYER_GRAVITY = 0.8
PLAYER_JUMP_STRENGTH = -16 # Increased initial jump height
PLAYER_DOUBLE_JUMP_STRENGTH = -13 # Increased strength of the second jump
PLAYER_SPEED = 5
PLAYER_DASH_SPEED = 15   # Speed during dash
PLAYER_DASH_DURATION = 8 # Duration of dash in frames
PLAYER_DASH_COOLDOWN = 30  # Cooldown period for dash in frames

# Moving Spike Settings
MOVING_SPIKE_SPEED = 2
MOVING_SPIKE_HORIZONTAL_RANGE = 3 # Number of tiles the spike moves left/right from its start

# Framerate
FPS = 60

# Fonts (Consider using a specific font file later)
MENU_FONT_SIZE = 50
MENU_FONT_COLOR = WHITE
MENU_FONT_HIGHLIGHT_COLOR = RED
