from src.settings import *

class MovementState:
    """Class to manage the movement state of a character."""
    def __init__(self):
        self.direction = 1 # 1 for right, -1 for left

        self.air_frames = 0

        self.can_jump = True
        self.can_dash = True
        self.can_double_jump = True

        self.dash_timer = 0
        self.dash_frame = 0
        self.climbing_jump_frame = 0

        self.is_climbing = False
        self.is_climbing_jump = False
        self.is_super_jumping = False
        self.is_dashing = False
        self.on_ground = True
        self.is_running = False
        self.is_idle = True

        self.velocity = [0, 0]  # [x_velocity, y_velocity]
        self.dash_speed = PLAYER_DASH_SPEED
        self.run_speed = PLAYER_SPEED
        self.jump_force = PLAYER_JUMP_STRENGTH
        self.gravity = PLAYER_GRAVITY
    
    def apply_gravity(self):
        """Apply gravity to the player."""
        # Gravity doesn't apply during dash
        if not self.is_dashing:
            self.velocity[1] += self.gravity
            # Basic terminal velocity
            if self.velocity[1] > -PLAYER_JUMP_STRENGTH:
                self.velocity[1] = -PLAYER_JUMP_STRENGTH

    def update(self):
        """Update the movement state based on velocity and gravity."""
        self.update_climbing_jump()
        if self.is_climbing_jump: return
        self.apply_gravity()
        self.update_dash()
        self.update_climbing()


    def jump(self):
        """Trigger a jump if not already jumping or falling."""
        if self.is_dashing and self.dash_frame <= PLAYER_DASH_PREPARE_FRAMES and self.can_jump:
            self.is_dashing = False
            self.is_super_jumping = True
            self.can_jump = False
            self.velocity[0] = self.dash_speed * self.direction * PLAYER_SUPER_JUMP_STRENGTH_RATE
            self.velocity[1] = self.jump_force
        elif self.is_climbing:
            self.is_climbing_jump = True
            self.is_idle = False
            self.is_climbing = False
            self.climbing_jump_frame = 0
        elif self.can_double_jump and self.air_frames > JUMP_TOLERANCE_FRAME:
            self.can_double_jump = False
            self.is_idle = False
            self.velocity[1] = self.jump_force * PLAYER_DOUBLE_JUMP_STRENGTH_RATE
        elif (self.on_ground or self.air_frames < JUMP_TOLERANCE_FRAME) and self.can_jump and not self.is_dashing:
            self.on_ground = False
            self.is_idle = False
            self.can_jump = False
            self.velocity[1] = self.jump_force

    def dash(self):
        """Trigger a dash (not implemented)."""
        if self.can_dash:
            self.is_dashing = True
            self.can_dash = False
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_frame = 0
            if self.is_climbing: self.direction *= -1

    def update_dash(self):
        """Update the dash state."""
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.dash_frame += 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.is_super_jumping = False
            else:
                if self.dash_frame > PLAYER_DASH_PREPARE_FRAMES:
                    self.velocity[0] = self.dash_speed * self.direction
                elif self.dash_frame <= PLAYER_DASH_PREPARE_FRAMES and not self.is_super_jumping:
                    self.velocity[0] = 0

    def move_left(self):
        """Move the character to the left."""
        self.is_running = True
        self.is_idle = False
        self.direction = -1  # Set direction to left
        if self.velocity[0] > 0:
            self.velocity[0] = 0  # Reset horizontal speed before moving
        self.velocity[0] -= self.run_speed / ACELERATION_FRAME
        self.velocity[0] = max(-self.run_speed, self.velocity[0])  # Limit left speed

    def move_right(self):
        """Move the character to the right."""
        self.is_running = True
        self.is_idle = False
        self.direction = 1
        if self.velocity[0] < 0:  # If moving left, stop moving left
            self.velocity[0] = 0  # Reset horizontal speed before moving
        self.velocity[0] += self.run_speed / ACELERATION_FRAME
        self.velocity[0] = min(self.run_speed, self.velocity[0]) # Limit right speed

    def stop_horizontal(self):
        """Stop horizontal movement."""
        self.is_running = False
        self.is_dashing = False
        self.velocity[0] = 0
    
    def reset_actions(self):
        """Reset the movement state actions."""
        self.can_dash = True
        self.can_jump = True
        self.can_double_jump = True

    def decelerate(self):
        """Gradually reduce horizontal speed."""
        if self.is_running:
            if self.velocity[0] > 0:
                self.velocity[0] -= self.run_speed / DECELERATION_FRAME
                if self.velocity[0] < 0:
                    self.velocity[0] = 0
            elif self.velocity[0] < 0:
                self.velocity[0] += self.run_speed / DECELERATION_FRAME
                if self.velocity[0] > 0:
                    self.velocity[0] = 0

    def reset(self):
        """Reset the movement state."""
        self.is_falling = False
        self.is_running = False
        self.is_idle = True
        self.velocity = [0, 0]
    
    def start_climbing(self):
        """Start climbing."""
        self.is_climbing = True
        self.air_frames = CLIMBING_JUMP_FRAME
        self.reset_actions()
    
    def update_climbing(self):
        """Update climbing state."""
        if self.is_climbing:
            self.velocity[1] = 1.5

    def update_climbing_jump(self):
        """Update climbing jump state."""
        if self.is_climbing_jump:
            self.climbing_jump_frame += 1
            if self.climbing_jump_frame > CLIMBING_JUMP_FRAME:
                self.is_climbing_jump = False
                self.direction *= -1
                self.is_running = True
                self.velocity[1] *= 0.6
            else:
                self.velocity[1] = PLAYER_JUMP_STRENGTH * PLAYER_DOUBLE_JUMP_STRENGTH_RATE
                self.velocity[0] = PLAYER_SPEED * -self.direction
