import pygame
import os
from src.settings import TILE_SIZE, EARTH_BROWN, SILVER, GREEN, CHECKPOINT_YELLOW, CHECKPOINT_ACTIVE_BLUE, TEMP_PLATFORM_COLOR, TEMP_PLATFORM_FADING_COLOR, TEMP_PLATFORM_DURATION_S, PERIODIC_PLATFORM_VISIBLE_S, PERIODIC_PLATFORM_INVISIBLE_S, PERIODIC_PLATFORM_COLOR # Keep GREEN for fallback

# Construct the path relative to the tile.py file
# Go up one level from src (..) to the project root, then down into assets/images
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # Gets the Group_AIGame directory
DOOR_IMAGE_PATH = os.path.join(BASE_DIR, '..', 'assets', 'images', '—Pngtree—vector painted open door_2570210.png')

class Tile(pygame.sprite.Sprite):
    """Represents a static tile in the game world (platform, trap, exit, checkpoint)."""
    def __init__(self, pos, groups, tile_type='platform'):
        super().__init__(groups)
        self.tile_type = tile_type
        self.is_active = False # Relevant for checkpoints

        # Temporary platform specific attributes
        self.timer_active = False
        self.time_left_s = TEMP_PLATFORM_DURATION_S

        # Determine image based on type
        match self.tile_type:
            case 'platform':
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                self.image.fill(EARTH_BROWN)
            case 'trap':
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA) # Use SRCALPHA for transparency
                self.image.fill((0,0,0,0)) # Transparent background
                pygame.draw.polygon(self.image, SILVER, [(0, TILE_SIZE), (TILE_SIZE // 2, 0), (TILE_SIZE, TILE_SIZE)])
            case 'exit':
                # Load the image HERE, inside init, after pygame.display is initialized
                try:
                    raw_door_image = pygame.image.load(DOOR_IMAGE_PATH).convert_alpha()
                    self.image = pygame.transform.scale(raw_door_image, (TILE_SIZE, TILE_SIZE))
                    # Optional: print success only once or remove if too noisy
                    # print(f"Loaded door image for tile at {pos}")
                except pygame.error as e:
                    print(f"Warning: Failed to load door image from {DOOR_IMAGE_PATH}. Error: {e}")
                    print(f"Falling back to green square for exit tile at {pos}.")
                    # Fallback to green square if image loading failed
                    self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    self.image.fill(GREEN)
            case 'checkpoint': # Handle checkpoint type
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                # Draw a simple flag or just color for now
                self.image.fill(CHECKPOINT_YELLOW) # Start yellow (inactive)
                # Could add more detail like a small rectangle post
                # pygame.draw.rect(self.image, BLACK, (TILE_SIZE // 2 - 2, TILE_SIZE // 2, 4, TILE_SIZE // 2)) # Example post
            case 'temp_platform':
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                self.image.fill(TEMP_PLATFORM_COLOR)
            case 'periodic_platform':
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA) # Support alpha for transparency
                self.image.fill(PERIODIC_PLATFORM_COLOR)
                self.is_currently_visible = True # Start visible
                self.cycle_timer_s = PERIODIC_PLATFORM_VISIBLE_S
            case _: # Default or unknown type
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                self.image.fill(EARTH_BROWN) # Default to Earth Brown

        self.rect = self.image.get_rect(topleft=pos)

    def activate(self):
        """Activate the checkpoint (visually)."""
        if self.tile_type == 'checkpoint' and not self.is_active:
            self.is_active = True
            self.is_active = True
            self.image.fill(CHECKPOINT_ACTIVE_BLUE) # Change to blue when active
            # Add any other visual change if needed

    def activate_timer(self):
        """Activates the timer for a temporary platform."""
        if self.tile_type == 'temp_platform' and not self.timer_active:
            self.timer_active = True
            self.image.fill(TEMP_PLATFORM_FADING_COLOR) # Change color to indicate it's active

    def update(self, dt):
        """Update tile state, e.g., for temporary platforms."""
        if self.tile_type == 'temp_platform' and self.timer_active:
            self.time_left_s -= dt
            if self.time_left_s <= 0:
                self.kill() # Remove the tile from all groups
        elif self.tile_type == 'periodic_platform':
            self.cycle_timer_s -= dt
            if self.cycle_timer_s <= 0:
                self.is_currently_visible = not self.is_currently_visible
                if self.is_currently_visible:
                    self.cycle_timer_s = PERIODIC_PLATFORM_VISIBLE_S
                    self.image.set_alpha(255) # Opaque
                else:
                    self.cycle_timer_s = PERIODIC_PLATFORM_INVISIBLE_S
                    self.image.set_alpha(0) # Transparent

    def reset_timer(self):
        """Resets a temporary platform to its initial state."""
        if self.tile_type == 'temp_platform':
            self.timer_active = False
            self.time_left_s = TEMP_PLATFORM_DURATION_S
            self.image.fill(TEMP_PLATFORM_COLOR)
            # The Level class will handle re-adding to sprite groups if it was killed.
