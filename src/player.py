# Proposed content for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/player.py
# Instruction: Update Player class to handle trap collisions, accept trap sprites/reset callback, exit sprites, and level complete callback.

import pygame
from .settings import *
from .bullet import Bullet

class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self, pos, groups, obstacle_sprites, trap_sprites, exit_sprites, 
                 level_complete_callback, death_callback, visible_sprites, 
                 bullet_sprites, bird_sprites, hidden_door_sprites, 
                 trigger_hidden_level_callback): 
        super().__init__(groups)

        # --- Sprite Groups (for spawning bullets) ---
        self.all_sprites = visible_sprites
        self.bullet_sprites = bullet_sprites

        # --- Scaling and Dimensions ---
        self.scale_factor = 1.5
        self.visual_height = int(TILE_SIZE * self.scale_factor)
        # Calculate visual component sizes based on the total visual height
        self.head_radius = int(self.visual_height * 0.2)
        self.body_height = int(self.visual_height * 0.4) # Body is shorter relative to head/legs
        self.shoulder_y_offset = self.head_radius * 1.5 # Relative to top of hitbox
        self.hip_y_offset = self.shoulder_y_offset + self.body_height # Relative to top of hitbox
        self.arm_length = int(self.visual_height * 0.35)
        self.leg_length = int(self.visual_height * 0.45)
        self.limb_thickness = max(3, int(4 * self.scale_factor)) # Scale thickness too

        # --- Hitbox Definition ---
        # Make hitbox slightly narrower than body/head, and full visual height
        hitbox_width = int(self.head_radius * 1.8) # Width based on head/body
        hitbox_height = self.visual_height
        # Position hitbox: Center horizontally in spawn tile, bottom aligned with tile bottom
        hitbox_x = pos[0] + (TILE_SIZE - hitbox_width) // 2
        hitbox_y = pos[1] + TILE_SIZE - hitbox_height
        self.rect = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

        # Save original position for reset
        self.start_pos = (hitbox_x, hitbox_y)

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
        self.bird_sprites = bird_sprites # Store bird sprites
        self.hidden_door_sprites = hidden_door_sprites # Store hidden door sprites
        self.level_complete_callback = level_complete_callback # For reaching exit
        self.death_callback = death_callback # Store death callback (for hitting traps)
        self.trigger_hidden_level_callback = trigger_hidden_level_callback # Store hidden level callback

        # Status flags
        self.on_ground = False
        self.facing_right = True # For animation later

        # Animation
        self.animation_state = 'idle' 
        self.animation_timer = 0.0
        self.animation_speed = 8 # Frames per second for animation
        self.animation_frame_index = 0

        # Shooting
        self.can_shoot = True
        self.shoot_cooldown_timer = 0

    def input(self):
        """Handle player input for movement, jumping, and dashing."""
        keys = pygame.key.get_pressed()

        # Horizontal Movement (unless dashing)
        if not self.is_dashing:
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing_direction = -1 # Update facing direction
                self.facing_right = False
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing_direction = 1 # Update facing direction
                self.facing_right = True
            else:
                self.direction.x = 0

        # Jump, Dash, and Shoot triggers are handled by KEYDOWN events in Game loop
        # for event handling separation, BUT we can poll single-press keys here too.
        # Let's handle shoot via polling for simplicity here.
        if keys[pygame.K_q]:
             if self.can_shoot:
                 self.shoot()

    def apply_gravity(self):
        """Apply gravity to the player."""
        # Gravity doesn't apply during dash
        if not self.is_dashing:
            self.direction.y += self.gravity
            # Basic terminal velocity
            if self.direction.y > 15:
                self.direction.y = 15

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
        # Gravity is now applied in move() before this check
        # Vertical movement (self.rect.y += self.direction.y) is also applied in move()
        
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
             # print("Landed! Jumps reset.") # Reduced debug prints

    def check_trap_collision(self):
        """Check for collisions with traps."""
        # Dash provides immunity during the dash frames
        if not self.is_dashing:
            trap_hit = pygame.sprite.spritecollideany(self, self.trap_sprites)
            if trap_hit:
                self.death_callback() # Call the death callback

    def check_bird_collision(self):
        """Check for collisions with birds."""
        # Dash immunity might apply here too, if desired
        if not self.is_dashing:
            bird_hit = pygame.sprite.spritecollideany(self, self.bird_sprites)
            if bird_hit:
                print("Player hit by bird!") # Debug
                self.death_callback()

    def check_hidden_door_collision(self):
        """Check if the player collides with a hidden door tile."""
        collided_door = pygame.sprite.spritecollideany(self, self.hidden_door_sprites)
        if collided_door:
            self.trigger_hidden_level_callback() # Call the callback to load the hidden level

    def shoot(self):
        """Creates and launches a bullet in the direction the player is facing."""
        # Calculate bullet start position (e.g., near player center)
        bullet_start_pos = self.rect.center
        
        # Set cooldown
        self.can_shoot = False
        self.shoot_cooldown_timer = PLAYER_SHOOT_COOLDOWN / 60.0 # Convert frames to seconds

        # Create bullet
        Bullet(pos=bullet_start_pos, 
               direction_x=self.facing_direction, 
               groups=[self.all_sprites, self.bullet_sprites])
        # print(f"Shoot! Dir: {self.facing_direction}") # Debug

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

    def move(self, dt):
        """Handles movement physics, collisions, dash, and sets animation state."""
        # --- Dash Handling ---
        current_speed = self.dash_speed if self.is_dashing else self.speed

        # Horizontal Movement (unless dashing)
        if not self.is_dashing:
            if self.direction.x != 0:
                self.rect.x += self.direction.x * current_speed

                for sprite in self.obstacle_sprites:
                    if sprite.rect.colliderect(self.rect):
                        if self.direction.x > 0: # Moving right
                            self.rect.right = sprite.rect.left
                        elif self.direction.x < 0: # Moving left
                            self.rect.left = sprite.rect.right
                        self.direction.x = 0

        # Apply gravity
        self.apply_gravity() # Modifies self.direction.y

        # Apply vertical movement
        # Apply ONLY if not dashing, as dash freezes vertical movement
        if not self.is_dashing:
            self.rect.y += self.direction.y

        # Check vertical collisions AFTER moving vertically
        self.vertical_collision() 

        # --- Animation State Logic (Post-Physics) ---
        if self.direction.y < 0:
            self.animation_state = 'jump'
        elif self.direction.y > self.gravity * 1.1: # Add small buffer to prevent flickering on landing
            self.animation_state = 'fall'
            # Reset frame index when starting to fall
            if self.animation_state != 'fall': self.animation_frame_index = 0 
        else: # On ground or very close to it
            if self.direction.x != 0:
                if self.animation_state != 'run': # Reset frame on starting run
                    self.animation_frame_index = 0
                self.animation_state = 'run'
            else:
                if self.animation_state != 'idle': # Reset frame on stopping
                    self.animation_frame_index = 0
                self.animation_state = 'idle'
        # print(f"State: {self.animation_state}, Frame: {self.animation_frame_index}, OnGround: {self.on_ground}, DirY: {self.direction.y:.2f}") # Debug print

    def update(self, dt):
        """Update player state including movement, collisions, and animation timer."""
        self.input() # Get player input first

        # Apply movement and collisions
        self.move(dt) # Pass dt to move for potential frame-rate independent movement

        # Update dash state (timers, cooldown)
        self.update_dash()

        # --- Update Shoot Cooldown ---
        if not self.can_shoot:
            self.shoot_cooldown_timer -= dt # Decrement by delta time
            if self.shoot_cooldown_timer <= 0:
                self.can_shoot = True

        # --- Update Animation Timer & Frame --- 
        self.animation_timer += dt
        time_per_frame = 1.0 / self.animation_speed

        if self.animation_timer >= time_per_frame:
            self.animation_timer -= time_per_frame # Reset timer preserving overshoot
            
            # Determine number of frames based on state
            if self.animation_state == 'run':
                num_frames = 2
            else: # idle, jump, fall
                num_frames = 1

            self.animation_frame_index = (self.animation_frame_index + 1) % num_frames

        # Check for interactions AFTER movement/collision resolution
        self.check_trap_collision() # Check for trap collisions
        self.check_bird_collision() # Check for bird collisions
        self.check_exit_collision() # Check for exit collisions
        self.check_hidden_door_collision() # Check for hidden door collisions

    def draw(self, screen, draw_topleft):
        # Draw stick figure directly onto the screen at the calculated offset position
        draw_cx = draw_topleft[0] + self.rect.width // 2
        draw_cy = draw_topleft[1] + self.rect.height // 2

        # --- Base Body Calculations --- 
        head_radius = self.head_radius
        body_height = self.body_height
        arm_length = self.arm_length
        leg_length = self.leg_length
        limb_thickness = self.limb_thickness

        # Calculate draw positions relative to hitbox center (draw_cx, draw_cy)
        # Head center Y needs to account for hitbox top and head radius
        head_center_y = draw_topleft[1] + head_radius
        # Body start/end relative to hitbox top
        body_start_y = draw_topleft[1] + self.shoulder_y_offset
        body_end_y = draw_topleft[1] + self.hip_y_offset
        shoulder_y = body_start_y # Arms start at body top
        hip_y = body_end_y # Legs start at body bottom

        # --- Draw Head and Body --- 
        # Draw head centered horizontally (draw_cx), vertically based on head_center_y
        pygame.draw.circle(screen, BLACK, (draw_cx, int(head_center_y)), head_radius)
        # Draw body line from shoulder height to hip height at horizontal center
        pygame.draw.line(screen, BLACK, (draw_cx, int(shoulder_y)), (draw_cx, int(hip_y)), limb_thickness)

        # --- Animated Limbs --- 
        state = self.animation_state
        frame = self.animation_frame_index
        facing_mult = 1 if self.facing_right else -1

        # Define limb positions based on state and frame
        left_arm_end = (0, 0)
        right_arm_end = (0, 0)
        left_leg_end = (0, 0)
        right_leg_end = (0, 0)

        if state == 'idle':
            left_arm_end = (draw_cx - arm_length * 0.3, shoulder_y + arm_length * 0.9)
            right_arm_end = (draw_cx + arm_length * 0.3, shoulder_y + arm_length * 0.9)
            left_leg_end = (draw_cx - leg_length * 0.2, hip_y + leg_length)
            right_leg_end = (draw_cx + leg_length * 0.2, hip_y + leg_length)
        elif state == 'run':
            swing = arm_length * 0.6 # How far limbs swing forward/back
            leg_lift = leg_length * 0.2 # How much legs bend
            if frame == 0:
                 # Left arm forward, right leg forward
                left_arm_end = (draw_cx + swing * facing_mult, shoulder_y + arm_length * 0.2)
                right_arm_end = (draw_cx - swing * 0.5 * facing_mult, shoulder_y + arm_length * 0.8)
                left_leg_end = (draw_cx - leg_length * 0.3 * facing_mult, hip_y + leg_length - leg_lift) # Back leg
                right_leg_end = (draw_cx + leg_length * 0.5 * facing_mult, hip_y + leg_length) # Forward leg
            else: # frame == 1
                 # Right arm forward, left leg forward
                left_arm_end = (draw_cx - swing * 0.5 * facing_mult, shoulder_y + arm_length * 0.8)
                right_arm_end = (draw_cx + swing * facing_mult, shoulder_y + arm_length * 0.2)
                left_leg_end = (draw_cx + leg_length * 0.5 * facing_mult, hip_y + leg_length) # Forward leg
                right_leg_end = (draw_cx - leg_length * 0.3 * facing_mult, hip_y + leg_length - leg_lift) # Back leg
        elif state == 'jump' or state == 'fall':
            # Arms up, legs dangling/tucked
            left_arm_end = (draw_cx - arm_length * 0.5, shoulder_y - arm_length * 0.5)
            right_arm_end = (draw_cx + arm_length * 0.5, shoulder_y - arm_length * 0.5)
            left_leg_end = (draw_cx - leg_length * 0.3, hip_y + leg_length * 0.7)
            right_leg_end = (draw_cx + leg_length * 0.3, hip_y + leg_length * 0.8)

        # Draw Arms
        pygame.draw.line(screen, BLACK, (draw_cx, int(shoulder_y)), left_arm_end, limb_thickness)
        pygame.draw.line(screen, BLACK, (draw_cx, int(shoulder_y)), right_arm_end, limb_thickness)

        # Draw Legs
        pygame.draw.line(screen, BLACK, (draw_cx, int(hip_y)), left_leg_end, limb_thickness)
        pygame.draw.line(screen, BLACK, (draw_cx, int(hip_y)), right_leg_end, limb_thickness)
