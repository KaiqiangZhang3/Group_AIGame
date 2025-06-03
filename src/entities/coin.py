import pygame
from src.settings import TILE_SIZE, COIN_COLOR_PRIMARY, COIN_COLOR_SHINE, COIN_ANIMATION_SPEED, COIN_RADIUS

class Coin(pygame.sprite.Sprite):
    """Represents a rotating coin that can be collected by the player."""
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.frames = []
        self._create_frames()
        self.current_frame_index = 0
        self.image = self.frames[self.current_frame_index]
        
        # Center the coin within the tile grid cell it's placed in
        center_x = pos[0] + TILE_SIZE // 2
        center_y = pos[1] + TILE_SIZE // 2
        self.rect = self.image.get_rect(center=(center_x, center_y))

        self.animation_timer = 0
        self.is_collected = False

    def _create_frames(self):
        """Creates the animation frames for the coin programmatically."""
        # Frame 1: Full circle
        frame_1 = pygame.Surface((COIN_RADIUS * 2, COIN_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(frame_1, COIN_COLOR_PRIMARY, (COIN_RADIUS, COIN_RADIUS), COIN_RADIUS)
        pygame.draw.circle(frame_1, COIN_COLOR_SHINE, (COIN_RADIUS - COIN_RADIUS // 3, COIN_RADIUS - COIN_RADIUS // 3), COIN_RADIUS // 4) # Shine
        self.frames.append(frame_1)

        # Frame 2: Squashed ellipse (width reduced)
        frame_2 = pygame.Surface((COIN_RADIUS * 2, COIN_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(frame_2, COIN_COLOR_PRIMARY, pygame.Rect(COIN_RADIUS // 2, 0, COIN_RADIUS, COIN_RADIUS * 2))
        self.frames.append(frame_2)

        # Frame 3: Thin line (edge-on view)
        frame_3 = pygame.Surface((COIN_RADIUS * 2, COIN_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.line(frame_3, COIN_COLOR_PRIMARY, (COIN_RADIUS, 0), (COIN_RADIUS, COIN_RADIUS * 2), 3) # Line width 3
        self.frames.append(frame_3)

        # Frame 4: Squashed ellipse (same as frame 2, for smoother loop)
        self.frames.append(frame_2.copy()) # Reuse frame 2

    def update(self, dt):
        """Updates the coin's animation."""
        if not self.is_collected:
            self.animation_timer += dt
            if self.animation_timer >= COIN_ANIMATION_SPEED:
                self.animation_timer = 0
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
                self.image = self.frames[self.current_frame_index]
                # Keep rect centered if size changes, though for this animation it shouldn't significantly
                # current_center = self.rect.center
                # self.rect = self.image.get_rect(center=current_center)

    def collect(self):
        """Marks the coin as collected and makes it disappear."""
        if not self.is_collected:
            self.is_collected = True
            self.kill() # Remove from all sprite groups

    def reset(self):
        """Resets the coin to its initial state (uncollected)."""
        self.is_collected = False
        self.current_frame_index = 0
        self.image = self.frames[self.current_frame_index]
        # Note: The Level class will be responsible for adding it back to sprite groups.
