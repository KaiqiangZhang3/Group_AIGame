import pygame
from .settings import SCREEN_WIDTH

BIRD_COLOR = (100, 100, 255) # A blue-ish color
BIRD_SPEED = 2
BIRD_SIZE = (25, 15) # Width, Height
BIRD_ANIMATION_SPEED = 5 # Frames per second for flapping

class Bird(pygame.sprite.Sprite):
    """Represents a flying bird enemy with flapping animation."""
    def __init__(self, pos, groups, obstacle_sprites, trap_sprites): # Add collision groups
        """
        Initializes a bird enemy.

        Args:
            pos (tuple): The (x, y) starting position (top-left).
            groups (list): A list of sprite groups to add this bird to.
            obstacle_sprites (Group): Sprites the bird should reverse direction on (walls).
            trap_sprites (Group): Sprites the bird should reverse direction on (spikes).
        """
        super().__init__(groups)

        # Store collision groups
        self.obstacle_sprites = obstacle_sprites
        self.trap_sprites = trap_sprites

        # Animation frames
        self.frames = []
        self._create_frames() # Helper to create the images
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Animation timer
        self.animation_timer = 0
        self.animation_speed = BIRD_ANIMATION_SPEED

        # Movement
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = 1 # 1 for right, -1 for left (start moving right)
        self.speed = BIRD_SPEED

    def _create_frames(self):
        """Creates the different animation frames for the bird."""
        # Frame 1: Wings slightly down (original 'V')
        frame_down = pygame.Surface(BIRD_SIZE, pygame.SRCALPHA)
        frame_down.convert_alpha()
        # pygame.draw.line(frame_down, BIRD_COLOR, (0, BIRD_SIZE[1] // 2), (BIRD_SIZE[0] // 2, 0), 3)
        # pygame.draw.line(frame_down, BIRD_COLOR, (BIRD_SIZE[0] // 2, 0), (BIRD_SIZE[0], BIRD_SIZE[1] // 2), 3)
        pygame.draw.line(frame_down, BIRD_COLOR, (0, BIRD_SIZE[1] // 2), (BIRD_SIZE[0] // 2, BIRD_SIZE[1] - 3), 3) # Lower center
        pygame.draw.line(frame_down, BIRD_COLOR, (BIRD_SIZE[0] // 2, BIRD_SIZE[1] - 3), (BIRD_SIZE[0], BIRD_SIZE[1] // 2), 3)
        self.frames.append(frame_down)

        # Frame 2: Wings slightly up
        frame_up = pygame.Surface(BIRD_SIZE, pygame.SRCALPHA)
        frame_up.convert_alpha()
        # pygame.draw.line(frame_up, BIRD_COLOR, (0, BIRD_SIZE[1] // 2), (BIRD_SIZE[0] // 2, 0), 3)
        pygame.draw.line(frame_up, BIRD_COLOR, (0, BIRD_SIZE[1] // 2), (BIRD_SIZE[0] // 2, 3), 3) # Higher center
        pygame.draw.line(frame_up, BIRD_COLOR, (BIRD_SIZE[0] // 2, 3), (BIRD_SIZE[0], BIRD_SIZE[1] // 2), 3)
        self.frames.append(frame_up)

    def _animate(self, dt):
        """Handles the bird's flapping animation."""
        self.animation_timer += dt
        time_per_frame = 1.0 / self.animation_speed

        if self.animation_timer >= time_per_frame:
            self.animation_timer -= time_per_frame # Reset timer preserving overshoot
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def update(self, dt): # Add dt for animation timing
        """Move the bird, check collisions, and animate."""
        self._animate(dt) # Update animation frame

        # Move horizontally
        self.rect.x += self.direction * self.speed

        # Check for collisions with obstacles or traps
        hit_obstacle = pygame.sprite.spritecollideany(self, self.obstacle_sprites)
        hit_trap = pygame.sprite.spritecollideany(self, self.trap_sprites)

        if hit_obstacle or hit_trap:
            # Move back to previous position to avoid getting stuck
            self.rect.x -= self.direction * self.speed
            # Reverse direction
            self.direction *= -1

        # Removed screen edge check - now relies on collision
        # if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
        #     self.direction *= -1
