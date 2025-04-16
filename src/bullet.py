import pygame
from .settings import BULLET_SPEED, BULLET_COLOR, SCREEN_WIDTH

class Bullet(pygame.sprite.Sprite):
    """Represents a projectile fired by the player."""
    def __init__(self, pos, direction_x, groups):
        """
        Initializes a bullet.

        Args:
            pos (tuple): The (x, y) starting position of the bullet.
            direction_x (int): The horizontal direction (-1 for left, 1 for right).
            groups (list): A list of sprite groups to add this bullet to.
        """
        super().__init__(groups)
        
        # Define bullet appearance (small black ball)
        radius = 4
        diameter = radius * 2
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA) # Use SRCALPHA for transparency
        self.image.convert_alpha()
        pygame.draw.circle(self.image, (0, 0, 0), (radius, radius), radius) # Draw black circle

        self.rect = self.image.get_rect(center=pos)
        
        self.direction = pygame.math.Vector2(direction_x, 0)
        self.speed = BULLET_SPEED

        # Store the starting x position to calculate travel distance
        self.start_x = pos[0]
        self.max_travel_distance = SCREEN_WIDTH * 1.5 # Remove bullet if it goes way off screen

    def update(self):
        """Move the bullet horizontally and check if it's off-screen."""
        self.rect.x += self.direction.x * self.speed
        
        # Check if the bullet has traveled too far
        if abs(self.rect.x - self.start_x) > self.max_travel_distance:
            self.kill() # Remove the sprite if it's too far off-screen
