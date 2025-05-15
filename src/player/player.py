import pygame
from src.settings import *
from src.player.movement_state import MovementState
# VOICE_COMMAND_JUMP is imported below with others
import math # Import math for sine wave
from ..core.input_buffer import InputBuffer
from ..settings import (
    PLAYER_COLOR, PLAYER_SPEED, PLAYER_JUMP_STRENGTH,
    PLAYER_GRAVITY, PLAYER_DASH_SPEED,
    PLAYER_DASH_DURATION, PLAYER_DASH_COOLDOWN, PLAYER_GLOW_COLOR, 
    PLAYER_LIGHT_BASE_RADIUS, PLAYER_LIGHT_PULSE_AMPLITUDE, PLAYER_LIGHT_PULSE_SPEED,
    PLAYER_LIGHT_MIN_ALPHA, PLAYER_LIGHT_MAX_ALPHA, PLAYER_MASK_BRUSH_COLOR,
    VOICE_LIGHT_MAX_BONUS_RADIUS, VOICE_LIGHT_DECAY_RATE, 
    VOICE_LIGHT_INCREASE_RATE, VOICE_SPEECH_COOLDOWN_DURATION, LONG_SILENCE_DURATION,
    VOICE_COMMAND_JUMP, VOICE_COMMAND_DASH, # Added VOICE_COMMAND_DASH
    INPUT_BUFFER_KEY_JUMP, INPUT_BUFFER_KEY_DASH, # Added Key buffer commands
    PERFECT_ACTION_WINDOW_MS, PERFECT_ACTION_DURATION_S, PERFECT_ACTION_COLOR, PLAYER_DEFAULT_COLOR # Added Perfect Action settings
)
import time # For current time if needed, though buffer timestamps are primary


