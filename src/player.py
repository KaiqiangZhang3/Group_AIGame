# Proposed content for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/player.py
# Instruction: Update Player class to handle trap collisions, accept trap sprites/reset callback, exit sprites, and level complete callback.

import pygame
from .settings import *

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

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        self.gravity = PLAYER_GRAVITY
        self.jump_strength = PLAYER_JUMP_STRENGTH
        self.on_ground = False

        # Double Jump
        self.max_jumps = 2
        self.jumps_left = self.max_jumps

        # Dash
        self.can_dash = True
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.dash_direction = 0 # 1 for right, -1 for left
        self.facing_direction = 1 # Track last non-zero horizontal direction

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.trap_sprites = trap_sprites # Store trap sprites
        self.exit_sprites = exit_sprites # Store exit sprites
        self.level_complete_callback = level_complete_callback # For reaching exit
        self.death_callback = death_callback # Store death callback (for hitting traps)

        # Status flags
        self.on_ground = False

    def input(self):
        """Handle player input for movement, jumping, and dashing."""
        keys = pygame.key.get_pressed()

        # Horizontal Movement (unless dashing)
        if not self.is_dashing:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.facing_direction = 1 # Update facing direction
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.facing_direction = -1 # Update facing direction
            else:
                self.direction.x = 0

    def apply_gravity(self):
        """Apply gravity to the player."""
        # Gravity doesn't apply during dash
        if not self.is_dashing:
            self.direction.y += self.gravity
            # Basic terminal velocity
            if self.direction.y > 15:
                self.direction.y = 15
            self.rect.y += self.direction.y

    def jump(self):
        """Make the player jump (single or double)."""
        if self.jumps_left > 0:
            # Use double jump strength if it's the second jump
            jump_power = self.jump_strength if self.jumps_left == self.max_jumps else PLAYER_DOUBLE_JUMP_STRENGTH
            self.direction.y = jump_power
            self.jumps_left -= 1
            self.on_ground = False # Player leaves the ground on jump

    def dash(self):
        """Initiate the dash."""
        if self.can_dash:
            print("Dash initiated!") # Debug print
            self.is_dashing = True
            self.can_dash = False # Can't dash again until cooldown finishes
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN # Start cooldown

            # Use facing direction for dash
            self.dash_direction = self.facing_direction

            # Freeze vertical movement during dash
            self.direction.y = 0

    def update_dash(self):
        """Update dash state, timer, and cooldown."""
        # Cooldown update
        if not self.can_dash:
            self.dash_cooldown_timer -= 1
            if self.dash_cooldown_timer <= 0:
                self.can_dash = True
                print("Dash ready!") # Debug print

        # Dash active update
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                print("Dash finished.") # Debug print
                self.direction.x = 0 # Stop horizontal movement after dash ends


    def horizontal_collision(self):
        """Handle horizontal collisions with obstacles, considering dash."""
        # Calculate horizontal movement based on speed or dash speed
        move_speed = PLAYER_DASH_SPEED if self.is_dashing else self.speed
        move_direction = self.dash_direction if self.is_dashing else self.direction.x

        # Only apply movement if direction is non-zero or dashing
        if move_direction != 0 or self.is_dashing:
             self.rect.x += move_direction * move_speed

             for sprite in self.obstacle_sprites:
                 if sprite.rect.colliderect(self.rect):
                     if move_direction > 0: # Moving right
                         self.rect.right = sprite.rect.left
                         if self.is_dashing: self.is_dashing = False # Stop dash on collision
                     elif move_direction < 0: # Moving left
                         self.rect.left = sprite.rect.right
                         if self.is_dashing: self.is_dashing = False # Stop dash on collision
                     # Stop horizontal movement on collision only if not dashing
                     # If dashing, direction.x might be 0 but dash_direction isn't
                     if not self.is_dashing:
                          self.direction.x = 0

    def vertical_collision(self):
        """Handle vertical collisions with obstacles."""
        # Apply gravity unless dashing
        if not self.is_dashing:
            self.apply_gravity()
        else:
             # Vertical position doesn't change during dash
             pass

        # Collision checking (always happens)
        previous_on_ground = self.on_ground
        self.on_ground = False # Assume not on ground until collision check

        # Check collision after potential vertical movement
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0: # Falling/moving down
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0: # Moving up (jumping)
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0 # Stop upward movement

        # Reset jumps if landed on ground
        if self.on_ground and not previous_on_ground:
             self.jumps_left = self.max_jumps
             print("Landed! Jumps reset.") # Debug print

    def check_trap_collision(self):
        """Check for collisions with traps."""
        # Dash provides immunity during the dash frames
        if not self.is_dashing:
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
        self.direction = pygame.math.Vector2(0, 0) # Reset velocity completely
        self.jumps_left = self.max_jumps # Reset jumps
        self.is_dashing = False # Ensure dash state is off
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.on_ground = False

    # We need to handle jump and dash triggers via events in the main game loop
    # The player.update method will just manage the state
    def update(self):
        """Update player state (called every frame)."""
        # Input polling is still useful for continuous movement (left/right)
        self.input() # Poll left/right keys

        # Update dash state (timers, cooldown)
        self.update_dash()

        # Apply movement and collisions
        self.horizontal_collision()
        self.vertical_collision() # Includes gravity application

        # Check for interactions AFTER movement/collision resolution
        self.check_trap_collision() # Check for trap collisions
        self.check_exit_collision() # Check for exit collisions
