import pygame
import os
from src.settings import TILE_SIZE, EARTH_BROWN, SILVER, GREEN, CHECKPOINT_YELLOW, CHECKPOINT_ACTIVE_BLUE # Keep GREEN for fallback

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
            case _: # Default or unknown type
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                self.image.fill(EARTH_BROWN) # Default to Earth Brown

        self.rect = self.image.get_rect(topleft=pos)

    def activate(self):
        """Activate the checkpoint (visually)."""
        if self.tile_type == 'checkpoint' and not self.is_active:
            self.is_active = True
            self.image.fill(CHECKPOINT_ACTIVE_BLUE) # Change to blue when active
            # Add any other visual change if needed
