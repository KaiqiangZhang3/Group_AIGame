import pygame
import os
from src.settings import *
from src.player.movement_state import MovementState
from src.animation import Animator # Added Animator import
from src.settings import VOICE_COMMAND_JUMP

class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self, pos, groups, obstacle_sprites, trap_sprites, exit_sprites, coin_sprites, level_complete_callback, death_callback): 
        super().__init__(groups)
        # Animator setup
        # Assuming player.py is in src/player/ and Assets is in the project root
        # Adjust path if your project structure is different
        sprites_base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Assets', 'Sprites')
        self.animator = Animator(sprites_base_path)
        self.image = self.animator.get_current_image()
        self.rect = self.image.get_rect(topleft=pos)

        self.movement_state = MovementState() # Initialize movement state

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.trap_sprites = trap_sprites # Store trap sprites
        self.exit_sprites = exit_sprites # Store exit sprites
        self.coin_sprites = coin_sprites # Store coin sprites
        self.level_complete_callback = level_complete_callback # For reaching exit
        self.death_callback = death_callback # Store death callback (for hitting traps)
    
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
                    # Check if landed on a temporary platform and activate its timer
                    if hasattr(sprite, 'tile_type') and sprite.tile_type == 'temp_platform':
                        if hasattr(sprite, 'activate_timer'):
                            sprite.activate_timer()
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

    def _check_coin_collision(self):
        """Check for collisions with coins and collect them."""
        # Use spritecollide to get a list of all coins hit
        collided_coins = pygame.sprite.spritecollide(self, self.coin_sprites, False) # False so coin isn't auto-removed
        for coin in collided_coins:
            if hasattr(coin, 'is_collected') and not coin.is_collected:
                if hasattr(coin, 'collect'):
                    coin.collect() # Coin handles its own removal from groups
                if hasattr(self.movement_state, 'recharge_double_jump'):
                    self.movement_state.recharge_double_jump()
                    # Optional: Add a sound effect or visual feedback here

    def reset_state(self, position):
        """Resets the player's physics state and sets position."""
        self.rect.topleft = position
        self.movement_state.reset() # Reset movement state
    
    # We need to handle jump and dash triggers via events in the main game loop
    # The player.update method will just manage the state
    def _get_animation_action(self):
        """Determine the animation action string based on the current movement state."""
        # Priority: Attacking, Hurt, Death (These would need new flags in MovementState and handling)
        # Example: if self.movement_state.is_attacking and 'attack_1' in self.animator.animations: return 'attack_1'
        # Example: if self.movement_state.is_hurt and 'hurt' in self.animator.animations: return 'hurt'

        if self.movement_state.is_dashing and 'dash' in self.animator.animations:
            return 'dash'
        
        if self.movement_state.is_climbing_jump:
            return 'wall_jump' if 'wall_jump' in self.animator.animations else 'jump'
        
        if self.movement_state.is_climbing:
            if 'climbing' in self.animator.animations:
                return 'climbing'
            # Fallback to wall_slide if climbing not distinct or player is sliding down wall
            elif self.movement_state.velocity[1] > 0 and 'wall_slide' in self.animator.animations:
                return 'wall_slide'
            elif 'wall_contact' in self.animator.animations: # If stationary on wall
                 return 'wall_contact'
            return 'jump_fall' # Generic fallback

        if not self.movement_state.on_ground:
            if self.movement_state.velocity[1] < -0.1: # Moving up (0.1 threshold for sensitivity)
                if self.movement_state.air_frames < 5 and 'jump_start' in self.animator.animations:
                    return 'jump_start'
                return 'jump' if 'jump' in self.animator.animations else 'idle'
            elif self.movement_state.velocity[1] > 0.1: # Moving down
                return 'jump_fall' if 'jump_fall' in self.animator.animations else 'idle'
            else: # Near apex of jump
                return 'jump_transition' if 'jump_transition' in self.animator.animations else ('jump' if 'jump' in self.animator.animations else 'idle')

        if self.movement_state.is_running:
            if 'run' in self.animator.animations:
                return 'run'
            elif 'walk' in self.animator.animations: # Fallback to walk if run isn't present
                return 'walk'
        
        if self.movement_state.is_idle:
            return 'idle'
        
        return 'idle' # Default fallback

    def update(self, dt):
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
        self._check_coin_collision() # Check for coin collisions

        # Animation update
        action = self._get_animation_action()
        self.animator.set_action(action)
        self.animator.update(dt)
        
        new_image = self.animator.get_current_image()
        if self.movement_state.direction == -1: # Facing left
            self.image = pygame.transform.flip(new_image, True, False)
        else: # Facing right
            self.image = new_image
        
        # Preserve the center of the rect when changing image/size to avoid jitter
        # This is a common strategy but might need fine-tuning based on sprite pivot points.
        current_center = self.rect.center
        self.rect.size = self.image.get_size()
        self.rect.center = current_center
