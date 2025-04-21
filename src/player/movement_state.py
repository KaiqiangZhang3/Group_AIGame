from src.settings import *

class MovementState:
    """Class to manage the movement state of a character."""
    def __init__(self):
        self.direction = 1 # 1 for right, -1 for left

        self.air_frames = 0

        self.can_jump = True
        self.can_dash = True

        self.dash_timer = 0
        self.dash_cooldown_timer = 0

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
        self.apply_gravity()
        self.update_dash()

    def jump(self):
        """Trigger a jump if not already jumping or falling."""
        if (self.on_ground or self.air_frames < 6) and self.can_jump:
            self.on_ground = False
            self.is_idle = False
            self.velocity[1] = self.jump_force

    def dash(self):
        """Trigger a dash (not implemented)."""
        if self.can_dash:
            self.is_dashing = True
            self.can_dash = False
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
            self.velocity[0] = self.dash_speed * self.direction
            self.velocity[1] = 0  # Reset vertical speed during dash

    def update_dash(self):
        """Update the dash state."""
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.velocity[1] = 0
            if self.dash_timer <= 0:
                self.is_dashing = False

        if not self.can_dash:
            self.dash_cooldown_timer -= 1
            if self.dash_cooldown_timer <= 0:
                self.can_dash = True

    def move_left(self):
        """Move the character to the left."""
        self.is_running = True
        self.is_idle = False
        self.direction = -1  # Set direction to left
        if self.velocity[0] > 0:
            self.velocity[0] = 0  # Reset horizontal speed before moving
        self.velocity[0] -= self.run_speed / 6
        self.velocity[0] = max(-self.run_speed, self.velocity[0])  # Limit left speed

    def move_right(self):
        """Move the character to the right."""
        self.is_running = True
        self.is_idle = False
        self.direction = 1
        if self.velocity[0] < 0:  # If moving left, stop moving left
            self.velocity[0] = 0  # Reset horizontal speed before moving
        self.velocity[0] += self.run_speed / 6
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

    def deaccelerate(self):
        """Gradually reduce horizontal speed."""
        if self.is_running:
            if self.velocity[0] > 0:
                self.velocity[0] -= self.run_speed / 3
                if self.velocity[0] < 0:
                    self.velocity[0] = 0
            elif self.velocity[0] < 0:
                self.velocity[0] += self.run_speed / 3
                if self.velocity[0] > 0:
                    self.velocity[0] = 0

    def reset(self):
        """Reset the movement state."""
        self.is_falling = False
        self.is_running = False
        self.is_idle = True
        self.velocity = [0, 0] 