class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self, pos, groups, obstacle_sprites, trap_sprites, exit_sprites, level_complete_callback, death_callback, input_buffer: InputBuffer, level_instance): 
        super().__init__(groups)
        
        self.diameter = TILE_SIZE - 8 # Diameter of the ball
        self.image = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(pos[0] + 4, pos[1] + 4))

        # Perfect Action State
        self.current_color = PLAYER_DEFAULT_COLOR
        self.is_perfect_action_active = False
        self.perfect_action_timer_s = 0.0
        self._redraw_player_surface() # Initial draw with default color

        self.movement_state = MovementState() # Initialize movement state
        self.input_buffer = input_buffer # Store the input buffer instance

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.trap_sprites = trap_sprites # Store trap sprites
        self.exit_sprites = exit_sprites # Store exit sprites
        self.level_complete_callback = level_complete_callback # For reaching exit
        self.death_callback = death_callback # Store death callback (for hitting traps)

        # Pulsing light effect
        self.pulse_timer = 0
        # Ensure light surface is large enough for base, pulse, and voice bonus
        max_possible_radius = PLAYER_LIGHT_BASE_RADIUS + PLAYER_LIGHT_PULSE_AMPLITUDE + VOICE_LIGHT_MAX_BONUS_RADIUS
        self.light_surface_size = (max_possible_radius * 2, max_possible_radius * 2)
        self.light_surface_center = (max_possible_radius, max_possible_radius)
        
        self.voice_light_bonus_radius = 0.0 # Bonus radius from voice
        self.level_instance = level_instance # Store reference to the current level
        self.full_illumination_triggered_this_session = False # Flag for full illumination
        self.speaking_cooldown_timer = 0.0 # Timer to track if player is 'speaking'
        self.time_since_last_ambient_speech = 0.0 # Timer for long silence decay

        # self.glow_surface = pygame.Surface(self.light_surface_size, pygame.SRCALPHA)
        # self.glow_surface.convert_alpha()
        self.mask_brush_surface = pygame.Surface(self.light_surface_size, pygame.SRCALPHA)
        self.mask_brush_surface.convert_alpha()
    
    def _redraw_player_surface(self):
        """Redraws the player's surface with the current color."""
        self.image.fill((0,0,0,0)) # Clear previous drawing (transparent fill)
        pygame.draw.circle(self.image, self.current_color, (self.diameter // 2, self.diameter // 2), self.diameter // 2)
    
    def process_input(self): 
        """Process player input from the input buffer for jumps and dashes, including perfect actions."""
        if self.movement_state.is_climbing_jump: return

        events_to_remove = []
        action_performed_this_frame = {'jump': False, 'dash': False}
        
        time_window_s = (PERFECT_ACTION_WINDOW_MS / 1000.0) * 1.1

        key_jump_events = self.input_buffer.get_recent_events([INPUT_BUFFER_KEY_JUMP], time_window_s)
        voice_jump_events = self.input_buffer.get_recent_events([VOICE_COMMAND_JUMP], time_window_s)
        key_dash_events = self.input_buffer.get_recent_events([INPUT_BUFFER_KEY_DASH], time_window_s)
        voice_dash_events = self.input_buffer.get_recent_events([VOICE_COMMAND_DASH], time_window_s)

        perfect_window_s = PERFECT_ACTION_WINDOW_MS / 1000.0

        # 1. Check for Perfect Jump
        for kj_event_key, kj_ts in key_jump_events:
            if action_performed_this_frame['jump']: break
            for vj_event_key, vj_ts in voice_jump_events:
                if abs(kj_ts - vj_ts) <= perfect_window_s:
                    print("PERFECT JUMP!")
                    self.movement_state.jump()
                    self.current_color = PERFECT_ACTION_COLOR
                    self.is_perfect_action_active = True
                    self.perfect_action_timer_s = PERFECT_ACTION_DURATION_S
                    self._redraw_player_surface()
                    events_to_remove.extend([(kj_event_key, kj_ts), (vj_event_key, vj_ts)])
                    action_performed_this_frame['jump'] = True
                    break 
            if action_performed_this_frame['jump']: break

        # 2. Check for Perfect Dash
        if not action_performed_this_frame['jump']:
            for kd_event_key, kd_ts in key_dash_events:
                if action_performed_this_frame['dash']: break
                for vd_event_key, vd_ts in voice_dash_events:
                    if abs(kd_ts - vd_ts) <= perfect_window_s:
                        print("PERFECT DASH!")
                        self.movement_state.dash()
                        self.current_color = PERFECT_ACTION_COLOR
                        self.is_perfect_action_active = True
                        self.perfect_action_timer_s = PERFECT_ACTION_DURATION_S
                        self._redraw_player_surface()
                        events_to_remove.extend([(kd_event_key, kd_ts), (vd_event_key, vd_ts)])
                        action_performed_this_frame['dash'] = True
                        break
                if action_performed_this_frame['dash']: break

        # 3. Process Regular Jump
        if not action_performed_this_frame['jump']:
            all_jump_candidates = sorted(
                [(e_key, ts) for e_key, ts in key_jump_events if (e_key, ts) not in events_to_remove] +
                [(e_key, ts) for e_key, ts in voice_jump_events if (e_key, ts) not in events_to_remove],
                key=lambda x: x[1], reverse=True
            )
            if all_jump_candidates:
                event_to_process = all_jump_candidates[0]
                self.movement_state.jump()
                events_to_remove.append(event_to_process)
                action_performed_this_frame['jump'] = True
                print(f"Regular Jump from: {event_to_process[0]}")

        # 4. Process Regular Dash
        if not action_performed_this_frame['jump'] and not action_performed_this_frame['dash']:
            all_dash_candidates = sorted(
                [(e_key, ts) for e_key, ts in key_dash_events if (e_key, ts) not in events_to_remove] +
                [(e_key, ts) for e_key, ts in voice_dash_events if (e_key, ts) not in events_to_remove],
                key=lambda x: x[1], reverse=True
            )
            if all_dash_candidates:
                event_to_process = all_dash_candidates[0]
                self.movement_state.dash()
                events_to_remove.append(event_to_process)
                action_performed_this_frame['dash'] = True
                print(f"Regular Dash from: {event_to_process[0]}")

        if events_to_remove:
            self.input_buffer.remove_specific_events(list(set(events_to_remove)))

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
        self.voice_light_bonus_radius = 0.0 # Also reset voice light bonus
        self.speaking_cooldown_timer = 0.0 # Reset speaking timer
        self.time_since_last_ambient_speech = 0.0 # Reset long silence timer
        self.full_illumination_triggered_this_session = False # Reset illumination trigger flag
        self.is_perfect_action_active = False
        self.perfect_action_timer_s = 0.0
        self.current_color = PLAYER_DEFAULT_COLOR
        self._redraw_player_surface()

    def notify_ambient_speech(self):
        """Called when non-command speech is detected. Sets a timer to indicate recent speech and resets long silence timer."""
        self.speaking_cooldown_timer = VOICE_SPEECH_COOLDOWN_DURATION
        self.time_since_last_ambient_speech = 0.0 # Reset long silence timer on any ambient speech

    def get_light_effects(self):
        """Prepares and returns player's light mask brush surface, its world position, radius, and center."""
        # Calculate current pulse values
        oscillation = math.sin(self.pulse_timer)
        current_radius_offset = oscillation * PLAYER_LIGHT_PULSE_AMPLITUDE
        # Base radius now includes voice bonus
        current_base_radius = PLAYER_LIGHT_BASE_RADIUS + self.voice_light_bonus_radius
        pulsing_radius = current_base_radius + current_radius_offset
        pulsing_radius = max(0, pulsing_radius) # Ensure radius is not negative

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

    def update(self, dt): 
        """Update player state (called every frame)."""
        self.process_input() 

        if self.is_perfect_action_active:
            self.perfect_action_timer_s -= dt
            if self.perfect_action_timer_s <= 0:
                self.is_perfect_action_active = False
                self.perfect_action_timer_s = 0.0
                self.current_color = PLAYER_DEFAULT_COLOR
                self._redraw_player_surface()

        # Update pulse timer for light effect
        self.pulse_timer += PLAYER_LIGHT_PULSE_SPEED * dt 
        if self.pulse_timer > 2 * math.pi: 
            self.pulse_timer -= 2 * math.pi

        # Voice-activated light expansion/decay logic
        if self.speaking_cooldown_timer > 0:
            self.speaking_cooldown_timer -= dt
            self.speaking_cooldown_timer = max(0, self.speaking_cooldown_timer) 
            
            # Player is considered "speaking", increase light radius
            increase_amount = VOICE_LIGHT_INCREASE_RATE * dt
            self.voice_light_bonus_radius += increase_amount
            self.voice_light_bonus_radius = min(self.voice_light_bonus_radius, VOICE_LIGHT_MAX_BONUS_RADIUS)
            
            # While actively speaking (or in cooldown), long silence timer is implicitly reset (or doesn't advance meaningfully)
            # self.time_since_last_ambient_speech = 0 
        else:
            # Player is not in active speech cooldown, start counting time since last ambient speech
            self.time_since_last_ambient_speech += dt
            
            # Only decay if the long silence duration has been met
            if self.time_since_last_ambient_speech >= LONG_SILENCE_DURATION:
                if self.voice_light_bonus_radius > 0:
                    decay_amount = VOICE_LIGHT_DECAY_RATE * dt
                    self.voice_light_bonus_radius -= decay_amount
                    self.voice_light_bonus_radius = max(0, self.voice_light_bonus_radius)
            # If self.time_since_last_ambient_speech < LONG_SILENCE_DURATION, bonus radius HOLDS its value.
        
        # Check for triggering full level illumination
        if self.voice_light_bonus_radius >= VOICE_LIGHT_MAX_BONUS_RADIUS:
            if not self.full_illumination_triggered_this_session and self.level_instance:
                self.level_instance.start_full_illumination()
                self.full_illumination_triggered_this_session = True
        else:
            # Reset the trigger if the light radius drops below max
            self.full_illumination_triggered_this_session = False

        # Input polling is still useful for continuous movement (left/right)
        self.continually_input() 
        self.movement_state.update()
        # Apply movement and collisions
        self.vertical_collision() 
        self.horizontal_collision()

        # Check for interactions AFTER movement/collision resolution
        self.check_trap_collision() 
        self.check_exit_collision() 
