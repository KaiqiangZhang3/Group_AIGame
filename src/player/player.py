import pygame
from src.settings import *
from src.player.movement_state import MovementState
from src.settings import VOICE_COMMAND_JUMP
import math # Import math for sine wave

class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self, pos, groups, obstacle_sprites, trap_sprites, exit_sprites, level_complete_callback, death_callback): 
        super().__init__(groups)
        # Visual representation (Circle)
        diameter = TILE_SIZE - 8 # Diameter of the ball
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA) # Create a surface with transparency
        self.image.convert_alpha() # Ensure alpha channel is optimized
        pygame.draw.circle(self.image, PLAYER_COLOR, (diameter // 2, diameter // 2), diameter // 2) # Draw player circle
        # Hitbox for collision (remains a rectangle, centered on the visual)
        self.rect = self.image.get_rect(topleft=(pos[0] + 4, pos[1] + 4)) # Position hitbox based on top-left

        self.movement_state = MovementState() # Initialize movement state

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.trap_sprites = trap_sprites # Store trap sprites
        self.exit_sprites = exit_sprites # Store exit sprites
        self.level_complete_callback = level_complete_callback # For reaching exit
        self.death_callback = death_callback # Store death callback (for hitting traps)

        # Pulsing light effect
        self.pulse_timer = 0
        # Max radius for the surface so it doesn't clip during pulse
        max_pulse_radius = PLAYER_LIGHT_BASE_RADIUS + PLAYER_LIGHT_PULSE_AMPLITUDE
        self.light_surface_size = (max_pulse_radius * 2, max_pulse_radius * 2)
        self.light_surface_center = (max_pulse_radius, max_pulse_radius)
        
        # self.glow_surface = pygame.Surface(self.light_surface_size, pygame.SRCALPHA)
        # self.glow_surface.convert_alpha()
        self.mask_brush_surface = pygame.Surface(self.light_surface_size, pygame.SRCALPHA)
        self.mask_brush_surface.convert_alpha()
    
    def process_input(self, input_buffer):
        """Process player input from the input buffer."""
        if self.movement_state.is_climbing_jump: return
        # Check for buffered inputs and handle them
        if input_buffer.get_and_remove_input(pygame.K_SPACE) or \
           input_buffer.get_and_remove_input(pygame.K_UP) or \
           input_buffer.get_and_remove_input(pygame.K_w) or \
           input_buffer.get_and_remove_input(VOICE_COMMAND_JUMP): 
            self.movement_state.jump() # Jump action
        if input_buffer.get_and_remove_input(pygame.K_LSHIFT) or input_buffer.get_and_remove_input(pygame.K_RSHIFT):
            self.movement_state.dash() # Dash action

    def continually_input(self):
        """Handle player input for movement, jumping, and dashing."""
        if self.movement_state.is_climbing_jump: return
        keys = pygame.key.get_pressed()

        if not self.movement_state.is_dashing and not self.movement_state.is_super_jumping:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.movement_state.move_right()
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.movement_state.move_left()
            else:
                self.movement_state.decelerate()

    def horizontal_collision(self):
        """Handle horizontal collisions with obstacles, considering dash."""
        # Only apply movement if direction is non-zero or dashing
        self.rect.x += self.movement_state.velocity[0]
        self.movement_state.is_climbing = False
        if self.movement_state.velocity[0] != 0 or self.movement_state.is_dashing:
             for sprite in self.obstacle_sprites:
                 if sprite.rect.colliderect(self.rect):
                     if not self.movement_state.on_ground and self.movement_state.air_frames > CLIMBING_JUMP_FRAME:
                         self.movement_state.start_climbing()
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
        if self.movement_state.is_dashing:
            self.movement_state.velocity[1] = 0 # Stop vertical movement during dash
        # Check collision after potential vertical movement
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                if self.movement_state.velocity[1] > 0: # Moving down (falling)
                    self.rect.bottom = sprite.rect.top
                    self.movement_state.on_ground = True
                    self.movement_state.air_frames = 0 # Reset air frames
                    self.movement_state.is_climbing = False # Stop climbing
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
    
    def get_light_effects(self):
        """Prepares and returns player's light mask brush surface, its world position, radius, and center."""
        # Calculate current pulse values
        oscillation = math.sin(self.pulse_timer)
        current_radius_offset = oscillation * PLAYER_LIGHT_PULSE_AMPLITUDE
        pulsing_radius = PLAYER_LIGHT_BASE_RADIUS + current_radius_offset

        normalized_sin_for_alpha = (oscillation + 1) / 2 # Range 0 to 1
        pulsing_alpha = PLAYER_LIGHT_MIN_ALPHA + normalized_sin_for_alpha * (PLAYER_LIGHT_MAX_ALPHA - PLAYER_LIGHT_MIN_ALPHA)
        
        current_mask_brush_color = (PLAYER_MASK_BRUSH_COLOR[0], PLAYER_MASK_BRUSH_COLOR[1], PLAYER_MASK_BRUSH_COLOR[2], int(pulsing_alpha))

        # Redraw the mask brush circle
        self.mask_brush_surface.fill((0,0,0,0))
        pygame.draw.circle(self.mask_brush_surface, current_mask_brush_color, self.light_surface_center, int(pulsing_radius))
        
        # Calculate top-left world position for the light surfaces to center them on the player
        light_world_pos_x = self.rect.centerx - self.light_surface_center[0]
        light_world_pos_y = self.rect.centery - self.light_surface_center[1]
        
        return self.mask_brush_surface, (light_world_pos_x, light_world_pos_y), pulsing_radius, self.light_surface_center

    # We need to handle jump and dash triggers via events in the main game loop
    # The player.update method will just manage the state
    def update(self):
        """Update player state (called every frame)."""
        # Update pulse timer for light effect
        self.pulse_timer += PLAYER_LIGHT_PULSE_SPEED * (1/FPS) # Tie speed to FPS for consistency
        if self.pulse_timer > 2 * math.pi: # Keep angle within one cycle to prevent large numbers
            self.pulse_timer -= 2 * math.pi

        # Input polling is still useful for continuous movement (left/right)
        self.continually_input() # Poll left/right keys
        self.movement_state.update()
        # Apply movement and collisions
        self.vertical_collision() # Includes gravity application
        self.horizontal_collision()

        # Check for interactions AFTER movement/collision resolution
        self.check_trap_collision() # Check for trap collisions
        self.check_exit_collision() # Check for exit collisions
