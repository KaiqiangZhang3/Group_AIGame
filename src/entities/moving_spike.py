import pygame
from src.settings import TILE_SIZE, MOVING_SPIKE_SPEED, MOVING_SPIKE_HORIZONTAL_RANGE, SILVER

class MovingSpike(pygame.sprite.Sprite):
    """Represents a spike trap that moves horizontally."""
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE // 2)) # Make spikes shorter like traps
        self.image.fill(SILVER)
        # Adjust rect position to sit on top of the platform tile visually
        self.rect = self.image.get_rect(midbottom = (pos[0] + TILE_SIZE // 2, pos[1] + TILE_SIZE))

        self.start_x = self.rect.centerx
        self.min_x = self.start_x - (MOVING_SPIKE_HORIZONTAL_RANGE * TILE_SIZE)
        self.max_x = self.start_x + (MOVING_SPIKE_HORIZONTAL_RANGE * TILE_SIZE)
        self.direction = 1 # 1 for right, -1 for left
        self.speed = MOVING_SPIKE_SPEED

    def update(self, dt=None):
        """Move the spike horizontally and reverse direction at boundaries.
        
        Args:
            dt: Delta time in seconds since last frame (optional, for frame rate independence)
        """
        # Apply movement (use dt if provided for frame rate independence)
        if dt:
            movement = self.direction * self.speed * dt * 60  # Scale by dt and normalize to 60fps
        else:
            movement = self.direction * self.speed
            
        self.rect.x += movement

        # Check boundaries and reverse direction
        if self.rect.centerx >= self.max_x:
            self.rect.centerx = self.max_x # Clamp position
            self.direction = -1
        elif self.rect.centerx <= self.min_x:
            self.rect.centerx = self.min_x # Clamp position
            self.direction = 1
