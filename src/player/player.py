import pygame
from src.settings import *
from src.player.movement_state import MovementState

class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self, pos, groups, obstacle_sprites, trap_sprites, exit_sprites, level_complete_callback, death_callback): 
        super().__init__(groups)
        # Visual representation (Circle)
        diameter = TILE_SIZE - 8 # Diameter of the ball
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA) # Create a surface with transparency
        self.image.convert_alpha() # Ensure alpha channel is optimized
        pygame.draw.circle(self.image, LIGHT_PINK, (diameter // 2, diameter // 2), diameter // 2) # Draw light pink circle centered
        # Hitbox for collision (remains a rectangle, centered on the visual)
        self.rect = self.image.get_rect(topleft=(pos[0] + 4, pos[1] + 4)) # Position hitbox based on top-left

        self.movement_state = MovementState() # Initialize movement state

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.trap_sprites = trap_sprites # Store trap sprites
        self.exit_sprites = exit_sprites # Store exit sprites
        self.level_complete_callback = level_complete_callback # For reaching exit
        self.death_callback = death_callback # Store death callback (for hitting traps)
    
    def process_input(self, input_buffer):
        """Process player input from the input buffer."""
        # Check for buffered inputs and handle them
        if input_buffer.get_and_remove_input(pygame.K_SPACE) or input_buffer.get_and_remove_input(pygame.K_UP) or input_buffer.get_and_remove_input(pygame.K_w):
            self.movement_state.jump() # Jump action
        if input_buffer.get_and_remove_input(pygame.K_LSHIFT) or input_buffer.get_and_remove_input(pygame.K_RSHIFT):
            self.movement_state.dash() # Dash action

    def continually_input(self):
        """Handle player input for movement, jumping, and dashing."""
        keys = pygame.key.get_pressed()

        # Horizontal Movement (unless dashing)
        if not self.movement_state.is_dashing:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.movement_state.move_right()
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.movement_state.move_left()
            else:
                self.movement_state.deaccelerate()

    def horizontal_collision(self):
        """Handle horizontal collisions with obstacles, considering dash."""
        # Only apply movement if direction is non-zero or dashing
        self.rect.x += self.movement_state.velocity[0]
        if self.movement_state.is_dashing or self.movement_state.is_running:
             for sprite in self.obstacle_sprites:
                 if sprite.rect.colliderect(self.rect):
                     self.movement_state.stop_horizontal() # Stop on collision
                     if self.movement_state.direction > 0: # Moving right
                         self.rect.right = sprite.rect.left
                     elif self.movement_state.direction < 0: # Moving left
                         self.rect.left = sprite.rect.right

    def vertical_collision(self):
        """Handle vertical collisions with obstacles."""
        # Collision checking (always happens)
        self.rect.y += self.movement_state.velocity[1]
        previous_on_ground = self.movement_state.on_ground
        self.movement_state.on_ground = False # Assume not on ground until collision check
        self.movement_state.air_frames += 1 # Increment air frames

        # Check collision after potential vertical movement
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                if self.movement_state.velocity[1] > 0: # Moving down (falling)
                    self.rect.bottom = sprite.rect.top
                    self.movement_state.on_ground = True
                    self.movement_state.air_frames = 0 # Reset air frames
                elif self.movement_state.velocity[1] < 0: # Moving up (jumping)
                    self.rect.top = sprite.rect.bottom
                self.movement_state.velocity[1] = 0 # Stop upward movement
        # Reset jumps if landed on ground
        if self.movement_state.on_ground and not previous_on_ground:
             self.movement_state.reset_actions()

    def check_trap_collision(self):
        """Check for collisions with traps."""
        # Dash provides immunity during the dash frames
        if not self.movement_state.is_dashing:
            trap_hit = pygame.sprite.spritecollideany(self, self.trap_sprites)
            if trap_hit:
                self.death_callback()

    def check_exit_collision(self):
        """Check for collisions with exit points."""
        exit_hit = pygame.sprite.spritecollideany(self, self.exit_sprites)
        if exit_hit:
            self.level_complete_callback()

    def reset_state(self, position):
        """Resets the player's physics state and sets position."""
        self.rect.topleft = position
        self.movement_state.reset() # Reset movement state
    
    # We need to handle jump and dash triggers via events in the main game loop
    # The player.update method will just manage the state
    def update(self):
        """Update player state (called every frame)."""
        # Input polling is still useful for continuous movement (left/right)
        self.continually_input() # Poll left/right keys
        self.movement_state.update()

        # Apply movement and collisions
        self.vertical_collision() # Includes gravity application
        self.horizontal_collision()


        # Check for interactions AFTER movement/collision resolution
        self.check_trap_collision() # Check for trap collisions
        self.check_exit_collision() # Check for exit collisions
