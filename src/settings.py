from enum import Enum, auto
import os

GAME_NAME = "I Wanna Study Computer Science"

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
PLAYER_COLOR = (255, 255, 0) # Player is now yellow
PLAYER_GLOW_COLOR = (255, 255, 150) # Soft yellow glow (RGB only, Alpha will be dynamic)
CHECKPOINT_YELLOW = (255, 255, 0) # Yellow for inactive checkpoints
CHECKPOINT_ACTIVE_BLUE = (0, 0, 255) # Blue for active checkpoints
SKY_BLUE = (135, 206, 235) # Added missing color

# Game States Enum
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    SETTINGS = auto() # Placeholder if needed
    DEATH_SCREEN = auto()
    GAME_OVER = auto() # Optional: If all levels completed

# Player setting
ACELERATION_FRAME = 6 # Frames to reach max speed
DECELERATION_FRAME = 3 # Frames to stop from max speed
CLIMBING_JUMP_FRAME = 6
PLAYER_GRAVITY = 0.6
JUMP_TOLERANCE_FRAME = 6
PLAYER_JUMP_STRENGTH = -11 # Increased initial jump height
PLAYER_DOUBLE_JUMP_STRENGTH_RATE = 0.8
PLAYER_SPEED = 7
PLAYER_SUPER_JUMP_STRENGTH_RATE = 1.5
PLAYER_DASH_PREPARE_FRAMES = 5 # Frames before dash to prepare
PLAYER_DASH_SPEED = 20   # Speed during dash
PLAYER_DASH_DURATION = 13 # Duration of dash in frames
PLAYER_DASH_COOLDOWN = 30  # Cooldown period for dash in frames
PLAYER_LIGHT_BASE_RADIUS = 60 # Base radius of the player's light glow
PLAYER_LIGHT_PULSE_AMPLITUDE = 15 # How much the radius changes from base
PLAYER_LIGHT_PULSE_SPEED = 1.5    # Speed of the pulsing (higher is faster)
PLAYER_LIGHT_MIN_ALPHA = 70       # Minimum alpha for the glow during pulse
PLAYER_LIGHT_MAX_ALPHA = 170      # Maximum alpha for the glow during pulse
DARKNESS_COLOR = (0, 0, 0, 255)     # RGBA for the darkness overlay (fully opaque black)
PLAYER_MASK_BRUSH_COLOR = (255, 255, 255) # White color for the mask brush surface

# Moving Spike Settings
MOVING_SPIKE_SPEED = 2
MOVING_SPIKE_HORIZONTAL_RANGE = 3 # Number of tiles the spike moves left/right from its start

# Framerate
FPS = 60

# --- Calculate Project Root based on settings.py location ---
# Path to the directory containing settings.py (src/)
_SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the project root (one level up from _SETTINGS_DIR)
_PROJECT_ROOT = os.path.dirname(_SETTINGS_DIR)
# ------------------------------------------------------------

# --- Asset Paths (NEW) ---
ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
# Example: ELEGANT_FONT_NAME = "Quicksand-Regular.ttf" # Replace with your font file
ELEGANT_FONT_NAME = None # Set to a font file name like "YourFont.ttf"
ELEGANT_FONT_PATH = os.path.join(FONTS_DIR, ELEGANT_FONT_NAME) if ELEGANT_FONT_NAME else None
# --------------------------

# Fonts (Consider using a specific font file later)
MENU_FONT_SIZE = 50
MENU_FONT_COLOR = WHITE
MENU_FONT_HIGHLIGHT_COLOR = RED # Kept for old menu style if needed, or for other UI

# --- New Minimalist Menu Settings (NEW) ---
ELEGANT_FONT_SIZE = 48
MINIMAL_MENU_BACKGROUND_COLOR = (30, 30, 40)   # Dark cool grey/blue
MINIMAL_MENU_TEXT_COLOR = (220, 220, 230) # Light grey/lavender
MINIMAL_MENU_HIGHLIGHT_COLOR = (255, 255, 255) # Bright white for selected
MINIMAL_MENU_GLOW_COLOR = (180, 180, 220, 100) # Semi-transparent lavender for glow (R,G,B,Alpha)

# --- New Atmospheric Background Settings (NEW) ---
GRADIENT_TOP_COLOR = (20, 20, 60)   # Deep blue
GRADIENT_BOTTOM_COLOR = (60, 20, 80)  # Dark purple
FIREFLY_COLOR = (255, 255, 150)      # Soft yellow for fireflies
FIREFLY_GLOW_COLOR = (200, 200, 100, 70) # Glow for fireflies (R,G,B,Alpha)

# --- Parallax Scrolling Settings (NEW) ---
BACKGROUND_GLOBAL_DRIFT_X = 0.05 # Very slow global horizontal drift speed
MIST_PARALLAX_FACTOR = 0.3       # Mist moves at 30% of global drift
FIREFLY_PARALLAX_FACTOR = 0.7    # Fireflies move at 70% of global drift
# -----------------------------------------

# Voice Command Constants for Input Buffer
VOICE_COMMAND_JUMP = "VOICE_JUMP"

# Voice Recognition (Vosk) Settings
# IMPORTANT: Download a Vosk model (e.g., vosk-model-small-en-us-0.15)
# from https://alphacephei.com/vosk/models, unzip it, and update this path.
# Example: If unzipped to project root -> "vosk-model-small-en-us-0.15"
_VOSK_MODEL_FOLDER_NAME = "vosk-model-small-en-us-0.15"
VOSK_MODEL_PATH = os.path.join(_PROJECT_ROOT, _VOSK_MODEL_FOLDER_NAME)

VOSK_SAMPLE_RATE = 16000  # Common sample rate for Vosk models
VOSK_CHANNELS = 1         # Mono audio
# Optional: Specify microphone device ID if the default is not correct.
# Run voice_recognizer.py directly (once model path is set) to see available devices if needed.
VOSK_DEVICE_ID = None     # None for default device, or an integer device ID

# Voice Recognition Toggle Setting
VOICE_RECOGNITION_ENABLED_BY_DEFAULT = True
